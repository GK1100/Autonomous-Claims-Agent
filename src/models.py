"""
Pydantic schemas for ACORD claim data.

Defines all data models used across the pipeline:
- ClaimData: Full extracted claim information
- VehicleInfo: Vehicle details (insured + other party)
- InjuryInfo: Injury details for involved persons
- WitnessInfo: Witness contact information
- DecisionResult: Output of the decision engine
- ClaimReport: Final output combining all pipeline stages
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# Sub-Models
# ──────────────────────────────────────────────

class InsuredDetails(BaseModel):
    """Personal details of the insured party."""
    name: str = Field(..., description="Full name of the insured")
    date_of_birth: Optional[str] = Field(None, description="DOB in DD/MM/YYYY format")
    marital_status: Optional[str] = None
    address: Optional[str] = None
    primary_phone: Optional[str] = None
    secondary_phone: Optional[str] = None
    primary_email: Optional[str] = None
    secondary_email: Optional[str] = None


class AgencyDetails(BaseModel):
    """Insurance agency information."""
    agency_name: Optional[str] = None
    agent_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    customer_id: Optional[str] = None


class PolicyDetails(BaseModel):
    """Policy metadata."""
    policy_number: str = Field(..., description="Unique policy identifier")
    carrier: Optional[str] = None
    naic_code: Optional[str] = None
    line_of_business: Optional[str] = None
    date_of_report: Optional[str] = Field(None, description="Date claim was reported")


class LossInformation(BaseModel):
    """Details about the loss event."""
    date_of_loss: str = Field(..., description="Date of the incident")
    time_of_loss: Optional[str] = None
    location: Optional[str] = None
    police_contacted: Optional[bool] = False
    police_report_number: Optional[str] = None
    description: Optional[str] = None


class VehicleInfo(BaseModel):
    """Vehicle details — used for both insured and other party vehicles."""
    vehicle_number: Optional[int] = None
    year: Optional[int] = None
    make: Optional[str] = None
    model: Optional[str] = None
    body_type: Optional[str] = None
    vin: Optional[str] = None
    plate_number: Optional[str] = None
    state: Optional[str] = None
    owner_name: Optional[str] = None
    driver_name: Optional[str] = None
    license_number: Optional[str] = None
    purpose_of_use: Optional[str] = None
    relation_to_insured: Optional[str] = None
    used_with_permission: Optional[bool] = None


class DamageDetails(BaseModel):
    """Damage assessment information."""
    description: Optional[str] = None
    estimated_amount: Optional[float] = Field(None, description="Estimated repair cost in INR")
    where_vehicle_can_be_seen: Optional[str] = None
    when_can_be_seen: Optional[str] = None
    child_seat_installed: Optional[bool] = False
    child_seat_in_use: Optional[bool] = False
    child_seat_damaged: Optional[bool] = False


class OtherPartyInfo(BaseModel):
    """Other vehicle / property involved."""
    vehicle_description: Optional[str] = None
    damage_description: Optional[str] = None
    has_insurance: Optional[bool] = None


class InjuryInfo(BaseModel):
    """Injury information for involved persons."""
    person_name: Optional[str] = None
    age: Optional[int] = None
    extent_of_injury: Optional[str] = None


class WitnessInfo(BaseModel):
    """Witness contact details."""
    name: Optional[str] = None
    phone: Optional[str] = None


# ──────────────────────────────────────────────
# Main Claim Model
# ──────────────────────────────────────────────

class ClaimData(BaseModel):
    """
    Complete structured representation of an ACORD claim document.
    This is the output of the LLM extraction step.
    """
    insured: InsuredDetails
    agency: Optional[AgencyDetails] = None
    policy: PolicyDetails
    loss: LossInformation
    insured_vehicle: Optional[VehicleInfo] = None
    damage: Optional[DamageDetails] = None
    other_party: Optional[OtherPartyInfo] = None
    injuries: Optional[list[InjuryInfo]] = None
    witnesses: Optional[list[WitnessInfo]] = None
    remarks: Optional[str] = None
    declaration: Optional[str] = None


# ──────────────────────────────────────────────
# Decision Output Models
# ──────────────────────────────────────────────

class ValidationResult(BaseModel):
    """Output of the validation step."""
    is_valid: bool = True
    flags: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    field_count: int = 0
    missing_fields: list[str] = Field(default_factory=list)


class DecisionResult(BaseModel):
    """Output of the decision engine."""
    severity: str = Field(..., description="LOW | MEDIUM | HIGH | FLAGGED")
    route: str = Field(..., description="AUTO_APPROVE | STANDARD_REVIEW | SENIOR_ADJUSTER | MANUAL_INVESTIGATION")
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: list[str] = Field(default_factory=list)


class ClaimReport(BaseModel):
    """
    Final pipeline output — combines extraction, validation, and decision.
    This is what gets written to the output JSON file.
    """
    claim_id: str
    processed_at: str
    source_file: str
    extracted_data: ClaimData
    validation: ValidationResult
    decision: DecisionResult
