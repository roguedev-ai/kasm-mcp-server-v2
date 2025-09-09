"""Basic tests for Kasm MCP Server components."""

import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.security import RootsValidator, SecurityError
from src.kasm_api import KasmAPIClient, KasmAPIError


class TestRootsValidator:
    """Test the Roots security validator."""
    
    def test_allowed_path(self):
        """Test that allowed paths pass validation."""
        validator = RootsValidator(["/home/kasm_user", "/workspace"])
        
        assert validator.is_path_allowed("/home/kasm_user/test.txt")
        assert validator.is_path_allowed("/workspace/project/file.py")
        
    def test_disallowed_path(self):
        """Test that disallowed paths fail validation."""
        validator = RootsValidator(["/home/kasm_user", "/workspace"])
        
        assert not validator.is_path_allowed("/etc/passwd")
        assert not validator.is_path_allowed("/root/.ssh/id_rsa")
        
    def test_validate_command_blocks_dangerous(self):
        """Test that dangerous commands are blocked."""
        validator = RootsValidator(["/home/kasm_user"])
        
        # Test blocked commands
        with pytest.raises(SecurityError):
            validator.validate_command("sudo rm -rf /")
            
        with pytest.raises(SecurityError):
            validator.validate_command("chmod 777 /etc/passwd")
            
    def test_validate_command_allows_safe(self):
        """Test that safe commands are allowed."""
        validator = RootsValidator(["/home/kasm_user"])
        
        # These should not raise
        validator.validate_command("ls -la /home/kasm_user")
        validator.validate_command("echo 'Hello World'")
        validator.validate_command("python3 /home/kasm_user/script.py")


class TestKasmAPIClient:
    """Test the Kasm API client."""
    
    def test_auth_hash_generation(self):
        """Test authentication hash generation."""
        client = KasmAPIClient(
            api_url="https://kasm.example.com",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        # Test hash generation
        endpoint = "/api/public/test"
        body = {"test": "data"}
        hash_result = client._generate_auth_hash(endpoint, body)
        
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA256 produces 64 character hex string
        
    @patch('requests.Session.post')
    def test_successful_api_call(self, mock_post):
        """Test successful API call."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        mock_post.return_value = mock_response
        
        client = KasmAPIClient(
            api_url="https://kasm.example.com",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        result = client._make_request("/api/test", {"param": "value"})
        
        assert result == {"success": True, "data": "test"}
        mock_post.assert_called_once()
        
    @patch('requests.Session.post')
    def test_api_error_handling(self, mock_post):
        """Test API error handling."""
        # Mock error response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": True, "error_message": "Test error"}
        mock_post.return_value = mock_response
        
        client = KasmAPIClient(
            api_url="https://kasm.example.com",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        with pytest.raises(KasmAPIError) as exc_info:
            client._make_request("/api/test", {"param": "value"})
            
        assert "Test error" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
