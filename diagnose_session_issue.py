#!/usr/bin/env python3
"""
Comprehensive diagnostic script for Kasm session creation issues.
This script tests various configurations and parameter combinations
to identify the exact cause of session creation failures.
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from kasm_api.client import KasmAPIClient


async def test_api_connectivity(client):
    """Test basic API connectivity and authentication."""
    print("\n" + "="*60)
    print("TESTING API CONNECTIVITY")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Get Images
    print("\n1. Testing get_images endpoint...")
    try:
        result = await client.get_images()
        print(f"✅ SUCCESS: Retrieved {len(result.get('images', []))} workspace images")
        tests_passed += 1
        
        # Show available images
        print("\nAvailable Images:")
        for img in result.get('images', [])[:5]:  # Show first 5
            print(f"  - {img.get('friendly_name', 'Unknown')} (ID: {img.get('image_id', 'N/A')})")
            print(f"    Docker: {img.get('image_src', 'N/A')}")
        
        return result.get('images', [])
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        tests_failed += 1
        return []


async def test_user_operations(client):
    """Test user-related operations."""
    print("\n" + "="*60)
    print("TESTING USER OPERATIONS")
    print("="*60)
    
    # Test: Get Users
    print("\n1. Testing get_users endpoint...")
    try:
        result = await client.get_users()
        users = result.get('users', [])
        print(f"✅ SUCCESS: Retrieved {len(users)} users")
        
        # Find the primary user
        primary_user = None
        for user in users:
            if 'jaymes.davis@kasmweb.com' in user.get('username', ''):
                primary_user = user
                break
        
        if primary_user:
            print(f"\nPrimary User Found:")
            print(f"  Username: {primary_user.get('username')}")
            print(f"  User ID: {primary_user.get('user_id')}")
            print(f"  Groups: {[g.get('name') for g in primary_user.get('groups', [])]}")
            
            return primary_user
        else:
            print("⚠️ WARNING: Primary user not found in user list")
            if users:
                print(f"First user in list: {users[0].get('username')} (ID: {users[0].get('user_id')})")
                return users[0]
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return None


async def test_session_creation_variants(client, user_info, images):
    """Test different session creation parameter combinations."""
    print("\n" + "="*60)
    print("TESTING SESSION CREATION VARIANTS")
    print("="*60)
    
    if not user_info or not images:
        print("❌ Cannot test session creation: Missing user info or images")
        return
    
    user_id = user_info.get('user_id')
    groups = user_info.get('groups', [])
    
    if not groups:
        print("❌ User has no groups assigned")
        return
    
    group_id = groups[0].get('group_id')
    print(f"\nUsing User ID: {user_id}")
    print(f"Using Group ID: {group_id}")
    
    # Find Chrome image
    chrome_image = None
    for img in images:
        if 'chrome' in img.get('friendly_name', '').lower():
            chrome_image = img
            break
    
    if not chrome_image:
        print("⚠️ Chrome image not found, using first available image")
        chrome_image = images[0]
    
    print(f"\nTarget Image: {chrome_image.get('friendly_name', 'Unknown')}")
    print(f"  Image ID: {chrome_image.get('image_id', 'N/A')}")
    print(f"  Docker: {chrome_image.get('image_src', 'N/A')}")
    
    # Test variants
    test_cases = [
        {
            "name": "Using image_id WITH hyphens",
            "image": chrome_image.get('image_id', ''),
            "description": "Standard UUID format with hyphens"
        },
        {
            "name": "Using image_id WITHOUT hyphens",
            "image": chrome_image.get('image_id', '').replace('-', ''),
            "description": "UUID format without hyphens"
        },
        {
            "name": "Using Docker image name",
            "image": chrome_image.get('image_src', ''),
            "description": "Full Docker image reference"
        },
        {
            "name": "Using friendly name",
            "image": chrome_image.get('friendly_name', ''),
            "description": "Human-readable image name"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        print(f"Description: {test_case['description']}")
        print(f"Image Parameter: {test_case['image']}")
        
        if not test_case['image']:
            print("⚠️ SKIPPED: Image value is empty")
            continue
        
        try:
            print("Attempting session creation...")
            result = await client.request_kasm(
                image_name=test_case['image'],
                user_id=user_id,
                group_id=group_id
            )
            
            print(f"✅ SUCCESS! Session created")
            print(f"  Session ID: {result.get('kasm_id', 'N/A')}")
            print(f"  URL: {result.get('kasm_url', 'N/A')}")
            
            # Try to destroy the session
            if result.get('kasm_id'):
                print("  Cleaning up session...")
                try:
                    await client.destroy_kasm(result['kasm_id'], user_id)
                    print("  ✅ Session destroyed")
                except Exception as e:
                    print(f"  ⚠️ Failed to destroy session: {e}")
            
            return True  # Success!
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ FAILED: {error_msg}")
            
            # Analyze error
            if "500" in error_msg and "HTML" in error_msg:
                print("  💡 Analysis: Server returning HTML error page (500 status)")
                print("     This suggests server-side validation or processing error")
            elif "404" in error_msg:
                print("  💡 Analysis: Endpoint not found")
            elif "403" in error_msg:
                print("  💡 Analysis: Permission denied")
            elif "401" in error_msg:
                print("  💡 Analysis: Authentication failed")
    
    return False


async def test_raw_api_call(client):
    """Test a raw API call with minimal parameters."""
    print("\n" + "="*60)
    print("TESTING RAW API CALL")
    print("="*60)
    
    # Get environment variables directly
    user_id = os.getenv('KASM_USER_ID')
    group_id = os.getenv('KASM_DEFAULT_GROUP_ID', '68d557ac4cac42cca9f31c7c853de0f3')
    
    print(f"\nDirect from environment:")
    print(f"  User ID: {user_id}")
    print(f"  Group ID: {group_id}")
    
    if not user_id:
        print("❌ KASM_USER_ID not set in environment")
        return
    
    # Test with absolutely minimal parameters
    print("\n1. Testing with minimal parameters (user_id and group_id only)...")
    try:
        data = {
            "user_id": user_id,
            "group_id": group_id
        }
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        result = await client._make_request("POST", "/api/public/request_kasm", data)
        print(f"✅ SUCCESS: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
    
    # Test with workspace_id (another possible parameter)
    print("\n2. Testing with workspace_id parameter...")
    try:
        # First get workspaces
        workspaces = await client.get_images()
        if workspaces.get('images'):
            workspace = workspaces['images'][0]
            data = {
                "user_id": user_id,
                "group_id": group_id,
                "workspace_id": workspace.get('image_id', '').replace('-', '')
            }
            print(f"Request data: {json.dumps(data, indent=2)}")
            
            result = await client._make_request("POST", "/api/public/request_kasm", data)
            print(f"✅ SUCCESS: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")


async def check_session_limits(client, user_id):
    """Check if there are existing sessions that might be blocking new ones."""
    print("\n" + "="*60)
    print("CHECKING EXISTING SESSIONS")
    print("="*60)
    
    try:
        # Get user's active sessions
        result = await client.get_user_kasms(user_id)
        sessions = result.get('kasms', [])
        
        if sessions:
            print(f"⚠️ Found {len(sessions)} active session(s):")
            for session in sessions:
                print(f"  - Session ID: {session.get('kasm_id')}")
                print(f"    Image: {session.get('image', 'Unknown')}")
                print(f"    Status: {session.get('operational_status', 'Unknown')}")
                print(f"    Created: {session.get('created', 'Unknown')}")
            
            print("\n💡 Existing sessions might be blocking new ones.")
            print("   Some Kasm configurations limit concurrent sessions per user.")
            
            # Offer to destroy sessions
            print("\nAttempting to clean up old sessions...")
            for session in sessions:
                try:
                    await client.destroy_kasm(session['kasm_id'], user_id)
                    print(f"  ✅ Destroyed session {session['kasm_id']}")
                except Exception as e:
                    print(f"  ❌ Failed to destroy session {session['kasm_id']}: {e}")
        else:
            print("✅ No existing sessions found for user")
            
    except Exception as e:
        print(f"❌ Failed to check sessions: {str(e)}")


async def main():
    """Main diagnostic routine."""
    print("\n" + "="*70)
    print(" KASM SESSION CREATION DIAGNOSTIC TOOL ")
    print("="*70)
    
    # Load environment variables
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from {env_path}")
    else:
        print(f"⚠️ No .env file found at {env_path}")
    
    # Check required environment variables
    api_url = os.getenv('KASM_API_URL')
    api_key = os.getenv('KASM_API_KEY')
    api_secret = os.getenv('KASM_API_SECRET')
    user_id = os.getenv('KASM_USER_ID')
    
    print("\nEnvironment Check:")
    print(f"  KASM_API_URL: {'✅ Set' if api_url else '❌ Missing'} ({api_url if api_url else 'Not set'})")
    print(f"  KASM_API_KEY: {'✅ Set' if api_key else '❌ Missing'} ({'*' * 10 if api_key else 'Not set'})")
    print(f"  KASM_API_SECRET: {'✅ Set' if api_secret else '❌ Missing'} ({'*' * 10 if api_secret else 'Not set'})")
    print(f"  KASM_USER_ID: {'✅ Set' if user_id else '❌ Missing'} ({user_id if user_id else 'Not set'})")
    
    if not all([api_url, api_key, api_secret]):
        print("\n❌ Missing required environment variables. Please check your .env file.")
        return 1
    
    # Create client
    async with KasmAPIClient(api_url, api_key, api_secret) as client:
        # Run tests
        images = await test_api_connectivity(client)
        user_info = await test_user_operations(client)
        
        if user_id:
            await check_session_limits(client, user_id)
        
        success = await test_session_creation_variants(client, user_info, images)
        await test_raw_api_call(client)
        
        # Summary
        print("\n" + "="*70)
        print(" DIAGNOSTIC SUMMARY ")
        print("="*70)
        
        if success:
            print("\n✅ Session creation SUCCEEDED with at least one configuration!")
            print("   Check the logs above to see which parameter format worked.")
        else:
            print("\n❌ Session creation FAILED with all tested configurations.")
            print("\nPossible causes:")
            print("  1. API credentials lack session creation permissions")
            print("  2. User has reached session limit")
            print("  3. No workspace images are available for the user's groups")
            print("  4. Kasm server configuration issue")
            print("  5. Network/firewall blocking certain API calls")
            print("\nRecommended actions:")
            print("  1. Check Kasm server logs for detailed error messages")
            print("  2. Verify API token has 'Kasm Sessions' permissions")
            print("  3. Check user's group memberships and workspace assignments")
            print("  4. Try creating a session through Kasm web UI to verify it works")
            print("  5. Contact Kasm support if issue persists")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
