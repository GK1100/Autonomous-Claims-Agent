from typing import TypedDict, Annotated, Optional
import operator
from pydantic import BaseModel
from src.models import ClaimData, ValidationResult, DecisionResult

class ClaimState(TypedDict):
    # Inputs
    file_path: str
    raw_text: Optional[str]
    doc_type: str
    
    # Extraction State
    claim_data: Optional[ClaimData]
    extraction_attempts: int
    missing_fields_to_retry: list[str]
    extraction_confidence: float
    
    # Validation State
    validation_result: Optional[ValidationResult]
    quality_score: float
    
    # Decision State
    decision_result: Optional[DecisionResult]
    rules_applied: list[str]
    escalation_chain: list[str]
    
    # Audit & Tracking State
    final_report_id: Optional[str]
    audit_trail: Annotated[list[str], operator.add]
    errors: Annotated[list[str], operator.add]
