"""E*TRADE OAuth Authentication Script"""
import json
import os
import webbrowser
import configparser
from rauth import OAuth1Service
from rauth.session import OAuth1Session

# Load configuration
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path)

TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'oauth_tokens.json')

def save_tokens(access_token, access_token_secret, base_url, consumer_key, consumer_secret):
    """Save OAuth tokens to file"""
    token_data = {
        "access_token": access_token,
        "access_token_secret": access_token_secret,
        "base_url": base_url,
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret
    }
    
    with open(TOKEN_FILE, 'w') as f:
        json.dump(token_data, f, indent=2)
    print(f"\nTokens saved to: {TOKEN_FILE}")

def load_tokens():
    """Load OAuth tokens from file"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return json.load(f)
    return None

def test_token_validity(access_token, access_token_secret, base_url, consumer_key, consumer_secret):
    """Test if tokens are still valid"""
    try:
        session = OAuth1Session(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        # Test with a simple API call
        url = base_url + "/v1/accounts/list.json"
        response = session.get(url, header_auth=True)
        return response.status_code == 200
    except:
        return False

def oauth():
    """OAuth 1.0 authentication flow"""
    consumer_key = config["DEFAULT"]["CONSUMER_KEY"]
    consumer_secret = config["DEFAULT"]["CONSUMER_SECRET"]
    
    print("\n" + "=" * 80)
    print("E*TRADE OAuth Authentication")
    print("=" * 80)
    
    # Check for existing tokens
    print("\nChecking for existing authentication tokens...")
    token_data = load_tokens()
    
    if token_data:
        print(f"Found stored tokens in: {TOKEN_FILE}")
        print("Testing token validity...")
        
        if test_token_validity(
            token_data['access_token'],
            token_data['access_token_secret'],
            token_data['base_url'],
            token_data['consumer_key'],
            token_data['consumer_secret']
        ):
            print("[OK] Stored tokens are valid!")
            print(f"Base URL: {token_data['base_url']}")
            print("\nYou can now use the MCP server.")
            return
        else:
            print("[INVALID] Stored tokens are invalid or expired.")
            print("Proceeding with new authentication...")
    
    # Select environment
    print("\nSelect E*TRADE Environment:")
    print("1. Sandbox (for testing)")
    print("2. Production (live trading)")
    print("3. Exit")
    
    while True:
        choice = input("\nEnter choice (1-3): ").strip()
        if choice == "1":
            base_url = config["DEFAULT"]["SANDBOX_BASE_URL"]
            request_token_url = "https://apisb.etrade.com/oauth/request_token"
            access_token_url = "https://apisb.etrade.com/oauth/access_token"
            authorize_url = "https://us.etrade.com/e/t/etws/authorize?key={}&token={}"
            break
        elif choice == "2":
            base_url = config["DEFAULT"]["PROD_BASE_URL"]
            request_token_url = "https://api.etrade.com/oauth/request_token"
            access_token_url = "https://api.etrade.com/oauth/access_token"
            authorize_url = "https://us.etrade.com/e/t/etws/authorize?key={}&token={}"
            break
        elif choice == "3":
            print("Exiting...")
            return
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    # Create OAuth service
    etrade = OAuth1Service(
        name="etrade",
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        request_token_url=request_token_url,
        access_token_url=access_token_url,
        authorize_url=authorize_url,
        base_url=base_url
    )
    
    print("\n" + "=" * 80)
    print("Step 1: Getting request token...")
    print("=" * 80)
    
    # Step 1: Get request token
    try:
        request_token, request_token_secret = etrade.get_request_token(
            params={"oauth_callback": "oob", "format": "json"}
        )
        print("[OK] Request token obtained")
    except Exception as e:
        print(f"[ERROR] Error getting request token: {e}")
        return
    
    print("\n" + "=" * 80)
    print("Step 2: Authorize in browser...")
    print("=" * 80)
    
    # Step 2: Get authorization URL and open browser
    auth_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    print(f"\nOpening browser for authorization...")
    print(f"If browser doesn't open, visit this URL manually:")
    print(f"\n{auth_url}\n")
    
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"Could not open browser automatically: {e}")
        print(f"Please visit the URL above manually.")
    
    # Step 3: Get verification code
    print("\n" + "=" * 80)
    print("Step 3: Enter verification code...")
    print("=" * 80)
    print("\nAfter authorizing in the browser, you will receive a verification code.")
    print("Enter that code below.")
    
    verification_code = input("\nEnter verification code: ").strip()
    
    if not verification_code:
        print("[ERROR] No verification code provided. Authentication cancelled.")
        return
    
    print("\n" + "=" * 80)
    print("Step 4: Exchanging for access token...")
    print("=" * 80)
    
    # Step 4: Exchange for access token
    try:
        session = etrade.get_auth_session(
            request_token,
            request_token_secret,
            params={"oauth_verifier": verification_code}
        )
        
        # Extract tokens from session
        access_token = getattr(session, 'access_token', None)
        access_token_secret = getattr(session, 'access_token_secret', None)
        
        # If not in session attributes, try to parse from response
        if not access_token or not access_token_secret:
            if hasattr(etrade, 'access_token_response') and etrade.access_token_response:
                from urllib.parse import parse_qs
                response_text = etrade.access_token_response.text
                parsed = parse_qs(response_text)
                access_token = parsed.get('oauth_token', [None])[0]
                access_token_secret = parsed.get('oauth_token_secret', [None])[0]
        
        if access_token and access_token_secret:
            print("[OK] Access token obtained")
            
            # Save tokens
            save_tokens(access_token, access_token_secret, base_url, consumer_key, consumer_secret)
            
            print("\n" + "=" * 80)
            print("Authentication Complete!")
            print("=" * 80)
            print(f"\n[OK] Tokens saved to: {TOKEN_FILE}")
            print(f"[OK] Base URL: {base_url}")
            print("\nYou can now use the MCP server with Cursor IDE.")
            print("\nNext steps:")
            print("1. Configure Cursor IDE (see CURSOR_MCP_SETUP.md)")
            print("2. Restart Cursor IDE")
            print("3. Start using E*TRADE tools in Cursor!")
            
        else:
            print("[ERROR] Could not extract access tokens from response.")
            print("Please try again.")
            
    except Exception as e:
        print(f"[ERROR] Error during authentication: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease try again.")

if __name__ == "__main__":
    oauth()

