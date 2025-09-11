#!/usr/bin/env python3
"""Debug script for Kasm session creation issues."""

import asyncio
import json
import logging
import os
from typing import Dict, Any

import aiohttp
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


async def make_raw_request(
    url: str,
    api_key: str,
    api_secret: str,
    endpoint: str,
    data: Dict[str, Any]
) -> None:
    """Make a raw request to debug the API response."""
    
    full_url = f"{url.rstrip('/')}{endpoint}"
    
    # Add authentication
    auth_data = {
        "api_key": api_key,
        "api_key_secret": api_secret
    }
    auth_data.update(data)
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"URL: {full_url}")
    print(f"Request data: {json.dumps(auth_data, indent=2)}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"{'='*60}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                full_url,
                json=auth_data,
                headers=headers,
                ssl=False  # Disable SSL verification for testing
            ) as response:
                content_type = response.headers.get('content-type', '')
                status = response.status
                
                print(f"Status: {status}")
                print(f"Content-Type: {content_type}")
                print(f"Response Headers: {dict(response.headers)}")
                
                if 'application/json' in content_type:
                    try:
                        json_data = await response.json()
                        print(f"JSON Response: {json.dumps(json_data, indent=2)}")
                    except:
                        text = await response.text()
                        print(f"Failed to parse JSON. Raw text: {text[:500]}")
                elif 'text/html' in content_type:
                    html = await response.text()
                    print(f"HTML Response (first 1000 chars):")
                    print(html[:1000])
                    
                    # Try to extract error messages from HTML
                    import re
                    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
                    if title_match:
                        print(f"\nExtracted title: {title_match.group(1)}")
                    
                    error_matches = re.findall(r'error["\']?\s*[:>]\s*([^<]+)', html, re.IGNORECASE)
                    if error_matches:
                        print(f"\nExtracted errors:")
                        for error in error_matches[:5]:
                            print(f"  - {error.strip()}")
                else:
                    text = await response.text()
                    print(f"Other response type. Raw text: {text[:500]}")
                    
        except Exception as e:
            print(f"Request failed: {e}")


async def test_session_creation_variations():
    """Test different variations of session creation."""
    
    api_url = os.getenv("KASM_API_URL", "https://workspaces.workoverip.com")
    api_key = os.getenv("KASM_API_KEY", "")
    api_secret = os.getenv("KASM_API_SECRET", "")
    user_id = os.getenv("KASM_USER_ID", "")
    group_id = os.getenv("KASM_GROUP_ID", "68d557ac4cac42cca9f31c7c853de0f3")
    
    if not all([api_key, api_secret, user_id]):
        print("ERROR: Missing required environment variables")
        print(f"KASM_API_KEY: {'SET' if api_key else 'NOT SET'}")
        print(f"KASM_API_SECRET: {'SET' if api_secret else 'NOT SET'}")
        print(f"KASM_USER_ID: {user_id if user_id else 'NOT SET'}")
        return
    
    print(f"\nConfiguration:")
    print(f"API URL: {api_url}")
    print(f"User ID: {user_id}")
    print(f"Group ID: {group_id}")
    
    # Test 1: Get users (known to work)
    print("\n" + "="*60)
    print("TEST 1: Get users (baseline - should work)")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/get_users",
        {}
    )
    
    # Test 2: Get images (should work)
    print("\n" + "="*60)
    print("TEST 2: Get images (should work)")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/get_images",
        {}
    )
    
    # Test 3: Session creation with image_id (UUID without hyphens)
    print("\n" + "="*60)
    print("TEST 3: Create session with image_id (no hyphens)")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/request_kasm",
        {
            "image_id": "01366df3a03b4bccbb8c913846594826",
            "user_id": user_id.replace('-', ''),  # Try without hyphens
            "group_id": group_id.replace('-', '')
        }
    )
    
    # Test 4: Session creation with image_id (UUID with hyphens)
    print("\n" + "="*60)
    print("TEST 4: Create session with image_id (with hyphens)")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/request_kasm",
        {
            "image_id": "01366df3-a03b-4bcc-bb8c-913846594826",
            "user_id": user_id,  # Keep hyphens
            "group_id": group_id
        }
    )
    
    # Test 5: Session creation with image_name
    print("\n" + "="*60)
    print("TEST 5: Create session with image_name")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/request_kasm",
        {
            "image_name": "kasmweb/chrome:1.16.0",
            "user_id": user_id,
            "group_id": group_id
        }
    )
    
    # Test 6: Get user's active sessions
    print("\n" + "="*60)
    print("TEST 6: Get user's active sessions")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/get_user_kasms",
        {
            "user_id": user_id
        }
    )
    
    # Test 7: Try with minimal data
    print("\n" + "="*60)
    print("TEST 7: Create session with minimal data")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/request_kasm",
        {
            "image_id": "01366df3a03b4bccbb8c913846594826",
            "user_id": user_id.replace('-', '')
        }
    )
    
    # Test 8: Check authentication only
    print("\n" + "="*60)
    print("TEST 8: Simple auth check")
    await make_raw_request(
        api_url, api_key, api_secret,
        "/api/public/get_kasms",
        {}
    )


if __name__ == "__main__":
    print("Kasm Session Creation Debug Script")
    print("===================================")
    asyncio.run(test_session_creation_variations())
