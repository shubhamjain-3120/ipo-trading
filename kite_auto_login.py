"""
Fully automated Kite Connect login using Selenium + TOTP
Based on: https://medium.com/@yasheshlele/how-to-fully-automate-your-zerodha-kite-api-login-with-python-1bf6001f34fe
"""

import time
import pyotp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from kiteconnect import KiteConnect
from datetime import datetime, timedelta
import config
import db

def get_chrome_driver():
    """Initialize headless Chrome driver"""
    import os

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # For Docker/Railway: use system chromium
    chrome_bin = os.environ.get('CHROME_BIN')
    if chrome_bin:
        chrome_options.binary_location = chrome_bin

    # Try to use system Chrome
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"Chrome driver error: {e}")
        print("Local: Install with 'brew install chromedriver'")
        print("Railway: Ensure Dockerfile installs chromium")
        return None

    return driver

def auto_login_kite():
    """
    Fully automated Kite Connect login
    Returns access_token or None
    """
    if not all([config.KITE_API_KEY, config.KITE_API_SECRET,
                config.KITE_USER_ID, config.KITE_PASSWORD, config.KITE_TOTP_KEY]):
        print("Missing Kite credentials for auto-login")
        return None

    print("Starting automated Kite login...")

    driver = get_chrome_driver()
    if not driver:
        return None

    try:
        # Initialize Kite Connect
        kite = KiteConnect(api_key=config.KITE_API_KEY)
        login_url = kite.login_url()

        print(f"Opening login URL: {login_url}")
        driver.get(login_url)

        # Wait for login page to load
        wait = WebDriverWait(driver, 10)

        # Enter user ID
        print("Entering user ID...")
        user_id_input = wait.until(EC.presence_of_element_located((By.ID, "userid")))
        user_id_input.send_keys(config.KITE_USER_ID)

        # Enter password
        print("Entering password...")
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(config.KITE_PASSWORD)

        # Click login button
        print("Clicking login...")
        login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_button.click()

        # Wait for TOTP page
        time.sleep(2)

        # Generate TOTP
        print("Generating TOTP...")
        totp = pyotp.TOTP(config.KITE_TOTP_KEY)
        totp_code = totp.now()

        # Enter TOTP
        print("Entering TOTP...")
        totp_input = wait.until(EC.presence_of_element_located((By.ID, "totp")))
        totp_input.send_keys(totp_code)

        # Click continue
        print("Submitting TOTP...")
        continue_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        continue_button.click()

        # Wait for redirect and capture request_token from URL
        print("Waiting for redirect...")
        time.sleep(3)

        current_url = driver.current_url
        print(f"Redirected to: {current_url}")

        # Extract request_token
        if "request_token=" in current_url:
            request_token = current_url.split("request_token=")[1].split("&")[0]
            print(f"Got request_token: {request_token[:20]}...")

            # Generate access token
            print("Generating access token...")
            data = kite.generate_session(request_token, api_secret=config.KITE_API_SECRET)
            access_token = data['access_token']

            # Store in database
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            db.save_access_token(access_token, expires_at)

            print("✓ Access token generated and saved!")
            return access_token
        else:
            print("No request_token in URL - login may have failed")
            return None

    except Exception as e:
        print(f"Auto-login error: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        driver.quit()

def auto_refresh_token_if_needed():
    """
    Check if token is expired and auto-refresh if needed
    Returns True if token is valid (either existing or refreshed)
    """
    token = db.get_access_token()

    if token:
        print("✓ Valid access token exists")
        return True

    print("Token expired or missing, attempting auto-refresh...")
    new_token = auto_login_kite()

    if new_token:
        print("✓ Token auto-refreshed successfully")
        return True
    else:
        print("✗ Auto-refresh failed")
        return False

if __name__ == '__main__':
    # Test auto-login
    print("Testing Kite auto-login...")
    token = auto_login_kite()
    if token:
        print(f"\nSuccess! Token: {token[:30]}...")
    else:
        print("\nFailed to get token")
