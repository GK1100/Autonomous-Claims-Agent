#!/usr/bin/env python3
"""
Build script for Render deployment
"""
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a shell command and handle errors"""
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"ERROR: Command failed with exit code {result.returncode}")
        sys.exit(1)
    
    return result

def main():
    print("=" * 60)
    print("Starting Render Build Process")
    print("=" * 60)
    
    # Install Python dependencies
    print("\n[1/3] Installing Python dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Check Node.js
    print("\n[2/3] Checking Node.js...")
    try:
        result = run_command("node --version")
        print(f"Node.js version: {result.stdout.strip()}")
        result = run_command("npm --version")
        print(f"NPM version: {result.stdout.strip()}")
    except:
        print("ERROR: Node.js not found!")
        sys.exit(1)
    
    # Build frontend
    print("\n[3/3] Building frontend...")
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("ERROR: frontend directory not found!")
        sys.exit(1)
    
    run_command("npm install", cwd=str(frontend_dir))
    run_command("npm run build", cwd=str(frontend_dir))
    
    # Verify build
    dist_dir = frontend_dir / "dist"
    index_html = dist_dir / "index.html"
    
    if not dist_dir.exists():
        print("ERROR: dist directory was not created!")
        sys.exit(1)
    
    if not index_html.exists():
        print("ERROR: index.html was not created!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ Build completed successfully!")
    print("=" * 60)
    
    # List dist contents
    print("\nDist directory contents:")
    for item in dist_dir.rglob("*"):
        if item.is_file():
            print(f"  - {item.relative_to(dist_dir)}")

if __name__ == "__main__":
    main()
