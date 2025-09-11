#!/usr/bin/env python3
"""Test script for validating Kasm MCP Server API endpoints."""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.kasm_api.client import KasmAPIClient

# Load environment variables
load_dotenv()


async def test_user_management(client: KasmAPIClient):
    """Test user management endpoints."""
    print("\n" + "="*60)
    print("Testing User Management Endpoints")
    print("="*60)
    
    test_username = f"test_user_{os.urandom(4).hex()}@example.com"
    test_password = "TestPass123!@#"
    user_id = None
    
    try:
        # Test 1: Create User
        print("\n1. Testing create_user...")
        result = await client.create_user(
            username=test_username,
            password=test_password,
            first_name="Test",
            last_name="User",
            organization="Test Org",
            phone="555-0123",
            locked=False,
            disabled=False
        )
        
        if "user" in result:
            user_data = result["user"]
            user_id = user_data.get("user_id")
            print(f"✅ Success! Created user: {test_username}")
            print(f"   User ID: {user_id}")
            print(f"   Groups: {user_data.get('groups', [])}")
        else:
            print(f"❌ Failed: {result}")
            
        # Test 2: Get User
        if user_id:
            print("\n2. Testing get_user...")
            result = await client.get_user(user_id=user_id)
            
            if "user" in result:
                user_data = result["user"]
                print(f"✅ Success! Retrieved user: {user_data.get('username')}")
                print(f"   First Name: {user_data.get('first_name')}")
                print(f"   Last Name: {user_data.get('last_name')}")
                print(f"   Organization: {user_data.get('organization')}")
            else:
                print(f"❌ Failed: {result}")
                
        # Test 3: Update User
        if user_id:
            print("\n3. Testing update_user...")
            result = await client.update_user(
                user_id=user_id,
                first_name="Updated",
                last_name="Name",
                organization="Updated Org"
            )
            
            if "user" in result:
                user_data = result["user"]
                print(f"✅ Success! Updated user: {user_data.get('username')}")
                print(f"   New First Name: {user_data.get('first_name')}")
                print(f"   New Last Name: {user_data.get('last_name')}")
            else:
                print(f"❌ Failed: {result}")
                
        # Test 4: Get All Users
        print("\n4. Testing get_users...")
        result = await client.get_users()
        
        if "users" in result:
            users = result["users"]
            print(f"✅ Success! Retrieved {len(users)} users")
            # Show first 3 users
            for i, user in enumerate(users[:3]):
                print(f"   User {i+1}: {user.get('username')} ({user.get('user_id')})")
        else:
            print(f"❌ Failed: {result}")
            
        # Test 5: Delete User
        if user_id:
            print("\n5. Testing delete_user...")
            result = await client.delete_user(user_id=user_id, force=True)
            
            if result == {} or "error" not in str(result).lower():
                print(f"✅ Success! Deleted user: {test_username}")
            else:
                print(f"❌ Failed: {result}")
                
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


async def test_workspace_management(client: KasmAPIClient):
    """Test workspace/image management endpoints."""
    print("\n" + "="*60)
    print("Testing Workspace Management Endpoints")
    print("="*60)
    
    try:
        # Test: Get Available Images
        print("\n1. Testing get_images...")
        result = await client.get_images()
        
        if "images" in result:
            images = result["images"]
            print(f"✅ Success! Retrieved {len(images)} workspace images")
            # Show first 3 images
            for i, image in enumerate(images[:3]):
                print(f"   Image {i+1}: {image.get('friendly_name', image.get('name'))}")
                print(f"      ID: {image.get('image_id')}")
                print(f"      Enabled: {image.get('enabled', 'Unknown')}")
        else:
            print(f"❌ Failed: {result}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("\n" + "="*60)
    print("Kasm MCP Server API Test Suite")
    print("="*60)
    
    # Get configuration from environment
    api_url = os.getenv("KASM_API_URL")
    api_key = os.getenv("KASM_API_KEY")
    api_secret = os.getenv("KASM_API_SECRET")
    
    if not all([api_url, api_key, api_secret]):
        print("❌ Error: Missing required environment variables")
        print("   Please ensure KASM_API_URL, KASM_API_KEY, and KASM_API_SECRET are set")
        return
    
    print(f"\nConnecting to: {api_url}")
    print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else api_key)
    
    # Create client
    async with KasmAPIClient(api_url, api_key, api_secret) as client:
        # Run tests
        await test_workspace_management(client)
        await test_user_management(client)
    
    print("\n" + "="*60)
    print("Test Suite Complete")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
