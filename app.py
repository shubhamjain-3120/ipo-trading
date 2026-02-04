from flask import Flask, render_template, redirect, url_for
from datetime import date
import config
import db
import scraper
import scheduler

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
