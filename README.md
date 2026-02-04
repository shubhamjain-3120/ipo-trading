# IPO Trading Tool

Automated IPO trading tool that:
1. Scrapes IPO data daily from NSE API
2. Evaluates subscription status on closing date
3. Places BUY orders on listing date with stop loss and target profit
4. Provides a dashboard to view data and decisions

## Setup

### 1. Zerodha Kite API Setup

1. Create a developer account at https://developers.kite.trade/
2. Create a new app to get your API key and secret
3. Generate access token (valid for 1 day):

```bash
# Run the token generator
python generate_token.py

# Follow the prompts:
# 1. Visit the login URL with your API key
# 2. Login with Zerodha credentials
# 3. Copy request_token from redirected URL
# 4. Enter API key, secret, and request token
# 5. Copy the generated access token
```

### 2. Local Testing

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Test scraper
python scraper.py

# Run Flask app
python app.py
# Open http://localhost:5000
```

### 3. Railway Deployment

1. Push to Railway
2. Set environment variables:
```
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_ACCESS_TOKEN=your_access_token
INVESTMENT_AMOUNT=5000
STOP_LOSS_PERCENT=1.5
TARGET_PROFIT_PERCENT=4
```

3. Set up cron job to hit `/cron` endpoint at 9 AM IST:
   - Cron expression: `30 3 * * *` (3:30 AM UTC = 9:00 AM IST)

## How It Works

### Daily Job Flow (9 AM IST)

1. **Scrape** - Fetches current IPOs from NSE API
2. **Evaluate** - For IPOs closing today, checks if ALL of (QIB, SNII, BNII, NII, Retail) > 1x
3. **Trade** - For IPOs listing today with BUY decision:
   - Places market BUY order (₹5000 worth)
   - Places stop loss at 1.5% below entry
   - Places target sell at 4% above entry

### Dashboard

Access at `/` to view:
- Recent IPOs with dates and prices
- Trading decisions (BUY/SKIP with reasons)
- Order execution status
- Run logs

## Configuration

Edit these in Railway env vars or `config.py`:

- `INVESTMENT_AMOUNT` - Amount to invest per IPO (default: 5000)
- `STOP_LOSS_PERCENT` - SL below entry (default: 1.5)
- `TARGET_PROFIT_PERCENT` - Target above entry (default: 4)

## Important Notes

- **Access token expires daily** - You'll need to regenerate it each day for automated trading
- **Paper trading first** - Test with small amounts before going live
- **Market hours** - Orders only execute during NSE trading hours (9:15 AM - 3:30 PM)
- **NSE API** - Using official NSE API, more reliable than scraping HTML

## Future Enhancements

- [ ] Auto-refresh access token (requires Kite session management)
- [ ] SMS/Telegram notifications for trades
- [ ] Trailing stop loss (requires paid Kite subscription for live data)
- [ ] Backtesting with historical data
- [ ] Multiple broker support
