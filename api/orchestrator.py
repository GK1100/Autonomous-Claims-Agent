import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import os
from pathlib import Path
from dotenv import load_dotenv
from uuid import uuid4

# FastAPI imports
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.graph.workflow import build_claim_graph

# Safer path handling (Vercel compatible)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_INPUT = PROJECT_ROOT / "data" / "input"

# Load environment variables globally
load_dotenv(PROJECT_ROOT / ".env")

# Initialize FastAPI App
app = FastAPI(title="Claims Processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = None

def get_graph():
    global graph
    if graph is None:
        graph = build_claim_graph()
    return graph

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# Add more endpoints as needed, or import from src/orchestrator.py
