from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path
from uuid import uuid4

# Add the parent directory to sys.path so we can import src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.workflow import build_claim_graph

app = FastAPI(title="Claims Processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_claim_graph()

@app.get("/api")
@app.get("/api/process")
async def api_status():
    return {"status": "ok", "message": "API is running. Send a POST request to /api/process with a 'file' payload to process a claim."}

@app.post("/api/process")
async def process_claim(file: UploadFile = File(...)):
    if not file.filename.endswith('.txt'):
        raise HTTPException(status_code=400, detail="Only text (.txt) files are supported")
    
    content = await file.read()
    temp_dir = Path("/tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"{uuid4().hex}.txt"
    
    try:
        temp_path.write_text(content.decode("utf-8"), encoding="utf-8")
        
        # Run graph
        state = {"file_path": str(temp_path)}
        final_state = graph.invoke(state)
        
        # Extract output JSON logic
        claim_data = final_state.get("claim_data")
        extracted_fields = claim_data.model_dump() if claim_data else {}
        
        val_result = final_state.get("validation_result")
        missing_fields = val_result.missing_fields.copy() if val_result else []
        
        # We also want the recursive missing fields logic here:
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
            "reasoning": " | ".join(final_state.get("rules_applied", [])) if final_state.get("rules_applied") else "Failed to parse document"
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path.exists():
            temp_path.unlink()
