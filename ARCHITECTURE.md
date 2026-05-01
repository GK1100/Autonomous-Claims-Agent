# 🏗️ Application Architecture

## Before Fix (Not Working on Render)

```
┌─────────────────────────────────────────────────────────┐
│                    Render Platform                       │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         FastAPI Application                     │    │
│  │                                                 │    │
│  │  ✅ /api/process  → Backend working            │    │
│  │  ✅ /api         → Health check working        │    │
│  │  ❌ /            → No route defined!           │    │
│  │  ❌ /assets/*    → Not served!                 │    │
│  │                                                 │    │
│  │  Result: {"detail": "Not Found"}               │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ❌ frontend/dist/ files exist but not served           │
└─────────────────────────────────────────────────────────┘
```

## After Fix (Working on Render)

```
┌─────────────────────────────────────────────────────────────────┐
│                       Render Platform                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              FastAPI Application                          │  │
│  │                                                           │  │
│  │  API Routes (Defined First):                             │  │
│  │  ✅ /api/process  → POST endpoint for file upload        │  │
│  │  ✅ /api         → GET health check                      │  │
│  │                                                           │  │
│  │  Static File Routes (Defined Last):                      │  │
│  │  ✅ /assets/*    → Serve CSS, JS, images                 │  │
│  │  ✅ /            → Serve index.html (React app)          │  │
│  │  ✅ /*           → Serve index.html (SPA routing)        │  │
│  │                                                           │  │
│  │  Result: Full working application! 🎉                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ✅ frontend/dist/ files properly served                        │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow Diagram

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ HTTP Request
       ↓
┌──────────────────────────────────────────────────┐
│              Render Load Balancer                 │
└──────────────────┬───────────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────────┐
│           FastAPI Application                     │
│                                                   │
│  Request Router:                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ Is path /api/* ?                         │    │
│  │   YES → API Handler                      │    │
│  │   ├─ POST /api/process → Process claim   │    │
│  │   └─ GET /api → Health check             │    │
│  │                                           │    │
│  │ Is path /assets/* ?                      │    │
│  │   YES → Static File Handler              │    │
│  │   └─ Serve from frontend/dist/assets/    │    │
│  │                                           │    │
│  │ Is path / or anything else?              │    │
│  │   YES → SPA Handler                      │    │
│  │   └─ Serve frontend/dist/index.html      │    │
│  └─────────────────────────────────────────┘    │
└──────────────────┬───────────────────────────────┘
                   │
                   │ HTTP Response
                   ↓
┌──────────────────────────────────────────────────┐
│              Browser Renders                      │
│                                                   │
│  - React App loads                                │
│  - User sees Claims Processing UI                 │
│  - User can upload files                          │
│  - Files sent to /api/process                     │
│  - Results displayed                              │
└──────────────────────────────────────────────────┘
```

## File Structure

