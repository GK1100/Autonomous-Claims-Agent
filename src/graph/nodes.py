import os
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from langchain_openrouter import ChatOpenRouter
from src.graph.state import ClaimState
from src.models import ClaimData, ValidationResult, DecisionResult
from src.graph.utils import (
    check_required_fields,
    check_dates,
    check_amount,
    count_fields,
    compute_quality_score,
    RECOVERABLE_FIELDS
)

# ──────────────────────────────────────────────
# 1. Ingestion Node
# ──────────────────────────────────────────────
def ingestion_node(state: ClaimState) -> ClaimState:
    path = Path(state["file_path"])
    if not path.exists():
        return {"errors": [f"File not found: {path}"]}
    
    raw_text = path.read_text(encoding="utf-8")
    doc_type = "ACORD_AUTO_LOSS" if "ACORD" in raw_text.upper() else "UNKNOWN"
    
    return {
        "raw_text": raw_text,
        "doc_type": doc_type,
        "audit_trail": [f"Ingested {path.name} ({len(raw_text)} chars)"]
    }

# ──────────────────────────────────────────────
# 2. Extraction Node
# ──────────────────────────────────────────────

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

EXTRACTION_PROMPT = """You are a precise insurance document parser. Extract ALL fields from the following ACORD Automobile Loss Notice into a structured format.

RULES:
1. Use null for any field that is not present in the document.
2. For estimated_amount, return the numeric value only (e.g., 45000).
3. Extract the accident/loss description verbatim from the document.

{format_instructions}

DOCUMENT:
{document}
"""

RETRY_SUFFIX = """
IMPORTANT: The previous extraction attempt missed these critical fields: {missing_fields}.
Please search the document thoroughly for these specific fields.
"""

def extraction_node(state: ClaimState) -> ClaimState:
    llm = ChatOpenRouter(
        model="openai/gpt-oss-120b:free",
        temperature=0,
    )
    
    parser = PydanticOutputParser(pydantic_object=ClaimData)
    
    prompt_text = EXTRACTION_PROMPT
    if state.get("missing_fields_to_retry") and state.get("extraction_attempts", 0) > 0:
        prompt_text += RETRY_SUFFIX.format(missing_fields=", ".join(state["missing_fields_to_retry"]))
        
    prompt = PromptTemplate(
        template=prompt_text,
        input_variables=["document"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    
    try:
        claim_data = chain.invoke({"document": state["raw_text"]})
        # Compute confidence based on populated fields (simplified)
        data_dict = claim_data.model_dump()
        populated = sum(1 for v in data_dict.values() if v is not None)
        confidence = min(1.0, populated / 10.0)
        
        return {
            "claim_data": claim_data,
            "extraction_attempts": state.get("extraction_attempts", 0) + 1,
            "extraction_confidence": confidence,
            "audit_trail": [f"Extraction attempt {state.get('extraction_attempts', 0) + 1} completed (conf: {confidence:.2f})"]
        }
    except Exception as e:
        import traceback
        return {
            "errors": [f"LLM Extraction failed: {str(e)}"],
            "extraction_attempts": state.get("extraction_attempts", 0) + 1
        }

# ──────────────────────────────────────────────
# 3. Validation Node
# ──────────────────────────────────────────────
def validation_node(state: ClaimState) -> ClaimState:
    if not state.get("claim_data"):
        return {"errors": ["No claim data to validate"]}
    
    flags, warnings, missing = [], [], []
    claim_data = state['claim_data']
    
    check_required_fields(claim_data, flags, missing)
    check_dates(claim_data, flags, warnings)
    check_amount(claim_data, flags, warnings)
    
    recoverable_fields = [f for f in missing if f in RECOVERABLE_FIELDS]
    
    field_count = count_fields(claim_data)
    quality = compute_quality_score(field_count, len(flags), len(warnings))
    
    val_result = ValidationResult(
        is_valid=len(flags)==0,
        flags=flags,
        warnings=warnings,
        field_count=field_count,
        missing_fields=missing
    )
    
    return {
        "validation_result": val_result,
        "quality_score": quality,
        "missing_fields_to_retry": recoverable_fields,
        "audit_trail": [f"Validation completed (valid: {val_result.is_valid}, flags: {len(flags)})"]
    }

# ──────────────────────────────────────────────
# 4. Decision Node
# ──────────────────────────────────────────────
def decision_node(state: ClaimState) -> ClaimState:
    claim = state.get("claim_data")
    val = state.get("validation_result")
    
    reasoning, rules, escalation = [], [], []
    
    if not claim or not val or not val.is_valid:
        severity, route = "FLAGGED", "MANUAL_INVESTIGATION"
        rules.append("RULE_01_VALIDATION_FLAGS_OR_MISSING_DATA")
    else:
        amt = claim.damage.estimated_amount if claim.damage and claim.damage.estimated_amount else 0
        if amt < 25000:
            severity, route = "LOW", "AUTO_APPROVE"
            rules.append("RULE_02_AMOUNT -> LOW")
        else:
            severity, route = "HIGH", "SENIOR_ADJUSTER"
            rules.append("RULE_02_AMOUNT -> HIGH")
            
        if claim.injuries:
            severity, route = "HIGH", "SENIOR_ADJUSTER"
            rules.append("RULE_03_INJURY -> HIGH")
            escalation.append("INJURY -> HIGH")
            
    dec_result = DecisionResult(
        severity=severity, 
        route=route, 
        confidence=state.get("quality_score", 0.0), 
        reasoning=reasoning
    )
    
    return {
        "decision_result": dec_result,
        "rules_applied": rules,
        "escalation_chain": escalation,
        "audit_trail": [f"Decision: {severity} -> {route}"]
    }

import json

# ──────────────────────────────────────────────
# 5. Audit Node
# ──────────────────────────────────────────────
def audit_node(state: ClaimState) -> ClaimState:
    report_id = f"CLM-{uuid4().hex[:8].upper()}"
    
    # Format the exact required output
    claim_data = state.get("claim_data")
    extracted_fields = claim_data.model_dump() if claim_data else {}
    
    val_result = state.get("validation_result")
    missing_fields = val_result.missing_fields.copy() if val_result else []
    
    # Recursively find all None/null fields to include in missingFields
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
                # If a list (like injuries/witnesses) is explicitly empty
                if prefix not in missing_fields:
                    missing_fields.append(prefix)
            else:
                for i, item in enumerate(data):
                    find_missing(item, f"{prefix}[{i}]")
                    
    find_missing(extracted_fields)
    
    dec_result = state.get("decision_result")
    recommended_route = dec_result.route if dec_result else "UNKNOWN"
    
    rules = state.get("rules_applied", [])
    reasoning = " | ".join(rules) if rules else "Failed to parse document"
    
    output_json = {
        "extractedFields": extracted_fields,
        "missingFields": missing_fields,
        "recommendedRoute": recommended_route,
        "reasoning": reasoning
    }
    
    # Save to output/ directory
    output_dir = Path("data/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    input_path = Path(state["file_path"])
    output_file = output_dir / f"{input_path.stem}_result.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_json, f, indent=2)
        
    return {
        "final_report_id": report_id,
        "audit_trail": [f"Generated report {report_id}", f"Saved JSON to {output_file}"]
    }
