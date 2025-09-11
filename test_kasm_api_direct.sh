#!/bin/bash

# Direct Kasm API Testing Script
# This script tests the Kasm API directly using curl to diagnose session creation issues

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Kasm API Direct Testing Script${NC}"
echo "================================"
echo ""

# Check required environment variables
if [ -z "$KASM_API_URL" ] || [ -z "$KASM_API_KEY" ] || [ -z "$KASM_API_SECRET" ] || [ -z "$KASM_USER_ID" ]; then
    echo -e "${RED}Error: Missing required environment variables${NC}"
    echo "Please ensure the following are set in your .env file:"
    echo "  KASM_API_URL"
    echo "  KASM_API_KEY"
    echo "  KASM_API_SECRET"
    echo "  KASM_USER_ID"
    echo "  KASM_GROUP_ID (optional, will use default if not set)"
    exit 1
fi

# Set default group ID if not provided
KASM_GROUP_ID=${KASM_GROUP_ID:-"68d557ac4cac42cca9f31c7c853de0f3"}

echo "Configuration:"
echo "  API URL: $KASM_API_URL"
echo "  User ID: $KASM_USER_ID"
echo "  Group ID: $KASM_GROUP_ID"
echo ""

# Function to make API request and format output
make_request() {
    local endpoint=$1
    local data=$2
    local description=$3
    
    echo -e "${YELLOW}Testing: $description${NC}"
    echo "Endpoint: $endpoint"
    echo "Request Data:"
    echo "$data" | jq '.' 2>/dev/null || echo "$data"
    echo ""
    
    response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$data" \
        "${KASM_API_URL}${endpoint}")
    
    http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    body=$(echo "$response" | sed '$d')
    
    echo "HTTP Status: $http_status"
    
    # Try to parse as JSON
    if echo "$body" | jq '.' 2>/dev/null; then
        echo -e "${GREEN}Response is valid JSON${NC}"
    else
        echo -e "${RED}Response is not JSON. First 500 chars:${NC}"
        echo "$body" | head -c 500
        echo ""
        
        # Try to extract error from HTML
        if [[ "$body" == *"<title>"* ]]; then
            title=$(echo "$body" | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g')
            echo -e "${YELLOW}HTML Title: $title${NC}"
        fi
    fi
    
    echo ""
    echo "----------------------------------------"
    echo ""
}

# Test 1: Get Users (baseline test - should work)
echo -e "${GREEN}TEST 1: Get Users (Baseline)${NC}"
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET"
}
EOF
)
make_request "/api/public/get_users" "$data" "Get list of users"

# Test 2: Get Images
echo -e "${GREEN}TEST 2: Get Images${NC}"
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET"
}
EOF
)
make_request "/api/public/get_images" "$data" "Get available workspace images"

# Test 3: Create session with image_id (no hyphens in any UUID)
echo -e "${GREEN}TEST 3: Create Session - image_id (no hyphens)${NC}"
user_id_no_hyphens=$(echo "$KASM_USER_ID" | tr -d '-')
group_id_no_hyphens=$(echo "$KASM_GROUP_ID" | tr -d '-')
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET",
    "image_id": "01366df3a03b4bccbb8c913846594826",
    "user_id": "$user_id_no_hyphens",
    "group_id": "$group_id_no_hyphens"
}
EOF
)
make_request "/api/public/request_kasm" "$data" "Session with image_id (no hyphens in any field)"

# Test 4: Create session with image_id (hyphens in user/group)
echo -e "${GREEN}TEST 4: Create Session - image_id (with hyphens in user/group)${NC}"
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET",
    "image_id": "01366df3a03b4bccbb8c913846594826",
    "user_id": "$KASM_USER_ID",
    "group_id": "$KASM_GROUP_ID"
}
EOF
)
make_request "/api/public/request_kasm" "$data" "Session with image_id (hyphens in user/group)"

# Test 5: Create session with image_name
echo -e "${GREEN}TEST 5: Create Session - image_name${NC}"
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET",
    "image_name": "kasmweb/chrome:1.16.0",
    "user_id": "$KASM_USER_ID",
    "group_id": "$KASM_GROUP_ID"
}
EOF
)
make_request "/api/public/request_kasm" "$data" "Session with image_name"

# Test 6: Get user's active sessions
echo -e "${GREEN}TEST 6: Get User Sessions${NC}"
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET",
    "user_id": "$KASM_USER_ID"
}
EOF
)
make_request "/api/public/get_user_kasms" "$data" "Get user's active sessions"

# Test 7: Get all active sessions (admin)
echo -e "${GREEN}TEST 7: Get All Sessions${NC}"
data=$(cat <<EOF
{
    "api_key": "$KASM_API_KEY",
    "api_key_secret": "$KASM_API_SECRET"
}
EOF
)
make_request "/api/public/get_kasms" "$data" "Get all active sessions"

echo -e "${GREEN}Testing complete!${NC}"
echo ""
echo "Summary:"
echo "- If Tests 1, 2, 6, 7 work but Tests 3, 4, 5 fail with HTML responses,"
echo "  then the issue is specific to session creation."
echo "- Check the HTML error messages for clues about what's wrong."
echo "- Common issues include:"
echo "  * Invalid or non-existent image_id/image_name"
echo "  * User doesn't have permission to create sessions"
echo "  * Group ID is invalid or user is not in the group"
echo "  * Session limits have been reached"
echo ""
