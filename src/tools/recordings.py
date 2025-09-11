"""Tools for managing Kasm session recordings."""

import logging
from typing import Any, Dict, List, Optional

from mcp.types import Tool

from .base import BaseKasmTool

logger = logging.getLogger(__name__)


class RecordingsTool(BaseKasmTool):
    """Tool for managing Kasm session recordings."""
    
    @property
    def tools(self) -> List[Tool]:
        """Get the list of tools provided by this module."""
        return [
            Tool(
                name="get_session_recordings",
                description="Get recordings for a specific Kasm session with optional download links",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kasm_id": {
                            "type": "string",
                            "description": "ID of the session to get recordings for"
                        },
                        "include_download_links": {
                            "type": "boolean",
                            "description": "Include pre-authorized download links (default: false)",
                            "default": False
                        }
                    },
                    "required": ["kasm_id"]
                }
            ),
            Tool(
                name="get_sessions_recordings",
                description="Get recordings for multiple Kasm sessions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "kasm_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of session IDs to get recordings for"
                        },
                        "include_download_links": {
                            "type": "boolean",
                            "description": "Include pre-authorized download links (default: false)",
                            "default": False
                        }
                    },
                    "required": ["kasm_ids"]
                }
            )
        ]
    
    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Handle tool calls for recordings management."""
        try:
            if tool_name == "get_session_recordings":
                return await self.get_session_recordings(**arguments)
            elif tool_name == "get_sessions_recordings":
                return await self.get_sessions_recordings(**arguments)
            else:
                return self._error_response(f"Unknown tool: {tool_name}")
        except Exception as e:
            logger.error(f"Error in {tool_name}: {e}")
            return self._error_response(str(e))
    
    async def get_session_recordings(
        self,
        kasm_id: str,
        include_download_links: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recordings for a specific Kasm session.
        
        Args:
            kasm_id: ID of the session to get recordings for
            include_download_links: Whether to include pre-authorized download links
            
        Returns:
            List containing the response with session recordings
        """
        try:
            result = await self.api_client.get_session_recordings(
                target_kasm_id=kasm_id,
                preauth_download_link=include_download_links
            )
            
            # Format the response
            recordings = result.get("session_recordings", [])
            
            if not recordings:
                return [{
                    "type": "text",
                    "text": f"No recordings found for session {kasm_id}"
                }]
            
            response_text = f"Found {len(recordings)} recording(s) for session {kasm_id}:\n\n"
            
            for idx, recording in enumerate(recordings, 1):
                response_text += f"Recording {idx}:\n"
                response_text += f"  - ID: {recording.get('recording_id', 'N/A')}\n"
                
                # Handle metadata
                metadata = recording.get('session_recording_metadata', {})
                if metadata:
                    response_text += f"  - Duration: {metadata.get('duration', 0)} seconds\n"
                    response_text += f"  - Timestamp: {metadata.get('timestamp', 'N/A')}\n"
                
                response_text += f"  - URL: {recording.get('session_recording_url', 'N/A')}\n"
                
                if include_download_links and recording.get('session_recording_download_url'):
                    response_text += f"  - Download URL: {recording.get('session_recording_download_url')}\n"
                
                response_text += "\n"
            
            return [{
                "type": "text",
                "text": response_text
            }]
            
        except Exception as e:
            return self._error_response(f"Failed to get session recordings: {str(e)}")
    
    async def get_sessions_recordings(
        self,
        kasm_ids: List[str],
        include_download_links: bool = False
    ) -> List[Dict[str, Any]]:
        """Get recordings for multiple Kasm sessions.
        
        Args:
            kasm_ids: List of session IDs to get recordings for
            include_download_links: Whether to include pre-authorized download links
            
        Returns:
            List containing the response with session recordings organized by session
        """
        try:
            result = await self.api_client.get_sessions_recordings(
                target_kasm_ids=kasm_ids,
                preauth_download_link=include_download_links
            )
            
            kasm_sessions = result.get("kasm_sessions", {})
            
            if not kasm_sessions:
                return [{
                    "type": "text",
                    "text": f"No recordings found for the specified sessions"
                }]
            
            response_text = f"Session recordings for {len(kasm_sessions)} session(s):\n\n"
            
            for kasm_id, session_data in kasm_sessions.items():
                recordings = session_data.get("session_recordings", [])
                response_text += f"Session {kasm_id}: {len(recordings)} recording(s)\n"
                
                for idx, recording in enumerate(recordings, 1):
                    response_text += f"  Recording {idx}:\n"
                    response_text += f"    - ID: {recording.get('recording_id', 'N/A')}\n"
                    
                    # Handle metadata
                    metadata = recording.get('session_recording_metadata', {})
                    if metadata:
                        response_text += f"    - Duration: {metadata.get('duration', 0)} seconds\n"
                        response_text += f"    - Timestamp: {metadata.get('timestamp', 'N/A')}\n"
                    
                    if include_download_links and recording.get('session_recording_download_url'):
                        response_text += f"    - Download URL: {recording.get('session_recording_download_url')}\n"
                
                response_text += "\n"
            
            return [{
                "type": "text",
                "text": response_text
            }]
            
        except Exception as e:
            return self._error_response(f"Failed to get sessions recordings: {str(e)}")
