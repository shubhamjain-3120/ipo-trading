import os

# Trading configuration
INVESTMENT_AMOUNT = int(os.environ.get('INVESTMENT_AMOUNT', 5000))  # Rs. per IPO
STOP_LOSS_PERCENT = float(os.environ.get('STOP_LOSS_PERCENT', 1.5))  # SL below entry price
TARGET_PROFIT_PERCENT = float(os.environ.get('TARGET_PROFIT_PERCENT', 4))  # Target exit above entry

# Zerodha Kite API credentials
KITE_API_KEY = os.environ.get('KITE_API_KEY', '')
KITE_API_SECRET = os.environ.get('KITE_API_SECRET', '')
KITE_ACCESS_TOKEN = os.environ.get('KITE_ACCESS_TOKEN', '')  # Fallback manual token
KITE_USER_ID = os.environ.get('KITE_USER_ID', '')
KITE_PASSWORD = os.environ.get('KITE_PASSWORD', '')
KITE_TOTP_KEY = os.environ.get('KITE_TOTP_KEY', '')  # TOTP secret for automation

# Database path
DB_PATH = os.environ.get('DB_PATH', 'data/ipo.db')

# NSE API URLs (using NSE instead of chittorgarh - more reliable)
NSE_IPO_LIST_URL = 'https://www.nseindia.com/api/ipo-current-issue'
NSE_IPO_DETAIL_URL = 'https://www.nseindia.com/api/ipo-detail'
