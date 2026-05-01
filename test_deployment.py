"""
Simple test script to verify deployment setup
Run this locally before deploying to catch issues early
"""

import sys
from pathlib import Path

def test_frontend_build():
    """Check if frontend is built"""
    dist_path = Path("frontend/dist")
    index_path = dist_path / "index.html"
    assets_path = dist_path / "assets"
    
    print("🔍 Checking frontend build...")
    
    if not dist_path.exists():
        print("❌ frontend/dist directory not found")
        print("   Run: cd frontend && npm install && npm run build")
        return False
    
    if not index_path.exists():
        print("❌ frontend/dist/index.html not found")
        return False
    
    if not assets_path.exists():
        print("❌ frontend/dist/assets directory not found")
        return False
    
    print("✅ Frontend build looks good!")
    return True

def test_python_dependencies():
    """Check if Python dependencies are installed"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "langchain",
        "langgraph",
        "python-dotenv",
        "rich"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies installed!")
    return True

def test_env_file():
    """Check if .env file exists and has required keys"""
    print("\n🔍 Checking environment configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create .env and add: OPENROUTER_API_KEY=your_key_here")
        return False
    
    env_content = env_path.read_text()
    if "OPENROUTER_API_KEY" not in env_content:
        print("❌ OPENROUTER_API_KEY not found in .env")
        return False
    
    # Check if key looks valid (not empty or placeholder)
    for line in env_content.split("\n"):
        if line.startswith("OPENROUTER_API_KEY"):
            key = line.split("=", 1)[1].strip()
            if not key or key == "your_key_here" or key == "your_openrouter_key_here":
                print("⚠️  OPENROUTER_API_KEY appears to be a placeholder")
                print("   Get a real key from: https://openrouter.ai")
                return False
    
    print("✅ Environment configuration looks good!")
    return True

def test_render_config():
    """Check if render.yaml exists"""
    print("\n🔍 Checking Render configuration...")
    
    render_yaml = Path("render.yaml")
    if not render_yaml.exists():
        print("❌ render.yaml not found")
        return False
    
    print("✅ Render configuration found!")
    return True

def test_project_structure():
    """Check if key files and directories exist"""
    print("\n🔍 Checking project structure...")
    
    required_paths = [
        "src/orchestrator.py",
        "src/graph/workflow.py",
        "src/models.py",
        "requirements.txt",
        "frontend/package.json",
        "data/input"
    ]
    
    missing = []
    for path_str in required_paths:
        if not Path(path_str).exists():
            missing.append(path_str)
    
    if missing:
        print(f"❌ Missing files/directories: {', '.join(missing)}")
        return False
    
    print("✅ Project structure looks good!")
    return True

def main():
    print("=" * 60)
    print("🚀 Deployment Readiness Check")
    print("=" * 60)
    
    tests = [
        test_project_structure,
        test_python_dependencies,
        test_env_file,
        test_frontend_build,
        test_render_config
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed! Ready to deploy to Render.")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Ready for deployment'")
        print("3. git push origin main")
        print("4. Deploy on Render dashboard")
    else:
        print("❌ Some checks failed. Fix the issues above before deploying.")
        sys.exit(1)
    print("=" * 60)

if __name__ == "__main__":
    main()
