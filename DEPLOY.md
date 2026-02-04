# Railway Deployment Guide

## Step 1: Prepare Code

Already done! The project is ready for deployment.

## Step 2: Push to GitHub

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit - IPO trading tool"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/ipo-trading.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy to Railway

### Option A: Railway Dashboard (Easiest)

1. Go to https://railway.app and sign up/login
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `ipo-trading` repository
4. Railway will auto-detect Python and deploy

### Option B: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

## Step 4: Set Environment Variables

In Railway dashboard → Variables, add:

```
KITE_API_KEY=your_api_key_here
KITE_API_SECRET=your_api_secret_here
KITE_ACCESS_TOKEN=your_access_token_here
INVESTMENT_AMOUNT=5000
STOP_LOSS_PERCENT=1.5
TARGET_PROFIT_PERCENT=4
PORT=5000
```

**Important:** Don't set access token yet - wait until you can access the deployed URL first.

## Step 5: Generate Access Token

After deployment, Railway will give you a URL like `https://your-app.railway.app`

1. Update your Kite Connect app redirect URL to: `https://your-app.railway.app`

2. Generate access token:
   - Visit: `https://kite.zerodha.com/connect/login?v=3&api_key=YOUR_API_KEY`
   - Login with Zerodha credentials
   - Copy `request_token` from redirected URL
   - Run locally: `python generate_token.py`
   - Copy the generated access token

3. Add access token to Railway environment variables

4. Redeploy (Railway will auto-redeploy when you change env vars)

## Step 6: Set Up Cron Job

Railway has built-in cron support:

1. In Railway dashboard, click "New" → "Cron Job"
2. Set schedule: `30 3 * * *` (9:00 AM IST = 3:30 AM UTC)
3. Set command: `curl https://your-app.railway.app/cron`

Or use an external cron service like:
- https://cron-job.org (free)
- Set URL: `https://your-app.railway.app/cron`
- Set schedule: Daily at 03:30 UTC

## Step 7: Verify

1. Visit your Railway URL to see the dashboard
2. Click "Run Daily Job" to test manually
3. Check the date detail page to verify data

## Daily Access Token Refresh

Access tokens expire daily. You have two options:

**Option 1: Manual (Simple)**
- Each morning, regenerate token using `generate_token.py`
- Update Railway env var `KITE_ACCESS_TOKEN`

**Option 2: Automated (Future)**
- Build a `/kite-callback` route to handle OAuth flow
- Store tokens in database
- Auto-refresh before trading

For now, Option 1 is fine for a POC.

## Troubleshooting

**Build fails:**
- Check Railway logs
- Verify requirements.txt is correct
- Ensure Python version matches runtime.txt

**App crashes:**
- Check Railway logs for errors
- Verify all env vars are set
- Test locally first with `gunicorn app:app`

**Database issues:**
- Railway provides ephemeral filesystem
- Consider using Railway PostgreSQL for persistence
- Or accept that data resets on redeploy (fine for POC)

**Cron not working:**
- Verify the /cron endpoint works: `curl https://your-app.railway.app/cron`
- Check cron service logs
- Ensure app is not sleeping (Railway free tier may sleep after inactivity)
