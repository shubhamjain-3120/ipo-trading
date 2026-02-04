import math
from datetime import date
from kiteconnect import KiteConnect
import config
import db

kite = None

def init_kite():
    """Initialize Kite Connect with access token from database or env var"""
    global kite

    if not config.KITE_API_KEY:
        print("Kite API credentials not configured")
        return None

    kite = KiteConnect(api_key=config.KITE_API_KEY)

    # Try to get token from database first
    access_token = db.get_access_token()

    # Fallback to env var if no DB token
    if not access_token and config.KITE_ACCESS_TOKEN:
        access_token = config.KITE_ACCESS_TOKEN

    if access_token:
        kite.set_access_token(access_token)
        print("Kite Connect initialized with access token")
    else:
        print("Kite Connect initialized (no access token - login required)")

    return kite

def set_access_token(access_token):
    """Set access token manually"""
    global kite
    if kite:
        kite.set_access_token(access_token)
        print("Access token updated")

def calculate_quantity(issue_price):
    """Calculate number of shares to buy based on investment amount"""
    if not issue_price or issue_price <= 0:
        return 0
    return math.ceil(config.INVESTMENT_AMOUNT / issue_price)

def get_instrument_token(symbol):
    """Get instrument token for a symbol (for placing orders)"""
    if not kite:
        return None

    # Search in NSE instruments
    instruments = kite.instruments("NSE")
    for inst in instruments:
        if inst['tradingsymbol'].upper() == symbol.upper():
            return inst['instrument_token']

    # Try BSE
    instruments = kite.instruments("BSE")
    for inst in instruments:
        if inst['tradingsymbol'].upper() == symbol.upper():
            return inst['instrument_token']

    return None

def place_buy_order(symbol, quantity):
    """Place a market buy order"""
    if not kite:
        print("Kite not initialized")
        return None

    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite.TRANSACTION_TYPE_BUY,
            quantity=quantity,
            product=kite.PRODUCT_CNC,  # Delivery
            order_type=kite.ORDER_TYPE_MARKET
        )
        print(f"Buy order placed: {order_id}")
        return order_id
    except Exception as e:
        print(f"Error placing buy order: {e}")
        return None

def place_stop_loss_order(symbol, quantity, trigger_price):
    """Place a stop loss market order (SL-M)"""
    if not kite:
        return None

    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            product=kite.PRODUCT_CNC,
            order_type=kite.ORDER_TYPE_SLM,
            trigger_price=trigger_price
        )
        print(f"Stop loss order placed: {order_id}")
        return order_id
    except Exception as e:
        print(f"Error placing SL order: {e}")
        return None

def place_target_order(symbol, quantity, price):
    """Place a limit sell order for target profit"""
    if not kite:
        return None

    try:
        order_id = kite.place_order(
            variety=kite.VARIETY_REGULAR,
            exchange=kite.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=kite.TRANSACTION_TYPE_SELL,
            quantity=quantity,
            product=kite.PRODUCT_CNC,
            order_type=kite.ORDER_TYPE_LIMIT,
            price=price
        )
        print(f"Target order placed: {order_id}")
        return order_id
    except Exception as e:
        print(f"Error placing target order: {e}")
        return None

def get_order_status(order_id):
    """Get status of an order"""
    if not kite:
        return None

    try:
        orders = kite.orders()
        for o in orders:
            if o['order_id'] == order_id:
                return o
        return None
    except Exception as e:
        print(f"Error getting order status: {e}")
        return None

def get_fill_price(order_id):
    """Get the average fill price of an executed order"""
    order = get_order_status(order_id)
    if order and order['status'] == 'COMPLETE':
        return order['average_price']
    return None

def evaluate_subscription(subscription):
    """
    Evaluate if subscription qualifies for BUY
    Rule: ALL of QIB, SNII, BNII, NII, Retail must be > 1x
    """
    qib = subscription.get('qib') or 0
    snii = subscription.get('snii') or 0
    bnii = subscription.get('bnii') or 0
    nii = subscription.get('nii') or 0
    retail = subscription.get('retail') or 0

    # Build reason string
    parts = []
    all_above_1 = True

    checks = [
        ('QIB', qib),
        ('SNII', snii),
        ('BNII', bnii),
        ('NII', nii),
        ('Retail', retail)
    ]

    for name, val in checks:
        if val > 1:
            parts.append(f"{name}: {val}x ✓")
        else:
            parts.append(f"{name}: {val}x ✗")
            all_above_1 = False

    reason = ', '.join(parts)

    if all_above_1:
        return 'BUY', f"All categories oversubscribed: {reason}"
    else:
        return 'SKIP', f"Not all categories oversubscribed: {reason}"

