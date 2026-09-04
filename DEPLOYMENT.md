# Veritas AI: Website Deployment Guide

This guide explains how to deploy your **Veritas AI Detector & Humanizer** website to the internet for **100% free**.

---

## ⚡ Option 1: Free 1-Click Cloud Hosting on Render (Recommended)

Render offers free web service hosting for Python FastAPI apps:

1. Create a free account at [render.com](https://render.com).
2. Push your project folder to a GitHub or GitLab repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of Veritas AI website"
   git remote add origin https://github.com/YOUR_USERNAME/veritas-ai.git
   git push -u origin main
   ```
3. In Render Dashboard, click **New +** ➔ **Web Service**.
4. Select your GitHub repository.
5. Render will automatically detect the settings from `render.yaml` or you can enter:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
6. Click **Create Web Service**. Within 2 minutes, your website will be live at `https://veritas-ai-xxxx.onrender.com`!

---

## ⚡ Option 2: Deploy on Hugging Face Spaces (Free Docker Hosting)

1. Create a free account at [huggingface.co](https://huggingface.co).
2. Go to **Spaces** ➔ **Create New Space**.
3. Choose **Docker** as the Space SDK and set license to **MIT**.
4. Clone the space repository and copy all files from this directory into it.
5. Push to Hugging Face:
   ```bash
   git add .
   git commit -m "Deploy Veritas AI"
   git push
   ```
6. Hugging Face will build the `Dockerfile` and give you a public URL like `https://huggingface.co/spaces/YOUR_NAME/veritas-ai`.

---

## ⚡ Option 3: Deploy on Railway (Free Tier)

1. Sign up at [railway.app](https://railway.app).
2. Click **New Project** ➔ **Deploy from GitHub repo**.
3. Railway automatically detects the `Procfile` and assigns a public domain with SSL.

---

## ⚡ Option 4: Instant Public URL from Your Computer (No Signup Needed)

If you want to share the website running on your computer with anyone right now, you can use **Cloudflare Tunnel** or **Localtunnel**:

### Using Localtunnel (Zero install):
```powershell
npx localtunnel --port 8000
```
This gives you a public `https://....loca.lt` URL instantly that routes to your running app!

### Using Cloudflared:
Download `cloudflared.exe` and run:
```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```
You get a free, secure `https://xxx.trycloudflare.com` URL to share with anyone in the world!
