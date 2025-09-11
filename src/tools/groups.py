"""Tools for managing Kasm user groups."""

import logging
from typing import Any, Dict, List

from mcp.types import Tool

from .base import BaseKasmTool

logger = logging.getLogger(__name__)


class GroupsTool(BaseKasmTool):
    """Tool for managing Kasm user groups."""
    
    @property
    def tools(self) -> List[Tool]:
        """Get the list of tools provided by this module."""
        return [
            Tool(
                name="add_user_to_group",
                description="Add a user to an existing Kasm group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to add to the group"
                        },
                        "group_id": {
                            "type": "string",
                            "description": "Group ID to add the user to"
                        }
                    },
                    "required": ["user_id", "group_id"]
                }
            ),
            Tool(
                name="remove_user_from_group",
                description="Remove a user from an existing Kasm group",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to remove from the group"
                        },
                        "group_id": {
                            "type": "string",
                            "description": "Group ID to remove the user from"
                        }
                    },
                    "required": ["user_id", "group_id"]
                }
            ),
            Tool(
                name="get_login_link",
                description="Generate a passwordless login link for a user",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "user_id": {
                            "type": "string",
                            "description": "User ID to generate login link for"
                        }
                    },
                    "required": ["user_id"]
                }
            ),
            Tool(
                name="get_deployment_zones",
                description="Get list of Kasm deployment zones",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "brief": {
                            "type": "boolean",
                            "description": "Return limited information for each zone (default: false)",
                            "default": False
                        }
                    }
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle tool calls for group management."""
        try:
            if tool_name == "add_user_to_group":
                return await self.add_user_to_group(**arguments)
            elif tool_name == "remove_user_from_group":
                return await self.remove_user_from_group(**arguments)
            elif tool_name == "get_login_link":
                return await self.get_login_link(**arguments)
            elif tool_name == "get_deployment_zones":
                return await self.get_deployment_zones(**arguments)
            else:
                return self._error_response(f"Unknown tool: {tool_name}")
        except Exception as e:
            logger.error(f"Error in {tool_name}: {e}")
            return self._error_response(str(e))
    
    async def add_user_to_group(
        self,
        user_id: str,
        group_id: str
    ) -> List[Dict[str, Any]]:
        """Add a user to an existing group.
        
        Args:
            user_id: User ID to add to the group
            group_id: Group ID to add the user to
            
        Returns:
            List containing the response
        """
        try:
            await self.api_client.add_user_to_group(
                user_id=user_id,
                group_id=group_id
            )
            
            return [{
                "type": "text",
                "text": f"✅ Successfully added user {user_id} to group {group_id}"
            }]
            
        except Exception as e:
            return self._error_response(f"Failed to add user to group: {str(e)}")
    
    async def remove_user_from_group(
        self,
        user_id: str,
        group_id: str
    ) -> List[Dict[str, Any]]:
        """Remove a user from an existing group.
        
        Args:
            user_id: User ID to remove from the group
            group_id: Group ID to remove the user from
            
        Returns:
            List containing the response
        """
        try:
            await self.api_client.remove_user_from_group(
                user_id=user_id,
                group_id=group_id
            )
            
            return [{
                "type": "text",
                "text": f"✅ Successfully removed user {user_id} from group {group_id}"
            }]
            
        except Exception as e:
            return self._error_response(f"Failed to remove user from group: {str(e)}")
    
    async def get_login_link(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Generate a passwordless login link for a user.
        
        Args:
            user_id: User ID to generate login link for
            
        Returns:
            List containing the response with the login URL
        """
        try:
            result = await self.api_client.get_login_link(user_id=user_id)
            
            login_url = result.get("url", "")
            
            if not login_url:
                return self._error_response("No login URL returned from API")
            
            response_text = f"🔗 Login link generated for user {user_id}:\n\n"
            response_text += f"{login_url}\n\n"
            response_text += "⚠️  This link provides direct access to the user's account.\n"
            response_text += "Share it securely and only with the intended recipient."
            
            return [{
                "type": "text",
                "text": response_text
            }]
            
        except Exception as e:
            return self._error_response(f"Failed to generate login link: {str(e)}")
    
    async def get_deployment_zones(
        self,
        brief: bool = False
    ) -> List[Dict[str, Any]]:
        """Get list of Kasm deployment zones.
        
        Args:
            brief: Return limited information for each zone
            
        Returns:
            List containing the response with deployment zones
        """
        try:
            result = await self.api_client.get_zones(brief=brief)
            
            zones = result.get("zones", [])
            
            if not zones:
                return [{
                    "type": "text",
                    "text": "No deployment zones found"
                }]
            
            response_text = f"Found {len(zones)} deployment zone(s):\n\n"
            
            for zone in zones:
                response_text += f"Zone: {zone.get('zone_name', 'N/A')}\n"
                response_text += f"  - ID: {zone.get('zone_id', 'N/A')}\n"
                
                if not brief:
                    # Include detailed information when not in brief mode
                    response_text += f"  - Auto-scaling: {zone.get('auto_scaling_enabled', False)}\n"
                    
                    if zone.get('aws_enabled'):
                        response_text += f"  - AWS Region: {zone.get('aws_region', 'N/A')}\n"
                        response_text += f"  - AWS AMI ID: {zone.get('ec2_agent_ami_id', 'N/A')}\n"
                
                response_text += "\n"
            
            return [{
                "type": "text",
                "text": response_text
            }]
            
        except Exception as e:
            return self._error_response(f"Failed to get deployment zones: {str(e)}")
