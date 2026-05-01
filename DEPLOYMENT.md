# Deployment Guide

## 🚀 Deploying to Render

### Prerequisites
- A GitHub account with your code pushed to a repository
- A Render account (free tier available at https://render.com)
- An OpenRouter API key (get one at https://openrouter.ai)

### Step-by-Step Deployment

#### 1. Prepare Your Repository
Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account if you haven't already
4. Select your repository from the list

#### 3. Configure the Service

Render will auto-detect the `render.yaml` file. If not, use these settings:

- **Name:** `claims-processing-agent` (or your preferred name)
- **Region:** Choose the closest to your users
- **Branch:** `main` (or your default branch)
- **Runtime:** `Python 3`
- **Build Command:**
  ```bash
  pip install -r requirements.txt && cd frontend && npm install && npm run build
  ```
- **Start Command:**
  ```bash
  uvicorn src.orchestrator:app --host 0.0.0.0 --port $PORT
  ```

#### 4. Add Environment Variables

In the "Environment" section, add:

| Key | Value |
|-----|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `PYTHON_VERSION` | `3.9.0` |

**Important:** Make sure to keep `OPENROUTER_API_KEY` secret!

#### 5. Deploy

1. Click **"Create Web Service"**
2. Render will start building your application
3. Wait for the build to complete (usually 5-10 minutes)
4. Once deployed, you'll get a URL like: `https://your-app-name.onrender.com`

### 6. Verify Deployment

Visit your app URL. You should see the Claims Processing Agent frontend with:
- A file upload area
- "Process Claim" button
- Clean, modern UI

Test the API endpoint:
```bash
curl https://your-app-name.onrender.com/api
```

Expected response:
```json
{
  "status": "ok",
  "message": "API is running. Use POST /api/process to upload file."
}
```

---

## 🔧 Troubleshooting

### Issue: "detail: Not Found" appears instead of frontend

**Cause:** Frontend wasn't built or static files aren't being served.

**Solution:**
1. Check build logs in Render dashboard
2. Ensure `frontend/dist` directory was created during build
3. Verify the build command includes: `cd frontend && npm install && npm run build`

### Issue: API returns 500 error

**Cause:** Missing `OPENROUTER_API_KEY` environment variable.

**Solution:**
1. Go to Render dashboard → Your service → Environment
2. Add `OPENROUTER_API_KEY` with your actual API key
3. Save and redeploy

### Issue: Build fails with "npm not found"

**Cause:** Node.js isn't installed in the build environment.

**Solution:**
Render's Python environment includes Node.js by default. If this fails:
1. Check the build logs for specific errors
2. Ensure `package.json` exists in the `frontend/` directory

### Issue: Application crashes on startup

**Cause:** Missing Python dependencies or incorrect start command.

**Solution:**
1. Check that all dependencies in `requirements.txt` are installed
2. Verify the start command: `uvicorn src.orchestrator:app --host 0.0.0.0 --port $PORT`
3. Check logs for specific error messages

---

## 🌐 Custom Domain (Optional)

To use your own domain:

1. Go to your service in Render dashboard
2. Click **"Settings"** → **"Custom Domain"**
3. Add your domain (e.g., `claims.yourdomain.com`)
4. Update your DNS records as instructed by Render
5. Wait for SSL certificate to be provisioned (automatic)

---

## 🔄 Continuous Deployment

Render automatically redeploys when you push to your connected branch:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render will automatically detect the push and redeploy
```

---

## 📊 Monitoring

### View Logs
1. Go to Render dashboard → Your service
2. Click **"Logs"** tab
3. View real-time application logs

### Check Metrics
1. Go to **"Metrics"** tab
2. Monitor:
   - CPU usage
   - Memory usage
   - Request count
   - Response times

---

## 💰 Pricing

**Free Tier:**
- 750 hours/month of runtime
- Automatic sleep after 15 minutes of inactivity
- Wakes up on incoming requests (may take 30-60 seconds)

**Paid Tiers:**
- Always-on instances
- More CPU and memory
- Custom domains included
- Priority support

For production use, consider upgrading to a paid tier for better performance.

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - It's already in `.gitignore`
2. **Use Render's environment variables** - Don't hardcode API keys
3. **Enable HTTPS** - Render provides free SSL certificates
4. **Rotate API keys regularly** - Update in Render dashboard when needed
5. **Monitor logs** - Check for suspicious activity

---

## 📝 Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [OpenRouter API Docs](https://openrouter.ai/docs)

---

## 🆘 Need Help?

If you encounter issues:
1. Check the [Render Community Forum](https://community.render.com/)
2. Review application logs in Render dashboard
3. Verify all environment variables are set correctly
4. Ensure your code works locally before deploying
