#!/bin/bash
# Simple run script for Grok Imagine
# Usage: ./run.sh [prompt] [options]

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  Grok Imagine - Image Generator"
echo "========================================"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ Error: 'uv' is not installed"
    echo ""
    echo "Install with:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo ""
    echo "Or use Homebrew:"
    echo "  brew install uv"
    exit 1
fi

# Check if .venv exists, if not create it
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Check if dependencies are installed
if [ ! -f ".venv/pyvenv.cfg" ] || ! uv pip list 2>/dev/null | grep -q "requests"; then
    echo "📦 Installing dependencies..."
    uv pip install -r requirements.txt
    echo "✓ Dependencies installed"
    echo ""
fi

# Check for API key
if [ -z "$XAI_API_KEY" ]; then
    if [ ! -f ".env" ] && [ ! -f "../.env" ]; then
        echo "⚠️  Warning: XAI_API_KEY not found"
        echo ""
        echo "Set it with:"
        echo "  export XAI_API_KEY='your-key-here'"
        echo ""
        echo "Or create a .env file:"
        echo "  echo 'XAI_API_KEY=your-key-here' > .env"
        echo ""
        echo "Get your API key from: https://console.x.ai/"
        echo ""
        read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
    fi
fi

# Run the script with all arguments passed through
echo "🚀 Running Grok Imagine..."
echo ""
uv run imagine.py "$@"
