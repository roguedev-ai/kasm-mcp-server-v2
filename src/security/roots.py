"""MCP Roots security implementation for validating file operations."""

import logging
import os
from pathlib import Path
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Security violation exception."""
    pass


class RootsValidator:
    """Validates file operations against MCP Roots security boundaries."""
    
    def __init__(self, allowed_roots: Optional[List[str]] = None):
        """Initialize the roots validator.
        
        Args:
            allowed_roots: List of allowed root directories. If None, defaults to ["/home/kasm-user"]
        """
        if allowed_roots is None:
            allowed_roots = ["/home/kasm-user"]
            
        self.allowed_roots: Set[Path] = set()
        for root in allowed_roots:
            try:
                # Resolve to absolute path
                root_path = Path(root).resolve()
                self.allowed_roots.add(root_path)
                logger.info(f"Added allowed root: {root_path}")
            except Exception as e:
                logger.warning(f"Failed to add root {root}: {e}")
                
    def is_path_allowed(self, path: str) -> bool:
        """Check if a path is within allowed roots.
        
        Args:
            path: Path to check
            
        Returns:
            True if path is allowed, False otherwise
        """
        try:
            # Resolve the path
            target_path = Path(path).resolve()
            
            # Check if path is under any allowed root
            for root in self.allowed_roots:
                try:
                    # Check if target is relative to root
                    target_path.relative_to(root)
                    return True
                except ValueError:
                    # Path is not relative to this root
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking path {path}: {e}")
            return False
            
    def validate_command(self, command: str, working_dir: Optional[str] = None) -> None:
        """Validate a command for security violations.
        
        Args:
            command: Command to validate
            working_dir: Working directory for command execution
            
        Raises:
            SecurityError: If command contains security violations
        """
        # Check for dangerous patterns
        dangerous_patterns = [
            "../",  # Directory traversal
            "/..",  # Directory traversal variant
            "|",    # Pipe (could be used for command injection)
            ";",    # Command separator
            "&&",   # Command chaining
            "||",   # Command chaining
            "`",    # Command substitution
            "$(",   # Command substitution
            "${",   # Variable expansion that could be dangerous
            ">>",   # Append redirect (could overwrite files)
            ">",    # Redirect (could overwrite files)
            "<",    # Input redirect
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command:
                raise SecurityError(
                    f"Command contains potentially dangerous pattern: {pattern}"
                )
                
        # Validate working directory if provided
        if working_dir:
            if not self.is_path_allowed(working_dir):
                raise SecurityError(
                    f"Working directory outside allowed roots: {working_dir}"
                )
                
    def validate_file_operation(self, file_path: str, operation: str = "access") -> None:
        """Validate a file operation against security boundaries.
        
        Args:
            file_path: Path to the file
            operation: Type of operation (read, write, access)
            
        Raises:
            SecurityError: If operation violates security boundaries
        """
        # Check if path is within allowed roots
        if not self.is_path_allowed(file_path):
            raise SecurityError(
                f"File {operation} outside allowed roots: {file_path}"
            )
            
        # Additional checks for write operations
        if operation == "write":
            # Check for attempts to write to sensitive locations
            sensitive_paths = [
                "/etc",
                "/usr",
                "/bin",
                "/sbin",
                "/lib",
                "/proc",
                "/sys",
                "/dev",
                ".ssh",
                ".gnupg",
            ]
            
            path_str = str(Path(file_path).resolve())
            for sensitive in sensitive_paths:
                if path_str.startswith(sensitive) or f"/{sensitive}/" in path_str:
                    raise SecurityError(
                        f"Attempt to write to sensitive location: {file_path}"
                    )
                    
    def get_safe_path(self, path: str) -> Optional[str]:
        """Get a safe version of a path if it's within allowed roots.
        
        Args:
            path: Path to make safe
            
        Returns:
            Safe absolute path if allowed, None otherwise
        """
        try:
            resolved_path = Path(path).resolve()
            
            if self.is_path_allowed(str(resolved_path)):
                return str(resolved_path)
                
            return None
            
        except Exception as e:
            logger.error(f"Error resolving path {path}: {e}")
            return None
            
    def add_root(self, root: str) -> bool:
        """Add a new allowed root directory.
        
        Args:
            root: Root directory to add
            
        Returns:
            True if root was added successfully
        """
        try:
            root_path = Path(root).resolve()
            self.allowed_roots.add(root_path)
            logger.info(f"Added allowed root: {root_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to add root {root}: {e}")
            return False
            
    def remove_root(self, root: str) -> bool:
        """Remove an allowed root directory.
        
        Args:
            root: Root directory to remove
            
        Returns:
            True if root was removed successfully
        """
        try:
            root_path = Path(root).resolve()
            if root_path in self.allowed_roots:
                self.allowed_roots.remove(root_path)
                logger.info(f"Removed allowed root: {root_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove root {root}: {e}")
            return False
            
    def get_allowed_roots(self) -> List[str]:
        """Get list of allowed root directories.
        
        Returns:
            List of allowed root paths as strings
        """
        return [str(root) for root in sorted(self.allowed_roots)]
