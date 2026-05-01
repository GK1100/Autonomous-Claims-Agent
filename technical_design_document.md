# Autonomous Claims Processing Agent
## Decision Intelligence Layer — Technical Design Document

---

## 1. System Architecture (Agent Workflow)

The system operates as an **autonomous agent pipeline** that takes raw insurance claim documents (ACORD forms), extracts structured data, validates it, makes routing decisions, and produces human-readable explanations — all without human intervention.

### End-to-End Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  📄 INPUT     │───▶│  🤖 EXTRACT  │───▶│  ✅ VALIDATE │───▶│  🧠 DECIDE   │───▶│  📊 OUTPUT   │
│  Raw Claim    │    │  LLM Parsing │    │  Data QA     │    │  Rule Engine │    │  JSON + Log  │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Step-by-Step Breakdown

| Step | Component | What Happens | Agent Behavior |
|------|-----------|-------------|----------------|
| **1** | **Document Ingestion** | Raw ACORD text file is loaded from `data/input/` | Agent senses its environment (file system) |
| **2** | **LLM Extraction** | Google Gemini parses unstructured text → structured JSON | Agent reasons over noisy input |
| **3** | **Schema Validation** | Pydantic models enforce data types, required fields, value ranges | Agent self-checks its own work |
| **4** | **Decision Engine** | Rule-based logic evaluates claim severity, flags, and routing | Agent acts on validated data |
| **5** | **Reasoning Generator** | Human-readable explanations are produced for every decision | Agent explains itself |
| **6** | **Output Generation** | Final JSON report + console summary written to `data/output/` | Agent produces actionable output |

### Why It Behaves Like an Autonomous Agent

- **No human in the loop** — end-to-end processing without manual steps
- **Perception** — reads and interprets unstructured documents
- **Reasoning** — applies both LLM intelligence and deterministic rules
- **Action** — routes claims and generates reports autonomously
- **Explainability** — every decision comes with a traceable rationale

---

## 2. Technology Stack (Justification-Based)

| Component | Technology | Why This Choice |
|-----------|-----------|----------------|
| **Language** | Python 3.12 | Industry standard for AI/ML pipelines; rich ecosystem for data processing |
| **LLM Provider** | Google Gemini (via `google-generativeai`) | Fast, cost-effective structured output; excellent at form/document parsing |
| **Data Validation** | Pydantic v2 | Compile-time schema enforcement with automatic error messages; zero boilerplate |
| **Configuration** | python-dotenv | Secure API key management; keeps secrets out of code |
| **CLI Output** | Rich | Professional terminal output with tables, colors, and progress indicators |
| **Data Format** | JSON | Universal interchange format; human-readable and machine-parseable |

### Why NOT Other Choices

| Avoided | Reason |
|---------|--------|
| LangChain / LlamaIndex | Overkill for a single-agent pipeline; adds unnecessary abstraction |
| Database (SQLite/Postgres) | File-based I/O is sufficient for document processing; simpler deployment |
| FastAPI / Flask | No API needed — this is a batch processing agent, not a web service |

---

## 3. Project Structure (Engineering Clarity)

```
ACORD/
├── venv/                          # Python virtual environment
├── data/
│   ├── input/                     # Raw ACORD claim documents (.txt)
│   │   └── acord_text_document1.txt
│   └── output/                    # Processed results (.json)
│       └── claim_result_001.json
├── src/
│   ├── __init__.py
│   ├── main.py                    # 🎯 Entry point — orchestrates the full pipeline
│   ├── extractor.py               # 🤖 LLM-powered document parsing (Gemini)
│   ├── models.py                  # 📐 Pydantic schemas for all claim data
│   ├── validator.py               # ✅ Data quality checks & business rules
│   ├── decision_engine.py         # 🧠 Rule-based routing & severity classification
│   └── reasoning.py               # 💬 Human-readable explanation generator
├── .env                           # API keys (gitignored)
├── .gitignore
├── requirements.txt               # Pinned dependencies
├── technical_design_document.md   # This document
└── README.md                      # Quick-start guide
```

### Module Responsibilities

| Module | Single Responsibility |
|--------|-----------------------|
| `main.py` | Pipeline orchestration — calls each module in sequence, handles errors |
| `extractor.py` | Takes raw text → calls Gemini → returns structured dict |
| `models.py` | Defines `ClaimData`, `VehicleInfo`, `InjuryInfo`, `DecisionResult` schemas |
| `validator.py` | Runs field-level checks (missing data, invalid dates, amount thresholds) |
| `decision_engine.py` | Applies deterministic rules to produce routing decision + severity score |
| `reasoning.py` | Converts decision metadata into plain-English explanation strings |

### Design Principles

- **Single Responsibility** — each file does exactly one thing
- **No Circular Dependencies** — data flows in one direction: `main → extractor → models → validator → decision_engine → reasoning`
- **Testable in Isolation** — every module can be unit-tested independently
- **Config-Driven** — thresholds and rules are constants, not hardcoded magic numbers

---

## 4. Core Logic (Intelligence Layer)

### 4.1 Extraction (LLM Role)

The extractor sends the raw ACORD text to **Google Gemini** with a structured prompt that instructs the model to return a JSON object matching our Pydantic schema.

```python
# Simplified extraction flow
prompt = f"""
Extract all fields from this ACORD claim document into structured JSON.
Return EXACTLY this schema: {schema_template}

Document:
{raw_text}
"""
response = model.generate_content(prompt)
claim_data = json.loads(response.text)
```

