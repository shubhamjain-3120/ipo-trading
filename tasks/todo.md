# IPO Trading Tool - Implementation

## Completed
- [x] Project setup (requirements.txt, config.py)
- [x] Database schema and helper functions (db.py)
- [x] Web scraper using NSE API (scraper.py) - switched from chittorgarh (JS-rendered) to NSE API
- [x] Decision engine and Zerodha trader (trader.py)
- [x] Scheduler for daily job (scheduler.py)
- [x] Flask app with dashboard (app.py, templates/dashboard.html)
- [x] Railway deployment config (Procfile, railway.json)
- [x] Tested scraper locally - working with NSE API
- [x] Tested Flask dashboard - working

## To Deploy
- [ ] Deploy to Railway and configure env vars
- [ ] Set up Railway cron job (9 AM IST = 3:30 AM UTC)
- [ ] Test with real Zerodha credentials

## Environment Variables to Set in Railway
```
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_ACCESS_TOKEN=your_access_token
INVESTMENT_AMOUNT=5000
STOP_LOSS_PERCENT=1.5
TARGET_PROFIT_PERCENT=4
```

## How to Get Kite Access Token
1. Create app at https://developers.kite.trade/
2. Get your API key and secret
3. Generate access token:
   - Visit: `https://kite.zerodha.com/connect/login?v=3&api_key=YOUR_API_KEY`
   - Login with your Zerodha credentials (password + TOTP)
   - After redirect, copy `request_token` from URL
   - Exchange for access token using API secret (one-time setup)
4. Access token is valid for 1 day - needs daily refresh
   - Option 1: Manually update env var daily
   - Option 2: Build token refresh endpoint (future enhancement)

## Railway Cron Setup
Create a cron service that hits `/cron` endpoint at 9 AM IST:
- Cron expression: `30 3 * * *` (3:30 AM UTC = 9:00 AM IST)

## Local Testing
```bash
# Create venv and install deps
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run scraper
python scraper.py

# Run Flask app
python app.py
# Then open http://localhost:5000
```
