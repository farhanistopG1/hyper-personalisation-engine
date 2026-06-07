#!/bin/bash

# 💀 START HYPER PERSONALISATION N-ORGAN SERVER 💀

echo ""
echo "💀 STARTING HYPER PERSONALISATION N-ORGAN 💀"
echo ""

# Check if we're in the right directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check DEEPSEEK_API_KEY
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  WARNING: DEEPSEEK_API_KEY not set!"
    echo ""
    echo "Set it with:"
    echo "  export DEEPSEEK_API_KEY='your_key_here'"
    echo ""
    echo "Get your key at: https://platform.deepseek.com/"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Add parent directories to PYTHONPATH so imports work
export PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/../..:$PYTHONPATH"

echo "📁 Working directory: $SCRIPT_DIR"
echo "🔧 PYTHONPATH configured for imports"
echo ""

# Start the server
echo "🚀 Starting FastAPI server..."
echo ""
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

echo ""
echo "💀 Server stopped 💀"
echo ""
