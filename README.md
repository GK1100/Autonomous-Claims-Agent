# Autonomous Insurance Claims Processing Agent

An enterprise-grade, agentic AI pipeline that autonomously processes First Notice of Loss (FNOL) insurance claims. 

Built on **LangGraph**, this system orchestrates a Directed Acyclic Graph (DAG) of specialized nodes to ingest documents, perform robust LLM-based data extraction, apply deterministic business validation rules, and intelligent claim routing—all outputting to a structured JSON format.

## ✨ Key Features
- **LangGraph Orchestration**: Replaces fragile linear scripts with a resilient, state-driven workflow (`Ingestion → Extraction → Validation → Decision → Audit`).
- **Model-Agnostic Extraction**: Uses `PydanticOutputParser` to ensure perfect JSON extraction across **any** LLM provider (including free/rate-limited models via OpenRouter) without relying on brittle API-level function calling.
- **Controlled Autonomy**: Automatically triggers a fallback/retry loop if the LLM misses critical fields during the first extraction pass.
- **Deterministic Business Logic**: Decouples LLM hallucination risk from critical business logic. Uses hardcoded Python validation for amount thresholds, required fields, and rule-based routing.
- **Automated Auditing**: Recursively tracks all missing/null fields and generates a comprehensive `_result.json` audit report for every processed claim.

---

## 🚀 Quick Start

### 1. Environment Setup
Create a virtual environment and install the required dependencies:
```bash
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure API Keys
This project uses **OpenRouter** to access LLMs securely and affordably. 
Create a `.env` file in the root directory and add your key:
```env
OPENROUTER_API_KEY=your_openrouter_key_here
```
*(By default, the system uses `openai/gpt-oss-120b:free` or `z-ai/glm-4.5-air:free`. You can easily swap this out for `openai/gpt-4o-mini` or `anthropic/claude-3-haiku` in `src/graph/nodes.py`)*

### 3. Run the Agent
To process all `.txt` FNOL documents located in the `data/input/` folder automatically:
```bash
python -m src.orchestrator
```

To process a specific file directly via the command line:
```bash
python -m src.orchestrator path/to/your/document.txt
```

---

## 📂 Project Structure

```text
├── data/
│   ├── input/                # Place raw FNOL .txt or .pdf files here
│   └── output/               # Generated JSON audit reports are saved here
├── src/
│   ├── models.py             # Pydantic schemas (ClaimData, ValidationResult)
│   ├── orchestrator.py       # Main CLI entry point
│   └── graph/
│       ├── state.py          # TypedDict defining the LangGraph state
│       ├── workflow.py       # LangGraph DAG compilation and edge routing
│       ├── nodes.py          # The core logic for each graph node
│       └── utils.py          # Pure, deterministic validation & routing rules
├── requirements.txt
└── README.md
```

---

## 📊 Output Format
After processing, the final audit JSON is saved to `data/output/<filename>_result.json` and perfectly matches the specification:

```json
{
  "extractedFields": { ... },
  "missingFields": [
    "damage.description",
    "other_party",
    "injuries",
    "witnesses"
  ],
  "recommendedRoute": "AUTO_APPROVE",
  "reasoning": "RULE_02_AMOUNT -> LOW"
}
```
