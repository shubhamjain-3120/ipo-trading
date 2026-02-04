import sqlite3
from datetime import date, datetime
import config

def get_db():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS ipos (
            id INTEGER PRIMARY KEY,
            company TEXT NOT NULL,
            open_date DATE,
            close_date DATE,
            listing_date DATE,
            issue_price REAL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY,
            company TEXT NOT NULL,
            close_date DATE,
            qib REAL,
            snii REAL,
            bnii REAL,
            nii REAL,
            retail REAL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            company TEXT NOT NULL,
            decision_type TEXT,
            reason TEXT,
            order_id TEXT,
            entry_price REAL,
            stop_loss_price REAL,
            target_price REAL,
            quantity INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS run_logs (
            id INTEGER PRIMARY KEY,
            run_date DATE NOT NULL,
            run_type TEXT,
            status TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

# IPO functions
def upsert_ipo(company, open_date, close_date, listing_date, issue_price):
    conn = get_db()
    conn.execute('''
        INSERT INTO ipos (company, open_date, close_date, listing_date, issue_price)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            open_date=excluded.open_date,
            close_date=excluded.close_date,
            listing_date=excluded.listing_date,
            issue_price=excluded.issue_price,
            scraped_at=CURRENT_TIMESTAMP
    ''', (company, open_date, close_date, listing_date, issue_price))
    conn.commit()
    conn.close()

def get_ipos_by_close_date(close_date):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM ipos WHERE close_date = ?', (close_date,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ipos_by_listing_date(listing_date):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM ipos WHERE listing_date = ?', (listing_date,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_ipos():
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM ipos ORDER BY close_date DESC LIMIT 50'
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Subscription functions
def save_subscription(company, close_date, qib, snii, bnii, nii, retail):
    conn = get_db()
    conn.execute('''
        INSERT INTO subscriptions (company, close_date, qib, snii, bnii, nii, retail)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (company, close_date, qib, snii, bnii, nii, retail))
    conn.commit()
    conn.close()

def get_subscription(company, close_date):
    conn = get_db()
    row = conn.execute(
        'SELECT * FROM subscriptions WHERE company = ? AND close_date = ?',
        (company, close_date)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

# Decision functions
def save_decision(date, company, decision_type, reason, order_id=None,
                  entry_price=None, stop_loss_price=None, target_price=None,
                  quantity=None, status='PENDING'):
    conn = get_db()
    conn.execute('''
        INSERT INTO decisions (date, company, decision_type, reason, order_id,
                               entry_price, stop_loss_price, target_price, quantity, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, company, decision_type, reason, order_id, entry_price,
          stop_loss_price, target_price, quantity, status))
    conn.commit()
    conn.close()

def update_decision(id, **kwargs):
    conn = get_db()
    sets = ', '.join(f'{k} = ?' for k in kwargs.keys())
    values = list(kwargs.values()) + [id]
    conn.execute(f'UPDATE decisions SET {sets} WHERE id = ?', values)
    conn.commit()
    conn.close()

def get_pending_buys(listing_date):
    conn = get_db()
    rows = conn.execute('''
        SELECT d.*, i.issue_price
        FROM decisions d
        JOIN ipos i ON d.company = i.company
        WHERE d.decision_type = 'BUY'
        AND d.status = 'PENDING'
        AND i.listing_date = ?
    ''', (listing_date,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_recent_decisions(limit=20):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM decisions ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Log functions
def log_run(run_type, status, details=''):
    conn = get_db()
    conn.execute('''
        INSERT INTO run_logs (run_date, run_type, status, details)
        VALUES (?, ?, ?, ?)
    ''', (date.today(), run_type, status, details))
    conn.commit()
    conn.close()

def get_recent_logs(limit=50):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM run_logs ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Date-based queries
def get_all_run_dates():
    """Get all unique dates that have activity"""
    conn = get_db()
    rows = conn.execute('''
        SELECT DISTINCT run_date FROM run_logs
        ORDER BY run_date DESC
    ''').fetchall()
    conn.close()
    return [r['run_date'] for r in rows]

def get_ipos_by_date(date_str):
    """Get IPOs relevant for a date (closing or listing)"""
    conn = get_db()
    rows = conn.execute('''
        SELECT * FROM ipos
        WHERE close_date = ? OR listing_date = ? OR open_date = ?
        ORDER BY company
    ''', (date_str, date_str, date_str)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_decisions_by_date(date_str):
    """Get decisions made on a date"""
    conn = get_db()
    rows = conn.execute('''
        SELECT * FROM decisions
        WHERE date = ?
        ORDER BY created_at DESC
    ''', (date_str,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_logs_by_date(date_str):
    """Get run logs for a date"""
    conn = get_db()
    rows = conn.execute('''
        SELECT * FROM run_logs
        WHERE run_date = ?
        ORDER BY created_at
    ''', (date_str,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize on import
init_db()
