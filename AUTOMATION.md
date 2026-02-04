# Fully Automated Kite Token Refresh

This setup enables **zero-touch** operation - the system automatically refreshes Kite tokens before they expire.

## How It Works

1. **Daily Cron Job** runs at 9 AM IST
2. **Checks token** - if expired, automatically refreshes
3. **Automated login** using Selenium + stored credentials + TOTP
4. **No manual intervention** needed

## Setup

### 1. Get TOTP Secret from Zerodha

Your TOTP secret is the base32 string used to generate 2FA codes.

**To get it:**
1. Go to Zerodha settings → 2FA
2. Disable 2FA temporarily
3. Re-enable 2FA - Zerodha shows QR code
4. Click "Can't scan?" to see the secret key (base32 string)
5. Copy this secret (looks like: `JBSWY3DPEHPK3PXP`)
6. Complete 2FA setup in your authenticator app

### 2. Environment Variables

Add these to Railway (in addition to existing ones):

```
KITE_USER_ID=your_zerodha_user_id
KITE_PASSWORD=your_zerodha_password
KITE_TOTP_KEY=your_totp_secret_base32
```

### 3. Install Chrome on Railway

Railway needs Chrome for Selenium. Add `nixpacks.toml`:

```toml
[phases.setup]
nixPkgs = ["...", "chromium", "chromedriver"]
```

Or use a buildpack that includes Chrome.

### 4. Test Locally

```bash
# Install chromedriver
brew install chromedriver

# Set env vars
export KITE_USER_ID=your_id
export KITE_PASSWORD=your_password
export KITE_TOTP_KEY=your_secret

# Test auto-login
python kite_auto_login.py
```

If successful, you'll see: "✓ Access token generated and saved!"

## How Auto-Refresh Works

```python
# Before trading each day:
1. Check if token exists in DB
2. If expired → Run automated login (Selenium)
3. Login → Enter credentials → Generate TOTP → Submit
4. Extract request_token from redirect URL
5. Generate access_token using Kite API
6. Store in database (valid 24 hours)
7. Proceed with trading
```

## Security Considerations

**Risks:**
- Storing credentials in env vars (Railway encrypts them)
- Automated login may violate Zerodha TOS (use at own risk)
- Account could be flagged for automated access

**Mitigations:**
- Use strong Railway account security
- Enable 2FA on Railway
- Monitor for any Zerodha alerts
- Consider this for personal use only

## Fallback

If auto-refresh fails:
1. Dashboard shows "Token expired"
2. Manual "Refresh Kite Token" button still available (OAuth flow)
3. System logs the failure

## Alternative: Accept One Daily Click

If you're uncomfortable with automation:
- Don't set `KITE_USER_ID`, `KITE_PASSWORD`, `KITE_TOTP_KEY`
- Auto-refresh won't run
- Click "Refresh Kite Token" once per day (5 seconds)
- More secure, fully compliant with TOS

## Railway-Specific Setup

For Railway deployment with Chrome:

**Option 1: Use Docker** (Recommended)
Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:$PORT"]
```

**Option 2: Use Nixpacks**
Create `nixpacks.toml`:
```toml
[phases.setup]
nixPkgs = ["python311", "chromium", "chromedriver"]
```

Then Railway will auto-build with Chrome support.

## Monitoring

Check logs to see auto-refresh in action:
```
=== Running daily job for 2026-02-04 ===
[0/4] Checking Kite token...
Token expired or missing, attempting auto-refresh...
Starting automated Kite login...
Entering user ID...
Entering password...
Generating TOTP...
✓ Access token generated and saved!
✓ Token auto-refreshed successfully
```

## Troubleshooting

**"Chrome driver error"**
- Install Chrome/Chromium on server
- Check chromedriver is in PATH

**"TOTP code rejected"**
- Verify TOTP_KEY is correct base32 string
- Check server time is synced (TOTP is time-based)

**"Login failed"**
- Check credentials are correct
- Zerodha may have changed UI (update selectors)
- Check if account is locked

**"Access token expired during trading"**
- Token only refreshes at start of daily job
- If manually testing, token might expire mid-day
- Click manual refresh or wait for next cron run
