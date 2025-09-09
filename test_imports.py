#!/usr/bin/env python3
"""Test script to verify all imports are working correctly."""

import sys
import traceback

def test_imports():
    """Test that all modules can be imported successfully."""
    modules_to_test = [
        "src.server",
        "src.kasm_api.client",
        "src.security.roots",
        "src.tools.command",
        "src.tools.session",
        "src.tools.admin",
    ]
    
    print("Testing imports for Kasm MCP Server...")
    print("-" * 50)
    
    all_passed = True
    
    for module in modules_to_test:
        try:
            # Attempt to import the module
            __import__(module)
            print(f"✓ {module} - imported successfully")
        except ImportError as e:
            print(f"✗ {module} - import failed: {e}")
            all_passed = False
        except Exception as e:
            print(f"✗ {module} - unexpected error: {e}")
            traceback.print_exc()
            all_passed = False
    
    print("-" * 50)
    
    if all_passed:
        print("✓ All imports successful!")
        return 0
    else:
        print("✗ Some imports failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(test_imports())
