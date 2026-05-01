@echo off

REM Local development startup script for Windows

echo Starting Claims Processing Agent...

REM Check if frontend is built
if not exist "frontend\dist" (
    echo Frontend not built. Building now...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

REM Start the server
echo Starting FastAPI server...
uvicorn src.orchestrator:app --reload --host 0.0.0.0 --port 8000
