import requests
from datetime import datetime, date
import db
import config

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
}

# NSE API endpoints
NSE_IPO_LIST_URL = 'https://www.nseindia.com/api/ipo-current-issue'
NSE_IPO_DETAIL_URL = 'https://www.nseindia.com/api/ipo-detail'

def parse_nse_date(date_str):
    """Parse date from NSE format like '04-Feb-2026'"""
    if not date_str or date_str.strip() == '-':
        return None
    date_str = date_str.strip()
    for fmt in ['%d-%b-%Y', '%d-%B-%Y', '%Y-%m-%d']:
        try:
            return datetime.strptime(date_str, fmt).date().isoformat()
        except ValueError:
            continue
    return None

def parse_float(val):
    """Parse float from string"""
    if not val or str(val).strip() in ['-', '', '0.00']:
        return 0.0
    val = str(val).strip().replace(',', '').replace('x', '').replace('X', '')
    try:
        return float(val)
    except ValueError:
        return 0.0

def scrape_ipo_list():
    """Scrape current IPO list from NSE API"""
    print(f"Scraping IPO list from NSE API...")

    resp = requests.get(NSE_IPO_LIST_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    data = resp.json()
    ipos = []

    for item in data:
        # Skip SME IPOs for now (focus on mainboard)
        # if item.get('series') == 'SME':
        #     continue

        ipo = {
            'company': item.get('companyName', ''),
            'symbol': item.get('symbol', ''),
            'open_date': parse_nse_date(item.get('issueStartDate')),
            'close_date': parse_nse_date(item.get('issueEndDate')),
            'listing_date': None,  # NSE API doesn't provide this in list
            'issue_price': None,   # Need to get from detail
            'status': item.get('status', ''),
            'series': item.get('series', ''),
            'subscription': parse_float(item.get('noOfTime', 0)),
        }

        if ipo['company']:
            ipos.append(ipo)
            print(f"  Found: {ipo['company']} ({ipo['symbol']}) - {ipo['subscription']}x subscribed")

    return ipos

def scrape_subscription_detail(symbol):
    """Get detailed subscription status for an IPO from NSE"""
    print(f"  Getting subscription details for {symbol}...")

    url = f"{NSE_IPO_DETAIL_URL}?symbol={symbol}"
    resp = requests.get(url, headers=HEADERS, timeout=30)

    if resp.status_code != 200:
        return None

    data = resp.json()
    bid_details = data.get('bidDetails', [])

    sub = {
        'qib': 0.0,
        'nii': 0.0,
        'snii': 0.0,
        'bnii': 0.0,
        'retail': 0.0,
    }

    for bid in bid_details:
        category = bid.get('category', '').lower()
        times = parse_float(bid.get('noOfTime', 0))

        if 'qualified institutional' in category or category.startswith('qib'):
            sub['qib'] = times
        elif 'non institutional' in category and 'more than' not in category and 'less than' not in category:
            sub['nii'] = times
        elif 'more than ten lakh' in category or 'shni' in category:
            sub['snii'] = times
        elif 'less than ten lakh' in category or 'bhni' in category:
            sub['bnii'] = times
        elif 'retail' in category:
            sub['retail'] = times

    return sub

def scrape_subscription_status():
    """Get subscription status for all current IPOs"""
    print("Scraping subscription status from NSE API...")

    ipos = scrape_ipo_list()
    subscriptions = []

    for ipo in ipos:
        symbol = ipo.get('symbol')
        if not symbol:
            continue

        detail = scrape_subscription_detail(symbol)
        if detail:
            sub = {
                'company': ipo['company'],
                'symbol': symbol,
                'close_date': ipo['close_date'],
                **detail
            }
            subscriptions.append(sub)
            print(f"    QIB: {sub['qib']}x, NII: {sub['nii']}x, Retail: {sub['retail']}x")

    return subscriptions

def save_ipos(ipos):
    """Save scraped IPOs to database"""
    for ipo in ipos:
        db.upsert_ipo(
            ipo['company'],
            ipo['open_date'],
            ipo['close_date'],
            ipo['listing_date'],
            ipo['issue_price']
        )
    print(f"Saved {len(ipos)} IPOs to database")

def save_subscriptions(subscriptions):
    """Save scraped subscriptions to database"""
    today = date.today().isoformat()

    for sub in subscriptions:
        close_date = sub.get('close_date') or today
        existing = db.get_subscription(sub['company'], close_date)
        if not existing:
            db.save_subscription(
                sub['company'],
                close_date,
                sub.get('qib', 0),
                sub.get('snii', 0),
                sub.get('bnii', 0),
                sub.get('nii', 0),
                sub.get('retail', 0)
            )
    print(f"Saved {len(subscriptions)} subscriptions to database")

def run_scraper():
    """Main scraper entry point"""
    try:
        ipos = scrape_ipo_list()
        save_ipos(ipos)
        db.log_run('SCRAPE_IPO', 'SUCCESS', f'Scraped {len(ipos)} IPOs')
    except Exception as e:
        print(f"Error scraping IPO list: {e}")
        db.log_run('SCRAPE_IPO', 'FAILED', str(e))

    try:
        subs = scrape_subscription_status()
        save_subscriptions(subs)
        db.log_run('SCRAPE_SUB', 'SUCCESS', f'Scraped {len(subs)} subscriptions')
    except Exception as e:
        print(f"Error scraping subscriptions: {e}")
        db.log_run('SCRAPE_SUB', 'FAILED', str(e))

if __name__ == '__main__':
    run_scraper()
