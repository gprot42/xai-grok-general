#!/bin/bash
# Test script to verify XAI_API_KEY loading from environment and .env file

echo "=================================="
echo "Testing XAI_API_KEY Configuration"
echo "=================================="
echo ""

# Test 1: Check if .env file exists
echo "Test 1: Checking for .env file..."
if [ -f ".env" ]; then
    echo "✓ .env file found in current directory"
    if grep -q "XAI_API_KEY=" .env; then
        echo "✓ XAI_API_KEY variable found in .env"
    else
        echo "⚠ XAI_API_KEY not found in .env file"
    fi
elif [ -f "../.env" ]; then
    echo "✓ .env file found in parent directory"
    if grep -q "XAI_API_KEY=" ../.env; then
        echo "✓ XAI_API_KEY variable found in ../.env"
    else
        echo "⚠ XAI_API_KEY not found in ../.env file"
    fi
else
    echo "⚠ No .env file found"
fi
echo ""

# Test 2: Check shell environment variable
echo "Test 2: Checking shell environment variable..."
if [ -n "$XAI_API_KEY" ]; then
    key_preview="${XAI_API_KEY:0:8}..."
    echo "✓ XAI_API_KEY is set in shell environment: $key_preview"
else
    echo "⚠ XAI_API_KEY is not set in shell environment"
    echo "  You can set it with: export XAI_API_KEY='your-key-here'"
fi
echo ""

# Test 3: Try running the script to see if it can find the key
echo "Test 3: Testing Python script initialization..."
echo "Running: python3 imagine.py --help"
echo ""
python3 imagine.py --help
echo ""

# Summary
echo "=================================="
echo "Configuration Summary"
echo "=================================="
echo ""
echo "The script will load XAI_API_KEY in this order:"
echo "  1. From shell environment (export XAI_API_KEY=...)"
echo "  2. From .env file in script directory (./grok-imagine/.env)"
echo "  3. From .env file in parent directory (./grok-general/.env)"
echo ""
echo "To set up your API key, choose ONE of these methods:"
echo ""
echo "Method 1 - Shell Environment Variable (temporary):"
echo "  export XAI_API_KEY='your-api-key-here'"
echo ""
echo "Method 2 - .env file (recommended, persistent):"
echo "  cp ../.env.example ../.env"
echo "  # Then edit ../.env and add your key"
echo ""
echo "Get your API key from: https://console.x.ai/"
echo ""
