"""MCP Roots security implementation for safe command execution."""

import os
import re
from pathlib import Path
from typing import List, Optional, Set


class SecurityError(Exception):
    """Security violation exception."""
    pass


class RootsValidator:
    """Validates file paths and commands against allowed roots."""
    
    def __init__(self, allowed_roots: List[str]):
        """
        Initialize roots validator.
        
        Args:
            allowed_roots: List of allowed root directories
        """
        self.allowed_roots = [Path(root).resolve() for root in allowed_roots]
        
        # Patterns for detecting potentially dangerous commands
        self.dangerous_patterns = [
            # Directory traversal
            r'\.\./|/\.\.',
            # Absolute paths outside allowed roots (checked separately)
            # Shell redirections that could escape sandbox
            r'>\s*/dev/|<\s*/dev/',
            # Dangerous commands
            r'\b(chmod|chown|mount|umount|mkfs|dd|fdisk)\b',
            # Network utilities that could be misused
            r'\b(nc|netcat|socat|nmap)\b\s+-[lep]',
            # System modification
            r'/etc/passwd|/etc/shadow|/etc/sudoers',
            # Kernel and boot
            r'/boot/|/sys/|/proc/sys/',
        ]
        
        # Commands that are always blocked
        self.blocked_commands = {
            'sudo', 'su', 'passwd', 'useradd', 'userdel', 'usermod',
            'groupadd', 'groupdel', 'groupmod', 'visudo', 'systemctl',
            'service', 'init', 'shutdown', 'reboot', 'halt', 'poweroff'
        }
        
    def is_path_allowed(self, path: str) -> bool:
        """
        Check if a path is within allowed roots.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is allowed, False otherwise
        """
        try:
            # Resolve the path (follow symlinks, make absolute)
            resolved_path = Path(path).resolve()
            
            # Check if path is under any allowed root
            for allowed_root in self.allowed_roots:
                try:
                    resolved_path.relative_to(allowed_root)
                    return True
                except ValueError:
                    # Path is not relative to this root
                    continue
                    
            return False
            
        except (OSError, RuntimeError):
            # Path resolution failed (e.g., path doesn't exist)
            # We still need to check if the path would be allowed
            path_obj = Path(path)
            if path_obj.is_absolute():
                for allowed_root in self.allowed_roots:
                    if str(path_obj).startswith(str(allowed_root)):
                        return True
            return False
    
    def validate_command(self, command: str, working_dir: Optional[str] = None) -> None:
        """
        Validate a command for security issues.
        
        Args:
            command: Command to validate
            working_dir: Working directory for command execution
            
        Raises:
            SecurityError: If command violates security rules
        """
        # Check for blocked commands
        command_parts = command.strip().split()
        if command_parts:
            base_command = os.path.basename(command_parts[0])
            if base_command in self.blocked_commands:
                raise SecurityError(f"Command '{base_command}' is not allowed")
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                raise SecurityError(f"Command contains dangerous pattern: {pattern}")
        
        # Validate working directory if provided
        if working_dir:
            if not self.is_path_allowed(working_dir):
                raise SecurityError(f"Working directory '{working_dir}' is outside allowed roots")
        
        # Extract and validate file paths from command
        self._validate_command_paths(command)
    
    def _validate_command_paths(self, command: str) -> None:
        """
        Extract and validate file paths from command.
        
        Args:
            command: Command to analyze
            
        Raises:
            SecurityError: If command contains paths outside allowed roots
        """
        # Common patterns for file paths in commands
        path_patterns = [
            # Absolute paths
            r'(?:^|\s)(/[^\s;|&<>]+)',
            # Paths with common file operations
            r'(?:cat|less|more|head|tail|grep|find|ls)\s+([^\s;|&<>]+)',
            # Redirection targets
            r'>\s*([^\s;|&<>]+)',
            r'<\s*([^\s;|&<>]+)',
            # Common file manipulation commands
            r'(?:cp|mv|rm|touch|mkdir)\s+[^\s]*\s+([^\s;|&<>]+)',
        ]
        
        for pattern in path_patterns:
            matches = re.findall(pattern, command)
            for match in matches:
                # Skip flags and options
                if match.startswith('-'):
                    continue
                    
                # Check absolute paths
                if match.startswith('/'):
                    if not self.is_path_allowed(match):
                        raise SecurityError(f"Path '{match}' is outside allowed roots")
    
    def validate_file_operation(self, file_path: str, operation: str = "access") -> None:
        """
        Validate a file operation.
        
        Args:
            file_path: Path to validate
            operation: Type of operation (read, write, access)
            
        Raises:
            SecurityError: If operation is not allowed
        """
        if not self.is_path_allowed(file_path):
            raise SecurityError(
                f"Cannot {operation} file '{file_path}': Path is outside allowed roots"
            )
    
    def get_safe_path(self, path: str, base_dir: Optional[str] = None) -> str:
        """
        Get a safe, validated path.
        
        Args:
            path: Path to make safe
            base_dir: Base directory for relative paths
            
        Returns:
            Safe, absolute path
            
        Raises:
            SecurityError: If path cannot be made safe
        """
        if base_dir and not os.path.isabs(path):
            full_path = os.path.join(base_dir, path)
        else:
            full_path = path
            
        # Normalize and resolve the path
        try:
            safe_path = str(Path(full_path).resolve())
        except (OSError, RuntimeError):
            # If path doesn't exist, normalize it
            safe_path = os.path.normpath(full_path)
            
        if not self.is_path_allowed(safe_path):
            raise SecurityError(f"Path '{path}' is outside allowed roots")
            
        return safe_path
