#!/bin/bash
# Test script for JupyterLite + Jupytext integration
# Run from the root of the jupytext repository

set -e

echo "🧪 Testing Jupytext JupyterLite Integration"
echo ""

# Check if we're in the right directory
if [ ! -d "jupyterlab/packages/jupyterlite-jupytext" ]; then
    echo "❌ Error: Run this script from the root of the jupytext repository"
    exit 1
fi

# Check if requirements are installed
echo "📋 Checking requirements..."
if ! command -v jupyter &> /dev/null; then
    echo "❌ Error: jupyter not found. Install with: pip install -r demo/jupyterlite-example/requirements.txt"
    exit 1
fi

if ! command -v jlpm &> /dev/null; then
    echo "❌ Error: jlpm not found. Install with: npm install -g yarn"
    exit 1
fi

echo "✅ Requirements check passed"
echo ""

# Build the extension
echo "🔧 Building Jupytext JupyterLite extension..."
cd jupyterlab/packages/jupyterlite-jupytext
jlpm install
jlpm build
cd ../../..
echo "✅ Extension built"
echo ""

# Build the demo site
echo "🌐 Building JupyterLite demo site..."
cd demo/jupyterlite-example
jupyter lite build --contents notebooks/
echo "✅ Demo site built"
echo ""

# Instructions
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ Build complete!"
echo ""
echo "To test locally, run:"
echo "  cd demo/jupyterlite-example"
echo "  jupyter lite serve"
echo ""
echo "Then open http://localhost:8000 in your browser"
echo "and try opening 'welcome.py' as a notebook!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
