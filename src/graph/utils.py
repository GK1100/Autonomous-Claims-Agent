import re
from datetime import datetime
from src.models import ClaimData

# ──────────────────────────────────────────────
# Configuration & Constants
# ──────────────────────────────────────────────
MAX_CLAIM_AMOUNT = 5_000_000
MIN_CLAIM_AMOUNT = 0
VIN_LENGTH = 17
PHONE_PATTERN = re.compile(r"^\d{10}$")
DATE_FORMATS = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d"]
RECOVERABLE_FIELDS = {"damage.estimated_amount", "loss.date_of_loss", "insured.name"}

# ──────────────────────────────────────────────
# Validation Logic
# ──────────────────────────────────────────────
def check_required_fields(claim: ClaimData, flags: list[str], missing: list[str]) -> None:
    if not claim.policy.policy_number:
        flags.append("MISSING_POLICY_NUMBER")
        missing.append("policy.policy_number")
    if not claim.loss.date_of_loss:
        flags.append("MISSING_DATE_OF_LOSS")
        missing.append("loss.date_of_loss")
    if not claim.insured.name:
        flags.append("MISSING_INSURED_NAME")
        missing.append("insured.name")
    if not claim.damage:
        flags.append("MISSING_DAMAGE_DETAILS")
        missing.append("damage")

def _parse_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def check_dates(claim: ClaimData, flags: list[str], warnings: list[str]) -> None:
    date_of_loss = _parse_date(claim.loss.date_of_loss)
    date_of_report = _parse_date(claim.policy.date_of_report if claim.policy else None)
    today = datetime.now()
    if date_of_loss and date_of_report and date_of_loss > date_of_report:
        flags.append("DATE_INCONSISTENCY_LOSS_AFTER_REPORT")
    if date_of_report and date_of_report > today:
        warnings.append("FUTURE_REPORT_DATE")
    if date_of_loss and date_of_loss > today:
        flags.append("FUTURE_LOSS_DATE")

def check_amount(claim: ClaimData, flags: list[str], warnings: list[str]) -> None:
    if claim.damage and claim.damage.estimated_amount is not None:
        amount = claim.damage.estimated_amount
        if amount <= MIN_CLAIM_AMOUNT:
            flags.append("INVALID_AMOUNT_ZERO_OR_NEGATIVE")
        if amount > MAX_CLAIM_AMOUNT:
            flags.append("AMOUNT_SUSPICIOUS_EXCEEDS_THRESHOLD")
            warnings.append(f"Amount Rs.{amount:,.0f} exceeds Rs.{MAX_CLAIM_AMOUNT:,.0f}")

def count_fields(claim: ClaimData) -> int:
    data = claim.model_dump()
    def _count(obj) -> int:
        total = 0
        if isinstance(obj, dict):
            for v in obj.values():
                if v is not None:
                    total += _count(v) if isinstance(v, (dict, list)) else 1
        elif isinstance(obj, list):
            for item in obj:
                total += _count(item)
        return total
    return _count(data)

def compute_quality_score(field_count: int, flag_count: int, warning_count: int) -> float:
    base = 0.95
    base -= flag_count * 0.12
    base -= warning_count * 0.03
    if field_count >= 30:
        base += 0.03
    elif field_count < 15:
        base -= 0.10
    return max(0.0, min(1.0, round(base, 2)))