def execute_trade(company, issue_price, decision_id):
    """Execute the full trade flow: buy + SL + target"""
    if not kite:
        print("Kite not initialized, simulating trade")
        db.update_decision(decision_id, status='SIMULATED')
        return False

    # Extract symbol from company name (rough, might need mapping)
    symbol = company.split()[0].upper()

    quantity = calculate_quantity(issue_price)
    if quantity <= 0:
        db.update_decision(decision_id, status='FAILED', reason='Invalid quantity')
        return False

    # Place buy order
    buy_order_id = place_buy_order(symbol, quantity)
    if not buy_order_id:
        db.update_decision(decision_id, status='FAILED', order_id=None)
        return False

    # Wait a bit for fill (in real scenario, poll status)
    import time
    time.sleep(5)

    # Get fill price
    fill_price = get_fill_price(buy_order_id)
    if not fill_price:
        fill_price = issue_price  # Fallback to issue price

    # Calculate SL and target
    sl_price = round(fill_price * (1 - config.STOP_LOSS_PERCENT / 100), 2)
    target_price = round(fill_price * (1 + config.TARGET_PROFIT_PERCENT / 100), 2)

    # Place SL order
    sl_order_id = place_stop_loss_order(symbol, quantity, sl_price)

    # Place target order
    target_order_id = place_target_order(symbol, quantity, target_price)

    # Update decision with all order info
    db.update_decision(
        decision_id,
        status='EXECUTED',
        order_id=buy_order_id,
        entry_price=fill_price,
        stop_loss_price=sl_price,
        target_price=target_price,
        quantity=quantity
    )

    print(f"Trade executed: {company}")
    print(f"  Quantity: {quantity}, Entry: {fill_price}")
    print(f"  SL: {sl_price}, Target: {target_price}")

    return True

def run_evaluation(today=None):
    """
    Run on closing date to evaluate subscriptions and create BUY decisions
    """
    if today is None:
        today = date.today().isoformat()

    print(f"Running evaluation for close date: {today}")

    # Get IPOs closing today
    ipos = db.get_ipos_by_close_date(today)
    if not ipos:
        print("No IPOs closing today")
        return

    for ipo in ipos:
        company = ipo['company']
        print(f"Evaluating: {company}")

        # Get subscription data
        sub = db.get_subscription(company, today)
        if not sub:
            print(f"  No subscription data for {company}")
            db.save_decision(today, company, 'SKIP', 'No subscription data available')
            continue

        # Evaluate
        decision, reason = evaluate_subscription(sub)
        print(f"  Decision: {decision} - {reason}")

        # Save decision
        db.save_decision(today, company, decision, reason)

    db.log_run('EVALUATE', 'SUCCESS', f'Evaluated {len(ipos)} IPOs')

def run_trading(today=None):
    """
    Run on listing date to execute BUY decisions
    """
    if today is None:
        today = date.today().isoformat()

    print(f"Running trading for listing date: {today}")

    # Initialize Kite
    init_kite()

    # Get pending BUY decisions for IPOs listing today
    pending = db.get_pending_buys(today)
    if not pending:
        print("No pending BUY orders for today")
        return

    for decision in pending:
        company = decision['company']
        issue_price = decision['issue_price']
        decision_id = decision['id']

        print(f"Executing trade: {company} at ~{issue_price}")
        execute_trade(company, issue_price, decision_id)

    db.log_run('TRADE', 'SUCCESS', f'Processed {len(pending)} trades')

if __name__ == '__main__':
    # For testing
    print("Testing evaluation logic...")
    test_sub = {
        'qib': 2.5,
        'snii': 1.2,
        'bnii': 1.8,
        'nii': 1.5,
        'retail': 3.2
    }
    decision, reason = evaluate_subscription(test_sub)
    print(f"Test result: {decision} - {reason}")