```
Project Root
│
├── 🐍 Backend (Python/FastAPI)
│   ├── src/
│   │   ├── orchestrator.py ──────→ Main FastAPI app
│   │   ├── models.py ─────────────→ Pydantic schemas
│   │   └── graph/
│   │       ├── workflow.py ───────→ LangGraph workflow
│   │       ├── nodes.py ──────────→ Processing nodes
│   │       ├── state.py ──────────→ State management
│   │       └── utils.py ──────────→ Utility functions
│   │
│   ├── api/
│   │   └── index.py ──────────────→ Vercel entry point (legacy)
│   │
│   ├── data/
│   │   ├── input/ ────────────────→ Sample claim documents
│   │   └── output/ ───────────────→ Processed results
│   │
│   ├── requirements.txt ──────────→ Python dependencies
│   ├── runtime.txt ───────────────→ Python version
│   └── .env ──────────────────────→ Environment variables (local)
│
├── ⚛️ Frontend (React/TypeScript)
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.tsx ───────────→ Main React component
│   │   │   ├── main.tsx ──────────→ Entry point
│   │   │   ├── App.css ───────────→ Styles
│   │   │   └── assets/ ───────────→ Images, icons
│   │   │
│   │   ├── public/ ───────────────→ Static assets
│   │   ├── dist/ ─────────────────→ Built files (served by FastAPI)
│   │   │   ├── index.html
│   │   │   └── assets/
│   │   │       ├── *.js
│   │   │       └── *.css
│   │   │
│   │   ├── package.json ──────────→ Node dependencies
│   │   ├── vite.config.ts ────────→ Build configuration
│   │   └── tsconfig.json ─────────→ TypeScript config
│
├── 🚀 Deployment
│   ├── render.yaml ───────────────→ Render configuration
│   ├── vercel.json ───────────────→ Vercel config (legacy)
│   ├── build.sh ──────────────────→ Build script
│   ├── start.sh ──────────────────→ Startup script (Linux/Mac)
│   └── start.bat ─────────────────→ Startup script (Windows)
│
└── 📚 Documentation
    ├── README.md ─────────────────→ Project overview
    ├── DEPLOYMENT.md ─────────────→ Deployment guide
    ├── QUICK_START.md ────────────→ Fast deployment
    ├── FIX_APPLIED.md ────────────→ Fix summary
    ├── RENDER_FIX_SUMMARY.md ─────→ Technical details
    ├── ARCHITECTURE.md ───────────→ This file
    └── technical_design_document.md → Original design doc
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Full Stack                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Frontend Layer:                                         │
│  ┌────────────────────────────────────────────────┐    │
│  │ React 19 + TypeScript + Vite                   │    │
│  │ - Modern UI with drag-and-drop                 │    │
│  │ - Real-time file processing                    │    │
│  │ - JSON visualization                           │    │
│  └────────────────────────────────────────────────┘    │
│                         ↕                                │
│  API Layer:                                              │
│  ┌────────────────────────────────────────────────┐    │
│  │ FastAPI + Uvicorn                              │    │
│  │ - RESTful endpoints                            │    │
│  │ - File upload handling                         │    │
│  │ - Static file serving                          │    │
│  └────────────────────────────────────────────────┘    │
│                         ↕                                │
│  Processing Layer:                                       │
│  ┌────────────────────────────────────────────────┐    │
│  │ LangGraph + LangChain                          │    │
│  │ - Workflow orchestration                       │    │
│  │ - State management                             │    │
│  │ - Node-based processing                        │    │
│  └────────────────────────────────────────────────┘    │
│                         ↕                                │
│  AI Layer:                                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ OpenRouter API                                 │    │
│  │ - LLM-powered extraction                       │    │
│  │ - Multiple model support                       │    │
│  │ - Structured output parsing                    │    │
│  └────────────────────────────────────────────────┘    │
│                         ↕                                │
│  Data Layer:                                             │
│  ┌────────────────────────────────────────────────┐    │
│  │ Pydantic Models                                │    │
│  │ - Schema validation                            │    │
│  │ - Type safety                                  │    │
│  │ - JSON serialization                           │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Deployment Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                  Local Development                       │
│                                                          │
│  1. Edit code                                            │
│  2. Test locally: uvicorn src.orchestrator:app --reload │
│  3. Run tests: python test_deployment.py                │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ git push
                       ↓
┌─────────────────────────────────────────────────────────┐
│                    GitHub Repository                     │
│                                                          │
│  - Source code stored                                    │
│  - Version control                                       │
│  - Webhook to Render                                     │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ Auto-trigger
                       ↓
┌─────────────────────────────────────────────────────────┐
│                   Render Build Process                   │
│                                                          │
│  Step 1: Install Python dependencies                     │
│  └─ pip install -r requirements.txt                      │
│                                                          │
│  Step 2: Build frontend                                  │
│  └─ cd frontend && npm install && npm run build          │
│                                                          │
│  Step 3: Verify build                                    │
│  └─ Check frontend/dist/ exists                          │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ Deploy
                       ↓
┌─────────────────────────────────────────────────────────┐
│                  Render Production                       │
│                                                          │
│  - Start command: uvicorn src.orchestrator:app          │
│  - Environment: OPENROUTER_API_KEY loaded               │
│  - Port: $PORT (assigned by Render)                     │
│  - URL: https://your-app.onrender.com                   │
└─────────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

### 1. **Monolithic Deployment**
- **Why:** Simpler deployment, single service to manage
- **Benefit:** No CORS issues, easier debugging
- **Trade-off:** Frontend and backend scale together

### 2. **Static File Serving in FastAPI**
- **Why:** Render doesn't have separate static hosting like Vercel
- **Benefit:** Single endpoint for entire application
- **Trade-off:** FastAPI serves files (not ideal for high traffic)

### 3. **SPA Catch-All Route**
- **Why:** React Router needs all routes to serve index.html
- **Benefit:** Client-side routing works seamlessly
- **Trade-off:** Must define API routes before catch-all

### 4. **Build-Time Frontend Compilation**
- **Why:** Faster runtime, smaller deployment size
- **Benefit:** Optimized production build
- **Trade-off:** Longer build time on deployment

### 5. **Environment-Based Configuration**
- **Why:** Security and flexibility
- **Benefit:** Same code works locally and in production
- **Trade-off:** Must configure environment variables separately

## Performance Considerations

```
┌─────────────────────────────────────────────────────────┐
│                   Performance Profile                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Cold Start (Free Tier):                                 │
│  └─ 30-60 seconds (after 15 min inactivity)             │
│                                                          │
│  Warm Request:                                           │
│  ├─ Static files: < 100ms                               │
│  ├─ API health check: < 50ms                            │
│  └─ Claim processing: 5-15 seconds (LLM dependent)      │
│                                                          │
│  Bottlenecks:                                            │
│  ├─ LLM API calls (OpenRouter)                          │
│  ├─ File I/O (/tmp directory)                           │
│  └─ Graph execution (LangGraph)                         │
│                                                          │
│  Optimizations Applied:                                  │
│  ├─ Lazy graph initialization                           │
│  ├─ Temporary file cleanup                              │
│  └─ Efficient state management                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Security Layers                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Transport Security:                                  │
│     ✅ HTTPS enforced (Render provides SSL)             │
│     ✅ Secure headers via CORS middleware               │
│                                                          │
│  2. API Security:                                        │
│     ✅ API key stored in environment variables          │
│     ✅ No secrets in code or version control            │
│     ✅ File type validation (.txt only)                 │
│                                                          │
│  3. Data Security:                                       │
│     ✅ Temporary files cleaned up after processing      │
│     ✅ No persistent storage of uploaded files          │
│     ✅ Pydantic validation for all data                 │
│                                                          │
│  4. Deployment Security:                                 │
│     ✅ .env file in .gitignore                          │
│     ✅ Environment variables in Render dashboard        │
│     ✅ No hardcoded credentials                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Scalability Path

```
Current (Single Service):
┌──────────────────────┐
│  Render Web Service  │
│  ├─ FastAPI          │
│  ├─ Frontend         │
│  └─ Processing       │
└──────────────────────┘

Future (Microservices):
┌──────────────────────┐     ┌──────────────────────┐
│   Static Hosting     │     │   API Service        │
│   (Vercel/Netlify)   │────▶│   (Render/Railway)   │
│   - React SPA        │     │   - FastAPI          │
└──────────────────────┘     └──────────┬───────────┘
                                        │
                                        ↓
                             ┌──────────────────────┐
                             │  Worker Service      │
                             │  (Background Jobs)   │
                             │  - LangGraph         │
                             └──────────────────────┘
```

---

**Current Status:** ✅ Optimized for Render deployment
**Architecture Type:** Monolithic with SPA frontend
**Deployment Model:** Single web service
**Scaling Strategy:** Vertical (upgrade Render plan)
