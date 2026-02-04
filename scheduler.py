"""
Main scheduler - called by Railway cron at 9 AM IST
Runs the full daily workflow:
1. Auto-refresh Kite token if needed
2. Scrape IPO data
3. Evaluate subscriptions for IPOs closing today
4. Execute trades for IPOs listing today
"""
from datetime import date
import scraper
import trader
import db

def run_daily_job():
    """Main entry point for daily cron job"""
    today = date.today().isoformat()
    print(f"=== Running daily job for {today} ===")

    # Step 0: Auto-refresh Kite token if needed
    print("\n[0/4] Checking Kite token...")
    try:
        import kite_auto_login
        if not kite_auto_login.auto_refresh_token_if_needed():
            print("⚠ Warning: Kite token refresh failed, trading may not work")
    except Exception as e:
        print(f"⚠ Token auto-refresh error: {e}")

    # Step 1: Scrape fresh data
    print("\n[1/4] Scraping IPO data...")
    scraper.run_scraper()

    # Step 2: Evaluate subscriptions
    print("\n[2/4] Evaluating subscriptions...")
    trader.run_evaluation(today)

    # Step 3: Execute trades
    print("\n[3/4] Executing trades...")
    trader.run_trading(today)

    print("\n=== Daily job complete ===")
    db.log_run('DAILY_JOB', 'SUCCESS', f'Completed for {today}')

if __name__ == '__main__':
    run_daily_job()
