import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from src.graph.workflow import build_claim_graph

PROJECT_ROOT = Path(__file__).parent.parent
DATA_INPUT = PROJECT_ROOT / "data" / "input"
console = Console()

def main():
    load_dotenv(PROJECT_ROOT / ".env")
    if not os.getenv("OPENROUTER_API_KEY"):
        console.print("[bold red]ERROR:[/] OPENROUTER_API_KEY not found in .env")
        sys.exit(1)

    app = build_claim_graph()
    
    if len(sys.argv) > 1:
        # Use files provided via command line arguments
        txt_files = [Path(arg) for arg in sys.argv[1:]]
    else:
        # Fallback to data/input directory
        txt_files = list(DATA_INPUT.glob("*.txt"))
        
    if not txt_files:
        console.print("[bold red]ERROR:[/] No input files provided.")
        console.print("Usage: [bold cyan]python -m src.orchestrator path/to/document.txt[/]")
        sys.exit(1)

    for f in txt_files:
        if not f.exists():
            console.print(f"[bold red]ERROR:[/] File not found: {f}")
            continue
            
        console.print(f"\n[bold cyan]🤖 LangGraph Claims Agent — Processing[/]")
        console.print(f"[dim]   File: {f.name}[/]")
        console.print("[dim]─" * 65 + "[/]")
        
        initial_state = {
            "file_path": str(f),
            "extraction_attempts": 0,
            "missing_fields_to_retry": [],
            "audit_trail": [],
            "errors": []
        }
        
        # Run the LangGraph
        for s in app.stream(initial_state):
            # Print node outputs as they stream
            for node_name, state_update in s.items():
                console.print(f"[bold yellow]▶ Node:[/] {node_name}")
                if "audit_trail" in state_update and state_update["audit_trail"]:
                    for msg in state_update["audit_trail"]:
                        console.print(f"  [green]✓[/] {msg}")
                if "errors" in state_update and state_update["errors"]:
                    for err in state_update["errors"]:
                        console.print(f"  [red]✗[/] {err}")
        
        console.print("\n[bold green]✅ Processing Complete![/]\n")

if __name__ == "__main__":
    main()
