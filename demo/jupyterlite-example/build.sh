#!/bin/bash
# Build script for JupyterLite demo with local Jupytext extension
# Uses pixi for package management

set -e  # Exit on error

echo "🔧 Building Jupytext extension for JupyterLite..."

# Check if we're in a pixi environment
if [ -z "$PIXI_PROJECT_ROOT" ]; then
    echo "⚠️  Not in a pixi environment. Run 'pixi shell' first or use 'pixi run build-jupyterlite'"
    exit 1
fi

cd ../../jupyterlab/packages/jupyterlite-jupytext

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing extension dependencies..."
    jlpm install
fi

# Build the extension
echo "🏗️  Building extension..."
jlpm build

cd -

echo ""
echo "🌐 Building JupyterLite site..."
jupyter lite build --contents notebooks/

echo ""
echo "✅ Build complete!"
echo ""
echo "To preview locally, run:"
echo "  jupyter lite serve"
echo ""
echo "Then open http://localhost:8000 in your browser"

