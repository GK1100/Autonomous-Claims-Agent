# 🚀 Quick Start Guide

## What Was Fixed

Your app was showing `{"detail": "Not Found"}` on Render because it was configured for Vercel but deployed to Render. The fix adds proper static file serving for Render.

## Deploy to Render NOW

### 1. Commit and Push Changes
```bash
git add .
git commit -m "Fix Render deployment - add static file serving"
git push origin main
```

### 2. Render Will Auto-Deploy
- If you already have the service on Render, it will automatically redeploy
- Wait 5-10 minutes for the build to complete
- Visit your Render URL - you should see the frontend!

### 3. If Auto-Deploy Doesn't Work
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select your service
3. Click "Manual Deploy" → "Deploy latest commit"

### 4. Verify It Works
Visit: `https://your-app-name.onrender.com`

You should see:
- ✅ Claims Processing Agent UI
- ✅ File upload area
- ✅ "Process Claim" button

## First Time Deploying?

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Initial deployment"
git push origin main
```

### Step 2: Create Render Service
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`

### Step 3: Add Environment Variable
In Render dashboard:
- Go to "Environment" tab
- Add: `OPENROUTER_API_KEY` = `your_actual_key`
- Save

### Step 4: Deploy
- Click "Create Web Service"
- Wait for build (5-10 minutes)
- Done!

## Test Locally First

### Build Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### Start Server
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# Or manually
uvicorn src.orchestrator:app --reload
```

### Visit
Open browser: `http://localhost:8000`

## Run Pre-Deployment Check

```bash
python test_deployment.py
```

This will verify:
- ✅ Frontend is built
- ✅ Python dependencies installed
- ✅ Environment variables configured
- ✅ Project structure correct
- ✅ Render config exists

## Troubleshooting

### Still seeing "Not Found"?
1. Check Render logs: Dashboard → Your Service → Logs
2. Verify `OPENROUTER_API_KEY` is set in Environment
3. Ensure build completed successfully
4. Check that `frontend/dist` was created during build

### Build fails?
1. Check build logs for specific errors
2. Verify `package.json` exists in `frontend/`
3. Ensure Node.js is available (Render includes it by default)

### API works but frontend doesn't?
1. Check that `frontend/dist/index.html` exists
2. Verify static file routes are registered
3. Look for errors in browser console

## Need More Help?

- 📖 Read `DEPLOYMENT.md` for detailed guide
- 📋 Check `RENDER_FIX_SUMMARY.md` for technical details
- 🔍 Review Render logs for error messages

## What Changed?

### Files Modified:
- `src/orchestrator.py` - Added static file serving
- `README.md` - Added deployment instructions

### Files Created:
- `render.yaml` - Render configuration
- `build.sh` / `start.sh` / `start.bat` - Helper scripts
- `DEPLOYMENT.md` - Detailed deployment guide
- `test_deployment.py` - Pre-deployment checks
- This file!

## Architecture

```
User → Render → FastAPI
                  ├─ /api/* → Backend API
                  ├─ /assets/* → Static files
                  └─ /* → React SPA (index.html)
```

## Important Notes

1. **Free Tier Sleep:** Render free tier sleeps after 15 minutes. First request may take 30-60 seconds to wake up.

2. **Environment Variables:** Never commit `.env` file. Always use Render's environment variables for production.

3. **Build Time:** First build takes longer as it installs all dependencies.

4. **Logs:** Always check logs if something doesn't work.

## Success Checklist

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] `OPENROUTER_API_KEY` added to Render environment
- [ ] Build completed successfully
- [ ] Frontend loads at root URL
- [ ] API responds at `/api`
- [ ] File upload works

## You're All Set! 🎉

Your Claims Processing Agent is now ready for production deployment on Render!
