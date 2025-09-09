"""Kasm Workspaces API client implementation."""

import hashlib
import json
import logging
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class KasmAPIError(Exception):
    """Base exception for Kasm API errors."""
    pass


class KasmAPIClient:
    """Client for interacting with Kasm Workspaces Developer API."""
    
    def __init__(self, api_url: str, api_key: str, api_secret: str):
        """
        Initialize Kasm API client.
        
        Args:
            api_url: Base URL for Kasm API
            api_key: API key for authentication
            api_secret: API secret for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        
    def _generate_auth_hash(self, endpoint: str, body: Dict[str, Any]) -> str:
        """
        Generate authentication hash for Kasm API.
        
        Args:
            endpoint: API endpoint path
            body: Request body
            
        Returns:
            Authentication hash
        """
        # Kasm uses SHA256 hash of endpoint + api_key + api_secret + request_body
        auth_string = f"{endpoint}{self.api_key}{self.api_secret}{json.dumps(body, separators=(',', ':'))}"
        return hashlib.sha256(auth_string.encode()).hexdigest()
    
    def _make_request(self, endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make authenticated request to Kasm API.
        
        Args:
            endpoint: API endpoint path
            body: Request body
            
        Returns:
            API response data
            
        Raises:
            KasmAPIError: If request fails
        """
        url = urljoin(self.api_url, endpoint)
        
        # Add authentication to body
        body['api_key'] = self.api_key
        body['api_key_auth'] = self._generate_auth_hash(endpoint, body)
        
        try:
            response = self.session.post(url, json=body)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API-level errors
            if isinstance(data, dict) and data.get('error'):
                raise KasmAPIError(f"API error: {data.get('error_message', 'Unknown error')}")
                
            return data
            
        except RequestException as e:
            logger.error(f"Request failed: {e}")
            raise KasmAPIError(f"Request failed: {str(e)}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise KasmAPIError(f"Invalid JSON response: {str(e)}") from e
    
    # Session Management Methods
    
    def request_kasm(self, image_name: str, user_id: str, group_id: str) -> Dict[str, Any]:
        """
        Request a new Kasm session.
        
        Args:
            image_name: Name of the workspace image
            user_id: User ID requesting the session
            group_id: Group ID for the session
            
        Returns:
            Session creation response including kasm_id
        """
        body = {
            "image_name": image_name,
            "user_id": user_id,
            "group_id": group_id
        }
        
        return self._make_request("/api/public/request_kasm", body)
    
    def destroy_kasm(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """
        Destroy a Kasm session.
        
        Args:
            kasm_id: ID of the session to destroy
            user_id: User ID owning the session
            
        Returns:
            Destruction confirmation
        """
        body = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return self._make_request("/api/public/destroy_kasm", body)
    
    def get_kasm_status(self, kasm_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get status of a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            
        Returns:
            Session status information
        """
        body = {
            "kasm_id": kasm_id,
            "user_id": user_id
        }
        
        return self._make_request("/api/public/get_kasm_status", body)
    
    # Command Execution
    
    def exec_command(self, kasm_id: str, user_id: str, command: str, 
                    working_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a command in a Kasm session.
        
        Args:
            kasm_id: ID of the session
            user_id: User ID owning the session
            command: Command to execute
            working_dir: Optional working directory
            
        Returns:
            Command execution results
        """
        body = {
            "kasm_id": kasm_id,
            "user_id": user_id,
            "exec": command
        }
        
        if working_dir:
            body["working_dir"] = working_dir
            
        return self._make_request("/api/public/exec_command_kasm", body)
    
    # User Management
    
    def get_users(self) -> Dict[str, Any]:
        """
        Get list of users.
        
        Returns:
            List of users
        """
        return self._make_request("/api/public/get_users", {})
    
    def create_user(self, username: str, password: str, 
                   first_name: str = "", last_name: str = "") -> Dict[str, Any]:
        """
        Create a new user.
        
        Args:
            username: Username for the new user
            password: Password for the new user
            first_name: User's first name
            last_name: User's last name
            
        Returns:
            User creation response
        """
        body = {
            "username": username,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        return self._make_request("/api/public/create_user", body)
    
    # Workspace Management
    
    def get_workspaces(self) -> Dict[str, Any]:
        """
        Get list of available workspaces.
        
        Returns:
            List of workspace images
        """
        return self._make_request("/api/public/get_workspaces", {})
