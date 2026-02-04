from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import date, datetime, timedelta
from kiteconnect import KiteConnect
import config
import db
import scraper
import scheduler

app = Flask(__name__)
app.secret_key = config.KITE_API_SECRET or 'dev-secret-key'

@app.route('/')
def dashboard():
    """Main dashboard showing dates"""
    # Get unique dates from run_logs
    dates = db.get_all_run_dates()
    return render_template('dashboard.html',
        dates=dates,
        today=date.today().isoformat()
    )

@app.route('/date/<date_str>')
def date_detail(date_str):
    """Show detailed view for a specific date"""
    # Get all data for this date
    ipos = db.get_ipos_by_date(date_str)
    decisions = db.get_decisions_by_date(date_str)
    logs = db.get_logs_by_date(date_str)

    return render_template('date_detail.html',
        date=date_str,
        ipos=ipos,
        decisions=decisions,
        logs=logs,
        config={
            'investment': config.INVESTMENT_AMOUNT,
            'stop_loss': config.STOP_LOSS_PERCENT,
            'target': config.TARGET_PROFIT_PERCENT
        }
    )

@app.route('/run')
def run_job():
    """Manually trigger the daily job"""
    scheduler.run_daily_job()
    return redirect(url_for('dashboard'))

@app.route('/scrape')
def run_scrape():
    """Manually trigger scraping only"""
    scraper.run_scraper()
    return redirect(url_for('dashboard'))

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return {'status': 'ok'}

@app.route('/cron')
def cron_trigger():
    """Endpoint for Railway cron to hit"""
    scheduler.run_daily_job()
    return {'status': 'completed'}

@app.route('/login-kite')
def login_kite():
    """Redirect to Kite login"""
    if not config.KITE_API_KEY:
        return "Kite API key not configured", 500

    kite = KiteConnect(api_key=config.KITE_API_KEY)
    login_url = kite.login_url()
    return redirect(login_url)

@app.route('/kite-callback')
def kite_callback():
    """Handle Kite OAuth callback"""
    request_token = request.args.get('request_token')

    if not request_token:
        return "No request token received", 400

    if not config.KITE_API_KEY or not config.KITE_API_SECRET:
        return "Kite credentials not configured", 500

    try:
        kite = KiteConnect(api_key=config.KITE_API_KEY)
        data = kite.generate_session(request_token, api_secret=config.KITE_API_SECRET)
        access_token = data['access_token']

        # Store token in database (expires in 24 hours)
        expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
        db.save_access_token(access_token, expires_at)

        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Error generating access token: {e}", 500

@app.route('/token-status')
def token_status():
    """Check if we have a valid token"""
    token = db.get_access_token()
    if token:
        return {'status': 'valid', 'has_token': True}
    else:
        return {'status': 'expired', 'has_token': False}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
