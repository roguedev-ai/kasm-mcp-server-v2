#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import traceback

def test_imports():
    """Test all imports to ensure they work correctly."""
    
    print("Testing imports for Kasm MCP Server V2...")
    print("-" * 50)
    
    tests = [
        ("MCP SDK", "from mcp.server.fastmcp import FastMCP"),
        ("Kasm API Client", "from src.kasm_api import KasmAPIClient"),
        ("Security", "from src.security import RootsValidator, SecurityError"),
        ("Server Main", "from src.server import main, mcp"),
        ("Environment", "from dotenv import load_dotenv"),
        ("Async Support", "import asyncio"),
        ("Logging", "import logging"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✓ {name}: SUCCESS")
            passed += 1
        except Exception as e:
            print(f"✗ {name}: FAILED - {type(e).__name__}: {str(e)}")
            failed += 1
            if "--verbose" in sys.argv:
                traceback.print_exc()
    
    print("-" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ All imports successful! The server is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure environment: cp .env.example .env")
        print("3. Run the server: python -m src")
    else:
        print("\n❌ Some imports failed. Please install dependencies:")
        print("   pip install -r requirements.txt")
    
    return failed == 0

if __name__ == "__main__":
    # Add the project directory to Python path
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    success = test_imports()
    sys.exit(0 if success else 1)