**Key design decisions:**
- Schema is provided in the prompt → forces consistent output structure
- JSON output mode is used when available → eliminates markdown wrapping issues
- Fallback regex parsing handles edge cases where LLM output is malformed

### 4.2 Validation (Data Quality Checks)

After extraction, every field passes through validation:

| Check | Rule | Action on Failure |
|-------|------|-------------------|
| **Required Fields** | `policy_number`, `date_of_loss`, `insured_name` must exist | Flag as `INCOMPLETE` |
| **Date Sanity** | `date_of_loss` ≤ `date_of_report` ≤ today | Flag as `DATE_ERROR` |
| **Amount Range** | `estimated_amount` > 0 and < ₹50,00,000 | Flag as `AMOUNT_SUSPICIOUS` |
| **VIN Format** | VIN must be 17 alphanumeric characters | Flag as `VIN_INVALID` |
| **Phone Format** | Phone numbers must be 10 digits | Flag as `CONTACT_INVALID` |

```python
# Example validation
def validate_claim(claim: ClaimData) -> list[str]:
    flags = []
    if not claim.policy_number:
        flags.append("MISSING_POLICY_NUMBER")
    if claim.estimated_amount and claim.estimated_amount > 5000000:
        flags.append("AMOUNT_SUSPICIOUS")
    if claim.date_of_loss and claim.date_of_report:
        if claim.date_of_loss > claim.date_of_report:
            flags.append("DATE_INCONSISTENCY")
    return flags
```

### 4.3 Decision Engine (Rule-Based Routing)

The decision engine classifies each claim into a **severity tier** and assigns a **routing destination**.

```
┌─────────────────────────────────────────────────────┐
│                  DECISION MATRIX                     │
├─────────────┬───────────────┬───────────────────────┤
│  Condition  │  Severity     │  Route To             │
├─────────────┼───────────────┼───────────────────────┤
│ Amount < ₹25K AND no injury │  LOW        │  Auto-Approve         │
│ Amount ₹25K–₹2L             │  MEDIUM     │  Standard Review      │
│ Amount > ₹2L OR has injury  │  HIGH       │  Senior Adjuster      │
│ Any validation flag          │  FLAGGED    │  Manual Investigation │
│ Police report present        │  +1 tier    │  Escalation bonus     │
└─────────────┴───────────────┴───────────────────────┘
```

```python
# Core decision logic
def decide(claim: ClaimData, flags: list[str]) -> DecisionResult:
    if flags:
        return DecisionResult(
            severity="FLAGGED",
            route="MANUAL_INVESTIGATION",
            confidence=0.6
        )
    
    amount = claim.estimated_amount or 0
    has_injury = claim.injury_details is not None
    
    if amount < 25000 and not has_injury:
        severity, route = "LOW", "AUTO_APPROVE"
    elif amount <= 200000:
        severity, route = "MEDIUM", "STANDARD_REVIEW"
    else:
        severity, route = "HIGH", "SENIOR_ADJUSTER"
    
    if has_injury:
        severity = "HIGH"
        route = "SENIOR_ADJUSTER"
    
    if claim.police_report:
        severity = escalate(severity)
    
    return DecisionResult(severity=severity, route=route, confidence=0.95)
```

### 4.4 Reasoning Generator (Explainability)

Every decision is accompanied by a **plain-English explanation** — critical for audit trails and regulatory compliance.

```python
# Example output
{
    "decision": "SENIOR_ADJUSTER",
    "severity": "HIGH",
    "reasoning": [
        "Estimated claim amount is ₹45,000 (within ₹25K–₹2L range → MEDIUM severity)",
        "Minor injury reported (neck strain) → escalated to HIGH severity",
        "Police report filed (BLR2026-778) → routed to Senior Adjuster",
        "All required fields present — no validation flags",
        "Final routing: SENIOR_ADJUSTER with confidence 0.95"
    ]
}
```

**Reasoning is NOT generated by the LLM** — it is deterministically constructed from the decision engine's evaluation path. This ensures:
- ✅ **Consistency** — same input always produces same explanation
- ✅ **Auditability** — every reasoning step maps to a specific rule
- ✅ **No hallucination** — explanations are grounded in actual data

---

## 5. Why This System Stands Out

- **🤖 True Agent Behavior** — Not just an LLM wrapper. The system perceives (reads documents), reasons (validates + decides), acts (routes claims), and explains (generates rationale) — completing the full agent loop.

- **🧠 Hybrid Intelligence** — LLM handles the *hard part* (unstructured text parsing) while deterministic rules handle the *critical part* (routing decisions). Best of both worlds — no hallucinated decisions.

- **🔍 Built-In Explainability** — Every routing decision comes with a traceable, rule-grounded explanation. This is not an afterthought — it's a core architectural pillar.

- **🏗️ Production-Grade Engineering** — Pydantic schemas, modular pipeline, config-driven thresholds, error handling, and clean separation of concerns. This is not a notebook — it's deployable code.

- **⚡ Zero-Overhead Design** — No databases, no API servers, no orchestration frameworks. A single `python main.py` processes a claim end-to-end in seconds. Complexity is added only when justified.

---

> **Bottom Line:** This system demonstrates that an intelligent claims processing agent doesn't need a complex multi-agent framework or a RAG pipeline. A well-architected single-agent pipeline with clean engineering, hybrid intelligence, and built-in explainability is both more practical and more impressive.
