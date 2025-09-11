"""Kasm API client for interacting with Kasm Workspaces."""

import json
import logging
import os
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class KasmAPIClient:
    """Client for interacting with Kasm Workspaces API."""
    
    def __init__(self, api_url: str, api_key: str, api_secret: str):
        """Initialize the Kasm API client.
        
        Args:
            api_url: Base URL for the Kasm API
            api_key: API key for authentication
            api_secret: API secret for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.session: Optional[ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the Kasm API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request data
            
        Returns:
            Response data as dictionary
        """
        if not self.session:
            self.session = ClientSession()
            
        url = urljoin(self.api_url, endpoint)
        
        # Prepare authentication
        auth_data = {
            "api_key": self.api_key,
            "api_key_secret": self.api_secret
        }
        
        if data:
            auth_data.update(data)
            
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            async with self.session.request(
                method,
                url,
                json=auth_data,
                headers=headers
            ) as response:
                # Check content type
                content_type = response.headers.get('content-type', '')
                
                # Handle HTML responses (usually error pages)
                if 'text/html' in content_type:
                    html_content = await response.text()
                    error_msg = f"Received HTML response instead of JSON (status {response.status})"
                    
                    # Try to extract meaningful error from HTML
                    if 'error' in html_content.lower():
                        # Simple extraction of error messages from HTML
                        import re
                        error_match = re.search(r'<title>(.*?)</title>', html_content, re.IGNORECASE)
                        if error_match:
                            error_msg += f": {error_match.group(1)}"
                    
                    logger.error(f"HTML response from {url}: {error_msg}")
                    logger.debug(f"Full HTML response: {html_content[:500]}...")
                    
                    raise Exception(error_msg)
                
                # Parse JSON response
                try:
                    response_data = await response.json()
                except json.JSONDecodeError as e:
                    text_content = await response.text()
                    logger.error(f"Failed to decode JSON from {url}: {e}")
                    logger.debug(f"Response content: {text_content[:500]}...")
                    raise Exception(f"Invalid JSON response from API: {e}")
                
                if response.status >= 400:
                    error_msg = response_data.get("error", f"API error with status {response.status}")
                    raise Exception(f"Kasm API error: {error_msg}")
                    
                return response_data
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error calling Kasm API: {e}")
            raise
        except Exception as e:
            if not str(e).startswith(("Kasm API error", "Invalid JSON", "Received HTML")):
                logger.error(f"Unexpected error calling Kasm API: {e}")
            raise
            
    # Session Management Methods
    
    async def request_kasm(
        self,
        image_name: str,
        user_id: str,
        group_id: str
    ) -> Dict[str, Any]:
        """Request a new Kasm session.
        
        Args:
            image_name: Name or ID of the workspace image
            user_id: User ID requesting the session
            group_id: Group ID for the session
            
        Returns:
            Session creation response
        """
        import re
        
        # Detect if the input is a UUID (image_id) or a Docker image name
        uuid_pattern = re.compile(r'^[a-f0-9]{32}$|^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}$', re.IGNORECASE)
        
        # Ensure UUIDs maintain their format (with hyphens for user/group)
        # but image_id should be without hyphens
        data = {
            "user_id": user_id,  # Keep original format (with hyphens)
            "group_id": group_id  # Keep original format (with hyphens)
        }
        
        # If it looks like a UUID, try image_id first
        if uuid_pattern.match(image_name):
            # Remove hyphens from image_id only
            data["image_id"] = image_name.replace('-', '')
            
            try:
                # Try with image_id first
                logger.debug(f"Attempting session creation with image_id: {data['image_id']}")
                return await self._make_request("POST", "/api/public/request_kasm", data)
            except Exception as e:
                # If that fails, try with image_name as fallback
                logger.warning(f"Failed with image_id, trying image_name: {e}")
                del data["image_id"]
                data["image_name"] = image_name
                return await self._make_request("POST", "/api/public/request_kasm", data)
        else:
            # It's a Docker image name like "kasmweb/chrome:1.8.0"
            data["image_name"] = image_name
            
            try:
                # Try with image_name
                logger.debug(f"Attempting session creation with image_name: {data['image_name']}")
                return await self._make_request("POST", "/api/public/request_kasm", data)
            except Exception as e:
                # If the image name looks like it might be an ID without hyphens, try that
                if re.match(r'^[a-f0-9]{32}$', image_name, re.IGNORECASE):
                    logger.warning(f"Failed with image_name, trying as image_id: {e}")
                    del data["image_name"]
                    data["image_id"] = image_name
                    return await self._make_request("POST", "/api/public/request_kasm", data)
                else:
                    raise
        
    async def destroy_kasm(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """Destroy a Kasm session.
        
        Args:
            kasm_id: ID of the session to destroy
            user_id: User ID owning the session
            
        Returns:
            Destruction response
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return await self._make_request("POST", "/api/public/destroy_kasm", data)
        
    async def get_kasm_status(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """Get the status of a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            
        Returns:
            Session status information
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return await self._make_request("POST", "/api/public/get_kasm_status", data)
    
    async def get_user_kasms(self, user_id: str) -> Dict[str, Any]:
        """Get list of active sessions for a user.
        
        Args:
            user_id: User ID to get sessions for
            
        Returns:
            List of user's active sessions
        """
        data = {
            "user_id": user_id
        }
        
        return await self._make_request("POST", "/api/public/get_user_kasms", data)
    
    async def get_kasms(self) -> Dict[str, Any]:
        """Get list of all active sessions (admin).
        
        Returns:
            List of all active sessions
        """
        return await self._make_request("POST", "/api/public/get_kasms")
    
    async def pause_kasm(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """Pause a Kasm session.
        
        Args:
            kasm_id: ID of the session to pause
            user_id: User ID owning the session
            
        Returns:
            Pause response
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return await self._make_request("POST", "/api/public/pause_kasm", data)
    
    async def resume_kasm(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """Resume a paused Kasm session.
        
        Args:
            kasm_id: ID of the session to resume
            user_id: User ID owning the session
            
        Returns:
            Resume response
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return await self._make_request("POST", "/api/public/resume_kasm", data)
    
    async def get_kasm_screenshot(
        self,
        kasm_id: str,
        user_id: str,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get a screenshot of a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            width: Width of the screenshot (default: 300)
            height: Height of the screenshot (auto-adjusted for aspect ratio)
            
        Returns:
            Screenshot data (JPEG image or base64 encoded)
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        if width:
            data["width"] = width
        if height:
            data["height"] = height
        
        return await self._make_request("POST", "/api/public/get_kasm_screenshot", data)
        
    # Command Execution
    
    async def exec_command(
        self,
        kasm_id: str,
        user_id: str,
        command: str,
        working_dir: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        privileged: bool = False,
        user: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a command in a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            command: Command to execute
            working_dir: Working directory for command execution
            environment: Environment variables for the command
            privileged: Run command as privileged
            user: User to run command as (e.g., 'root')
            
        Returns:
            Command execution result
        """
        # Build exec_config according to Kasm API spec
        exec_config = {
            "cmd": command
        }
        
        if working_dir:
            exec_config["workdir"] = working_dir
        if environment:
            exec_config["environment"] = environment
        if privileged:
            exec_config["privileged"] = privileged
        if user:
            exec_config["user"] = user
            
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id,
            "exec_config": exec_config
        }
        
        return await self._make_request("POST", "/api/public/exec_command_kasm", data)
        
    # Admin Methods
    
    async def get_images(self) -> Dict[str, Any]:
        """Get list of available workspace images.
        
        Returns:
            List of workspace image configurations
        """
        return await self._make_request("POST", "/api/public/get_images")
        
    async def get_users(self) -> Dict[str, Any]:
        """Get list of users.
        
        Returns:
            List of users
        """
        return await self._make_request("POST", "/api/public/get_users")
        
    async def create_user(
        self,
        username: str,
        password: str,
        first_name: str = "",
        last_name: str = "",
        organization: str = "",
        phone: str = "",
        locked: bool = False,
        disabled: bool = False
    ) -> Dict[str, Any]:
        """Create a new user.
        
        Args:
            username: Username for the new user
            password: Password for the new user
            first_name: User's first name
            last_name: User's last name
            organization: User's organization
            phone: User's phone number
            locked: Whether the account is locked
            disabled: Whether the account is disabled
            
        Returns:
            User creation response
        """
        data = {
            "target_user": {
                "username": username,
                "password": password,
                "first_name": first_name,
                "last_name": last_name,
                "organization": organization,
                "phone": phone,
                "locked": locked,
                "disabled": disabled
            }
        }
        
        return await self._make_request("POST", "/api/public/create_user", data)
    
    async def get_user(
        self,
        user_id: Optional[str] = None,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a specific user's details.
        
        Args:
            user_id: User ID to retrieve
            username: Username to retrieve (alternative to user_id)
            
        Returns:
            User details
        """
        if not user_id and not username:
            raise ValueError("Either user_id or username must be provided")
        
        data = {
            "target_user": {}
        }
        
        if user_id:
            data["target_user"]["user_id"] = user_id
        if username:
            data["target_user"]["username"] = username
            
        return await self._make_request("POST", "/api/public/get_user", data)
    
    async def update_user(
        self,
        user_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        organization: Optional[str] = None,
        phone: Optional[str] = None,
        locked: Optional[bool] = None,
        disabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update an existing user.
        
        Args:
            user_id: User ID to update
            username: New username
            password: New password
            first_name: New first name
            last_name: New last name
            organization: New organization
            phone: New phone number
            locked: New locked status
            disabled: New disabled status
            
        Returns:
            Updated user details
        """
        data = {
            "target_user": {
                "user_id": user_id
            }
        }
        
        # Only include fields that are being updated
        if username is not None:
            data["target_user"]["username"] = username
        if password is not None:
            data["target_user"]["password"] = password
        if first_name is not None:
            data["target_user"]["first_name"] = first_name
        if last_name is not None:
            data["target_user"]["last_name"] = last_name
        if organization is not None:
            data["target_user"]["organization"] = organization
        if phone is not None:
            data["target_user"]["phone"] = phone
        if locked is not None:
            data["target_user"]["locked"] = locked
        if disabled is not None:
            data["target_user"]["disabled"] = disabled
            
        return await self._make_request("POST", "/api/public/update_user", data)
    
    async def delete_user(
        self,
        user_id: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """Delete an existing user.
        
        Args:
            user_id: User ID to delete
            force: Force deletion even if user has active sessions
            
        Returns:
            Deletion response
        """
        data = {
            "target_user": {
                "user_id": user_id
            },
            "force": force
        }
        
        return await self._make_request("POST", "/api/public/delete_user", data)
    
    async def logout_user(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Logout all sessions for a user.
        
        Args:
            user_id: User ID to logout
            
        Returns:
            Logout response
        """
        data = {
            "target_user": {
                "user_id": user_id
            }
        }
        
        return await self._make_request("POST", "/api/public/logout_user", data)
    
    async def get_user_attributes(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get user attributes (preferences).
        
        Args:
            user_id: User ID to get attributes for
            
        Returns:
            User attributes
        """
        data = {
            "target_user": {
                "user_id": user_id
            }
        }
        
        return await self._make_request("POST", "/api/public/get_attributes", data)
    
    async def update_user_attributes(
        self,
        user_id: str,
        auto_login_kasm: Optional[bool] = None,
        default_image: Optional[str] = None,
        show_tips: Optional[bool] = None,
        toggle_control_panel: Optional[bool] = None,
        ssh_public_key: Optional[str] = None,
        chat_sfx: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update user attributes (preferences).
        
        Args:
            user_id: User ID to update attributes for
            auto_login_kasm: Auto-login to Kasm sessions
            default_image: Default workspace image ID
            show_tips: Show tips in UI
            toggle_control_panel: Toggle control panel visibility
            ssh_public_key: SSH public key for user
            chat_sfx: Enable chat sound effects
            
        Returns:
            Update response
        """
        data = {
            "target_user_attributes": {
                "user_id": user_id
            }
        }
        
        # Only include attributes that are being updated
        if auto_login_kasm is not None:
            data["target_user_attributes"]["auto_login_kasm"] = auto_login_kasm
        if default_image is not None:
            data["target_user_attributes"]["default_image"] = default_image
        if show_tips is not None:
            data["target_user_attributes"]["show_tips"] = show_tips
        if toggle_control_panel is not None:
            data["target_user_attributes"]["toggle_control_panel"] = toggle_control_panel
        if ssh_public_key is not None:
            data["target_user_attributes"]["ssh_public_key"] = ssh_public_key
        if chat_sfx is not None:
            data["target_user_attributes"]["chat_sfx"] = chat_sfx
            
        return await self._make_request("POST", "/api/public/update_user_attributes", data)
    
    # Performance and Monitoring Methods
    
    async def get_kasm_frame_stats(
        self,
        kasm_id: str,
        user_id: str,
        client: str = "auto"
    ) -> Dict[str, Any]:
        """Get frame statistics for a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            client: Which client to retrieve stats for ('none', 'auto', 'all', or websocket_id)
            
        Returns:
            Frame statistics including timing and performance metrics
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id,
            "client": client
        }
        
        return await self._make_request("POST", "/api/public/get_kasm_frame_stats", data)
    
    async def get_kasm_bottleneck_stats(
        self,
        kasm_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Get CPU and network bottleneck statistics for a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            
        Returns:
            Bottleneck statistics for CPU and network constraints
        """
        data = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return await self._make_request("POST", "/api/public/get_kasm_bottleneck_stats", data)
    
    async def get_session_recordings(
        self,
        target_kasm_id: str,
        preauth_download_link: bool = False
    ) -> Dict[str, Any]:
        """Get session recordings for a specific Kasm session.
        
        Args:
            target_kasm_id: ID of the session to get recordings for
            preauth_download_link: Whether to include pre-authorized download links
            
        Returns:
            List of session recordings with metadata and optional download links
        """
        data = {
            "target_kasm_id": target_kasm_id,
            "preauth_download_link": preauth_download_link
        }
        
        return await self._make_request("POST", "/api/public/get_session_recordings", data)
        
    # Synchronous wrapper methods for backward compatibility
    
    def request_kasm_sync(self, image_name: str, user_id: str, group_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for request_kasm."""
        import asyncio
        return asyncio.run(self.request_kasm(image_name, user_id, group_id))
        
    def destroy_kasm_sync(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for destroy_kasm."""
        import asyncio
        return asyncio.run(self.destroy_kasm(kasm_id, user_id))
        
    def get_kasm_status_sync(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """Synchronous wrapper for get_kasm_status."""
        import asyncio
        return asyncio.run(self.get_kasm_status(kasm_id, user_id))
        
    def exec_command_sync(
        self,
        kasm_id: str,
        user_id: str,
        command: str,
        working_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Synchronous wrapper for exec_command."""
        import asyncio
        return asyncio.run(self.exec_command(kasm_id, user_id, command, working_dir))
        
    def get_images_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for get_images."""
        import asyncio
        return asyncio.run(self.get_images())
        
    def get_users_sync(self) -> Dict[str, Any]:
        """Synchronous wrapper for get_users."""
        import asyncio
        return asyncio.run(self.get_users())
        
    def create_user_sync(
        self,
        username: str,
        password: str,
        first_name: str = "",
        last_name: str = ""
    ) -> Dict[str, Any]:
        """Synchronous wrapper for create_user."""
        import asyncio
        return asyncio.run(self.create_user(username, password, first_name, last_name))
        
    # Note: The async methods are the primary interface.
    # Sync wrappers are provided for backward compatibility but should not override async methods.
    # Use request_kasm_sync, destroy_kasm_sync, etc. explicitly if synchronous execution is needed.
