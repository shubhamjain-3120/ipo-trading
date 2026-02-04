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
INVESTMENT_AMOUNT=5000
STOP_LOSS_PERCENT=1.5
TARGET_PROFIT_PERCENT=4
```

**Note:** No need to manually set access token - the app handles it automatically!

## Step 5: Set Up Kite OAuth

After deployment, Railway will give you a URL like `https://your-app.railway.app`

1. Update your Kite Connect app redirect URL to: `https://your-app.railway.app/kite-callback`

2. Visit your Railway app URL and click **"Refresh Kite Token"**

3. Login with your Zerodha credentials (password + TOTP)

4. You'll be redirected back and the token will be stored in the database

**Token Auto-Management:**
- Token is stored in the database (valid for 24 hours)
- Dashboard shows token status (valid/expired)
- When expired, just click "Refresh Kite Token" again
- No manual token generation needed!

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

Access tokens expire after 24 hours. When it expires:

1. Dashboard shows: "⚠ Kite token expired"
2. Click **"Refresh Kite Token"** button
3. Login with Zerodha credentials
4. Done! Token stored for next 24 hours

**No manual token generation needed!** The app handles OAuth flow automatically.

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
