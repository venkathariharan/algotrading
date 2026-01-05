"""E*TRADE API Client Wrapper for MCP Server"""
import json
import logging
import configparser
import os
from rauth import OAuth1Session
from accounts.accounts import Accounts
from market.market import Market
from order.order import Order

logger = logging.getLogger('my_logger')

class EtradeClient:
    """Wrapper class for E*TRADE API operations"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        self.config.read(config_path)
        self.session = None
        self.base_url = None
        self.consumer_key = None
        self._load_session()
    
    def _load_session(self):
        """Load authenticated session from saved tokens"""
        token_file = os.path.join(os.path.dirname(__file__), '..', 'oauth_tokens.json')
        
        if not os.path.exists(token_file):
            raise Exception("No saved tokens found. Please authenticate first using etrade_python_client.py")
        
        with open(token_file, 'r') as f:
            token_data = json.load(f)
        
        self.base_url = token_data['base_url']
        self.consumer_key = token_data.get('consumer_key')
        self.session = OAuth1Session(
            consumer_key=token_data['consumer_key'],
            consumer_secret=token_data['consumer_secret'],
            access_token=token_data['access_token'],
            access_token_secret=token_data['access_token_secret']
        )
        logger.info("E*TRADE session loaded successfully")
    
    def _get_consumer_key(self):
        """Get consumer key from token data or config file"""
        # First try to get from stored token data
        if self.consumer_key:
            return self.consumer_key
        
        # Fall back to config file
        try:
            return self.config["DEFAULT"]["CONSUMER_KEY"]
        except (KeyError, configparser.NoSectionError, configparser.NoOptionError):
            # Last resort: try to load from token file again
            token_file = os.path.join(os.path.dirname(__file__), '..', 'oauth_tokens.json')
            if os.path.exists(token_file):
                with open(token_file, 'r') as f:
                    token_data = json.load(f)
                    self.consumer_key = token_data.get('consumer_key')
                    return self.consumer_key
        return None
    
    def get_accounts(self):
        """Get list of accounts"""
        accounts_obj = Accounts(self.session, self.base_url)
        url = self.base_url + "/v1/accounts/list.json"
        response = self.session.get(url, header_auth=True)
        
        if response.status_code == 200:
            data = response.json()
            if "AccountListResponse" in data and "Accounts" in data["AccountListResponse"]:
                accounts = data["AccountListResponse"]["Accounts"].get("Account", [])
                # Filter out closed accounts
                return [acc for acc in accounts if acc.get('accountStatus') != 'CLOSED']
        return []
    
    def get_account_balance(self, account_id_key: str):
        """Get account balance"""
        url = self.base_url + f"/v1/accounts/{account_id_key}/balance.json"
        headers = {"consumerkey": self.config["DEFAULT"]["CONSUMER_KEY"]}
        params = {"instType": "BROKERAGE", "realTimeNAV": "true"}
        response = self.session.get(url, header_auth=True, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_quote(self, symbol: str):
        """Get market quote for symbol"""
        url = self.base_url + f"/v1/market/quote/{symbol}.json"
        response = self.session.get(url)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_orders(self, account_id_key: str, status: str = "OPEN"):
        """Get orders for an account by status"""
        url = self.base_url + f"/v1/accounts/{account_id_key}/orders.json"
        consumer_key = self._get_consumer_key()
        headers = {"consumerkey": consumer_key} if consumer_key else {}
        params = {"status": status}
        response = self.session.get(url, header_auth=True, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_order(self, account_id_key: str, order_id: str):
        """Get specific order details by order ID"""
        url = self.base_url + f"/v1/accounts/{account_id_key}/orders/{order_id}.json"
        consumer_key = self._get_consumer_key()
        headers = {"consumerkey": consumer_key} if consumer_key else {}
        response = self.session.get(url, header_auth=True, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def cancel_order(self, account_id_key: str, order_id: str):
        """Cancel an open order"""
        url = self.base_url + f"/v1/accounts/{account_id_key}/orders/cancel.json"
        consumer_key = self._get_consumer_key()
        headers = {"Content-Type": "application/xml", "consumerKey": consumer_key}
        
        payload = f"""<CancelOrderRequest>
                       <orderId>{order_id}</orderId>
                   </CancelOrderRequest>"""
        
        response = self.session.put(url, header_auth=True, headers=headers, data=payload)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def place_order(self, account_id_key: str, order_details: dict):
        """
        Place an order
        
        :param account_id_key: Account ID key
        :param order_details: Order details dictionary
        :return: Order result
        """
        # Get account info
        accounts = self.get_accounts()
        account = None
        for acc in accounts:
            if acc.get("accountIdKey") == account_id_key:
                account = acc
                break
        
        if not account:
            return {"error": "Account not found"}
        
        # Create order object
        order_obj = Order(self.session, account, self.base_url)
        
        # Use the existing place_order_flow but with provided details
        # For MCP, we'll create a simplified order placement
        return self._place_order_simple(order_obj, account, order_details)
    
    def _place_order_simple(self, order_obj, account, order_details):
        """Place order using simplified flow for MCP"""
        try:
            import random
            # Get consumer key using helper method
            consumer_key = self._get_consumer_key()
            if not consumer_key:
                return {"error": "CONSUMER_KEY not found in config.ini or oauth_tokens.json. Please check your configuration."}
            
            # Build order structure
            order_dict = {
                "client_order_id": str(random.randint(1000000000, 9999999999)),
                "price_type": order_details.get("price_type", "MARKET"),
                "order_term": order_details.get("order_term", "GOOD_FOR_DAY"),
                "limit_price": str(order_details.get("limit_price", "")),
                "symbol": str(order_details.get("symbol", "")).strip().upper(),
                "order_action": order_details.get("order_action", "BUY"),
                "quantity": str(order_details.get("quantity", 1))
            }
            
            # Preview order using direct API call
            url = self.base_url + "/v1/accounts/" + account["accountIdKey"] + "/orders/preview.json"
            headers = {"Content-Type": "application/xml", "consumerKey": consumer_key}
            
            limit_price_value = order_dict["limit_price"] if order_dict["price_type"] == "LIMIT" else ""
            
            payload = """<PreviewOrderRequest>
                           <orderType>EQ</orderType>
                           <clientOrderId>{0}</clientOrderId>
                           <Order>
                               <allOrNone>false</allOrNone>
                               <priceType>{1}</priceType>
                               <orderTerm>{2}</orderTerm>
                               <marketSession>REGULAR</marketSession>
                               <stopPrice></stopPrice>
                               <limitPrice>{3}</limitPrice>
                               <Instrument>
                                   <Product>
                                       <securityType>EQ</securityType>
                                       <symbol>{4}</symbol>
                                   </Product>
                                   <orderAction>{5}</orderAction>
                                   <quantityType>QUANTITY</quantityType>
                                   <quantity>{6}</quantity>
                               </Instrument>
                           </Order>
                       </PreviewOrderRequest>"""
            
            payload = payload.format(
                order_dict["client_order_id"],
                order_dict["price_type"],
                order_dict["order_term"],
                limit_price_value,
                order_dict["symbol"],
                order_dict["order_action"],
                order_dict["quantity"]
            )
            
            response = self.session.post(url, header_auth=True, headers=headers, data=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "PreviewOrderResponse" in data and "PreviewIds" in data["PreviewOrderResponse"]:
                    preview_id = data["PreviewOrderResponse"]["PreviewIds"][0]["previewId"]
                    
                    # Place order directly (avoiding Order class which has old config access)
                    place_url = self.base_url + "/v1/accounts/" + account["accountIdKey"] + "/orders/place.json"
                    place_headers = {"Content-Type": "application/xml", "consumerKey": consumer_key}
                    place_payload = f"""<PlaceOrderRequest>
                                       <previewId>{preview_id}</previewId>
                                   </PlaceOrderRequest>"""
                    
                    place_response = self.session.post(place_url, header_auth=True, headers=place_headers, data=place_payload)
                    
                    if place_response.status_code == 200:
                        place_data = place_response.json()
                        if "PlaceOrderResponse" in place_data and "OrderIds" in place_data["PlaceOrderResponse"]:
                            order_id = place_data["PlaceOrderResponse"]["OrderIds"][0]["orderId"]
                            return {
                                "success": True,
                                "order_id": order_id,
                                "preview_id": preview_id,
                                "symbol": order_dict["symbol"],
                                "action": order_dict["order_action"],
                                "quantity": order_dict["quantity"]
                            }
                        else:
                            error_msg = "Unknown error"
                            if "Error" in place_data:
                                error_msg = place_data["Error"].get("message", "Unknown error")
                            return {"error": f"Order placement failed: {error_msg}"}
                    else:
                        place_error_data = place_response.json() if place_response.text else {}
                        place_error_msg = place_error_data.get("Error", {}).get("message", f"HTTP {place_response.status_code}")
                        return {"error": f"Order placement failed: {place_error_msg}"}
                else:
                    error_msg = "Unknown error"
                    if "Error" in data:
                        error_msg = data["Error"].get("message", "Unknown error")
                    return {"error": f"Order preview failed: {error_msg}"}
            else:
                error_data = response.json() if response.text else {}
                error_msg = error_data.get("Error", {}).get("message", f"HTTP {response.status_code}")
                return {"error": f"API error: {error_msg}"}
                
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return {"error": str(e)}

