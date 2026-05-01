
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

# ✅ Safer path handling (Vercel compatible)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_INPUT = PROJECT_ROOT / "data" / "input"

# ✅ Load environment variables globally (VERY IMPORTANT)
load_dotenv(PROJECT_ROOT / ".env")

# ✅ Initialize FastAPI App
app = FastAPI(title="Claims Processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Lazy graph initialization (prevents cold start crash)
graph = None

def get_graph():
    global graph
    if graph is None:
        graph = build_claim_graph()
    return graph

# ✅ Health check routes
@app.get("/")
@app.get("/api")
async def api_status():
    return {
        "status": "ok",
        "message": "API is running. Use POST /api/process to upload file."
    }

# ✅ Main API endpoint
@app.post("/api/process")
async def process_claim(file: UploadFile = File(...)):
    try:
        # Validate file
        if not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files supported")

        # Check API key
        if not os.getenv("OPENROUTER_API_KEY"):
            raise HTTPException(status_code=500, detail="Missing OPENROUTER_API_KEY")

        # Save file temporarily (Vercel uses /tmp)
        content = await file.read()
        temp_dir = Path("/tmp")
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_path = temp_dir / f"{uuid4().hex}.txt"
        temp_path.write_text(content.decode("utf-8"), encoding="utf-8")

        # Run graph
        graph = get_graph()

        state = {
            "file_path": str(temp_path),
            "extraction_attempts": 0,
            "missing_fields_to_retry": [],
            "audit_trail": [],
            "errors": []
        }

        final_state = graph.invoke(state)

        # Extract outputs
        claim_data = final_state.get("claim_data")
        extracted_fields = claim_data.model_dump() if claim_data else {}

        val_result = final_state.get("validation_result")
        missing_fields = val_result.missing_fields.copy() if val_result else []

        # Recursive missing field detection
        def find_missing(data, prefix=""):
            if isinstance(data, dict):
                for k, v in data.items():
                    path = f"{prefix}.{k}" if prefix else k
                    if v is None:
                        if path not in missing_fields:
                            missing_fields.append(path)
                    elif isinstance(v, (dict, list)):
                        find_missing(v, path)
            elif isinstance(data, list):
                if len(data) == 0:
                    if prefix not in missing_fields:
                        missing_fields.append(prefix)
                else:
                    for i, item in enumerate(data):
                        find_missing(item, f"{prefix}[{i}]")

        find_missing(extracted_fields)

        dec_result = final_state.get("decision_result")

        return {
            "extractedFields": extracted_fields,
            "missingFields": missing_fields,
            "recommendedRoute": dec_result.route if dec_result else "UNKNOWN",
            "reasoning": " | ".join(final_state.get("rules_applied", [])) if final_state.get("rules_applied") else "Processing completed"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if 'temp_path' in locals() and temp_path.exists():
            temp_path.unlink()

# --- CLI fallback (still works locally) ---
def main():
    from rich.console import Console
    console = Console()

    if not os.getenv("OPENROUTER_API_KEY"):
        console.print("[bold red]ERROR:[/] OPENROUTER_API_KEY not found in .env")
        sys.exit(1)

    if len(sys.argv) > 1:
        txt_files = [Path(arg) for arg in sys.argv[1:]]
    else:
        txt_files = list(DATA_INPUT.glob("*.txt"))

    if not txt_files:
        console.print("[bold red]ERROR:[/] No input files provided.")
        sys.exit(1)

    graph = get_graph()

    for f in txt_files:
        if not f.exists():
            console.print(f"[bold red]ERROR:[/] File not found: {f}")
            continue

        console.print(f"\nProcessing: {f.name}")

        state = {
            "file_path": str(f),
            "extraction_attempts": 0,
            "missing_fields_to_retry": [],
            "audit_trail": [],
            "errors": []
        }

        graph.invoke(state)

    console.print("\n✅ Done!")

if __name__ == "__main__":
    main()

