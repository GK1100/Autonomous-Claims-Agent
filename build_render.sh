#!/bin/bash
set -e

echo "=== Installing Python dependencies ==="
pip install -r requirements.txt

echo "=== Checking Node.js availability ==="
if ! command -v node &> /dev/null; then
    echo "Node.js not found. Installing..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt-get install -y nodejs
fi

echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

echo "=== Building frontend ==="
cd frontend
npm install
npm run build
cd ..

echo "=== Verifying build ==="
if [ -f "frontend/dist/index.html" ]; then
    echo "✓ Frontend built successfully"
    ls -la frontend/dist/
else
    echo "✗ Frontend build failed - index.html not found"
    exit 1
fi

echo "=== Build complete ==="
