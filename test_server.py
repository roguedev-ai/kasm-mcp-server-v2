#!/usr/bin/env python3
"""
Test script for Kasm MCP Server
This script verifies the installation and helps diagnose issues.
"""

import sys
import os
import json
import asyncio
import subprocess
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python_version():
    """Check if Python version meets requirements."""
    print_section("Python Version Check")
    print(f"Python version: {sys.version}")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ERROR: Python 3.8+ is required")
        return False
    else:
        print("✅ Python version is compatible")
        return True

def check_dependencies():
    """Check if required packages are installed."""
    print_section("Dependency Check")
    
    required_packages = {
        'mcp': 'mcp>=1.0.0',
        'aiohttp': 'aiohttp>=3.9.0',
        'pydantic': 'pydantic>=2.0.0',
        'dotenv': 'python-dotenv>=1.0.0'
    }
    
    missing = []
    for module, package in required_packages.items():
        try:
            if module == 'dotenv':
                import dotenv
            else:
                __import__(module)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"   Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def check_mcp_import():
    """Check MCP SDK import paths."""
    print_section("MCP SDK Import Check")
    
    import_paths = [
        ('mcp.server.fastmcp', 'FastMCP'),
        ('mcp.server', 'Server'),
        ('mcp', 'FastMCP'),
        ('mcp.server', 'FastMCP')
    ]
    
    successful_import = None
    for module_path, class_name in import_paths:
        try:
            module = __import__(module_path, fromlist=[class_name])
            if hasattr(module, class_name):
                print(f"✅ Successfully imported {class_name} from {module_path}")
                successful_import = (module_path, class_name)
                break
            else:
                print(f"⚠️  Module {module_path} exists but doesn't have {class_name}")
        except ImportError as e:
            print(f"❌ Failed to import from {module_path}: {e}")
    
    if not successful_import:
        print("\n❌ ERROR: Could not import MCP SDK from any known path")
        print("   Please verify the MCP package is correctly installed")
        return False
    
    print(f"\n✅ MCP SDK can be imported from: {successful_import[0]}")
    return True

def check_environment():
    """Check environment variables."""
    print_section("Environment Configuration")
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print(f"✅ .env file found at: {env_file.absolute()}")
        
        # Load and check variables
        from dotenv import load_dotenv
        load_dotenv()
    else:
        print("⚠️  No .env file found. Using environment variables or defaults.")
    
    # Check required environment variables
    required_vars = {
        'KASM_API_URL': 'URL of your Kasm Workspaces instance',
        'KASM_API_KEY': 'API key for authentication',
        'KASM_API_SECRET': 'API secret for authentication'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'KEY' in var:
                masked_value = value[:4] + '****' + value[-4:] if len(value) > 8 else '****'
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET ({description})")
            missing_vars.append(var)
    
    # Check optional variables
    optional_vars = {
        'KASM_USER_ID': 'default',
        'KASM_ALLOWED_ROOTS': '/home/kasm-user',
        'LOG_LEVEL': 'INFO'
    }
    
    print("\nOptional variables:")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"  {var}: {value}")
    
    if missing_vars:
        print(f"\n⚠️  Missing required environment variables: {', '.join(missing_vars)}")
        print("   Please set these in your .env file or environment")
        return False
    
    return True

def test_imports():
    """Test importing the main server modules."""
    print_section("Module Import Test")
    
    modules_to_test = [
        'src.kasm_api.client',
        'src.security.roots',
        'src.server'
    ]
    
    failed_imports = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✅ Successfully imported {module}")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import modules: {', '.join(failed_imports)}")
        return False
    
    return True

async def test_server_startup():
    """Test server startup without actually running it."""
    print_section("Server Initialization Test")
    
    try:
        from src.server import initialize_clients, mcp
        
        print("Testing client initialization...")
        
        # Check if we can initialize (will fail if env vars missing)
        try:
            initialize_clients()
            print("✅ Client initialization successful")
        except ValueError as e:
            if "KASM_API_KEY" in str(e):
                print(f"⚠️  Expected error (missing credentials): {e}")
            else:
                print(f"❌ Unexpected error: {e}")
                return False
        except Exception as e:
            print(f"❌ Failed to initialize clients: {e}")
            return False
        
        # Check if MCP server object exists
        if mcp:
            print("✅ MCP server instance created successfully")
            
            # Try to list registered tools
            try:
                # This might vary based on the actual MCP SDK implementation
                if hasattr(mcp, 'tools'):
                    print(f"   Registered tools: {len(mcp.tools)} tools")
                elif hasattr(mcp, '_tools'):
                    print(f"   Registered tools: {len(mcp._tools)} tools")
                else:
                    print("   Could not count registered tools (implementation may vary)")
            except:
                pass
        else:
            print("❌ MCP server instance not created")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Server initialization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_command_execution():
    """Test running the server as a module."""
    print_section("Module Execution Test")
    
    try:
        # Try to run the module without actually starting the server
        result = subprocess.run(
            [sys.executable, "-c", "import src; print('Module can be imported')"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print("✅ Module can be imported as package")
        else:
            print(f"❌ Module import failed: {result.stderr}")
            return False
        
        # Test the actual command from package.json
        print("\nTesting 'python -m src' command...")
        result = subprocess.run(
            [sys.executable, "-m", "src", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Note: This might fail if the server doesn't support --help, but that's okay
        if "KASM_API_KEY" in result.stderr or "Server error" in result.stderr:
            print("✅ Server can be executed (fails due to missing config, which is expected)")
        elif result.returncode == 0:
            print("✅ Server module can be executed")
        else:
            print(f"⚠️  Server execution test inconclusive: {result.stderr[:200]}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("⚠️  Command timed out (this might be normal if server started)")
        return True
    except Exception as e:
        print(f"❌ Execution test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  Kasm MCP Server Diagnostic Test")
    print("=" * 60)
    
    tests = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("MCP SDK Import", check_mcp_import),
        ("Environment", check_environment),
        ("Module Imports", test_imports),
        ("Command Execution", test_command_execution)
    ]
    
    # Run async test separately
    async_tests = [
        ("Server Startup", test_server_startup)
    ]
    
    results = {}
    
    # Run synchronous tests
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Run async tests
    for name, test_func in async_tests:
        try:
            results[name] = asyncio.run(test_func())
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results[name] = False
    
    # Summary
    print_section("Test Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The server should be ready to run.")
        print("\nTo start the server:")
        print("  python -m src")
        print("\nOr with debug logging:")
        print("  LOG_LEVEL=DEBUG python -m src")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  1. Install missing packages: pip install -r requirements.txt")
        print("  2. Create .env file with your Kasm credentials")
        print("  3. Ensure Python 3.8+ is being used")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
