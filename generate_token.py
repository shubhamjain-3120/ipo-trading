"""
Helper script to generate Kite access token from request token
Run this once to get your access token, then set it in Railway env vars

Usage:
1. Visit: https://kite.zerodha.com/connect/login?v=3&api_key=YOUR_API_KEY
2. Login with Zerodha credentials
3. Copy the request_token from redirected URL
4. Run: python generate_token.py
5. Enter your API key, secret, and request token
6. Copy the generated access token to Railway env vars
"""

from kiteconnect import KiteConnect

def generate_access_token():
    api_key = input("Enter your Kite API Key: ").strip()
    api_secret = input("Enter your Kite API Secret: ").strip()
    request_token = input("Enter the request_token from URL: ").strip()

    kite = KiteConnect(api_key=api_key)

    try:
        data = kite.generate_session(request_token, api_secret=api_secret)
        access_token = data["access_token"]

        print("\n" + "="*60)
        print("SUCCESS! Your access token:")
        print("="*60)
        print(access_token)
        print("="*60)
        print("\nSet this in Railway environment variables:")
        print(f"KITE_ACCESS_TOKEN={access_token}")
        print("\nNote: Token expires daily. You'll need to regenerate it each day.")
        print("="*60)

    except Exception as e:
        print(f"\nError generating token: {e}")
        print("Make sure your API key, secret, and request token are correct.")

if __name__ == '__main__':
    print("\nKite Access Token Generator")
    print("-" * 60)
    print("First, visit this URL in your browser:")
    print("https://kite.zerodha.com/connect/login?v=3&api_key=YOUR_API_KEY")
    print("(Replace YOUR_API_KEY with your actual API key)")
    print("-" * 60)
    print()

    generate_access_token()
