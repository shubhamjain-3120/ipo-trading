"""
Main scheduler - called by Railway cron at 9 AM IST
Runs the full daily workflow:
1. Scrape IPO data
2. Evaluate subscriptions for IPOs closing today
3. Execute trades for IPOs listing today
"""
from datetime import date
import scraper
import trader
import db

def run_daily_job():
    """Main entry point for daily cron job"""
    today = date.today().isoformat()
    print(f"=== Running daily job for {today} ===")

    # Step 1: Scrape fresh data
    print("\n[1/3] Scraping IPO data...")
    scraper.run_scraper()

    # Step 2: Evaluate subscriptions
    print("\n[2/3] Evaluating subscriptions...")
    trader.run_evaluation(today)

    # Step 3: Execute trades
    print("\n[3/3] Executing trades...")
    trader.run_trading(today)

    print("\n=== Daily job complete ===")
    db.log_run('DAILY_JOB', 'SUCCESS', f'Completed for {today}')

if __name__ == '__main__':
    run_daily_job()
