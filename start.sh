#!/bin/bash

# Local development startup script

echo "Starting Claims Processing Agent..."

# Check if frontend is built
if [ ! -d "frontend/dist" ]; then
    echo "Frontend not built. Building now..."
    cd frontend
    npm install
    npm run build
    cd ..
fi

# Start the server
echo "Starting FastAPI server..."
uvicorn src.orchestrator:app --reload --host 0.0.0.0 --port 8000
