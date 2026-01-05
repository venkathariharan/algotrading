"""MCP Tools/Endpoints for E*TRADE"""
from typing import Any, Dict, Optional
from mcp_server.etrade_client import EtradeClient
from options.options_chain import OptionsChain
from options.options_display import OptionsChainDisplay

class EtradeTools:
    """MCP Tools for E*TRADE operations"""
    
    def __init__(self):
        self.client = EtradeClient()
        self.options_display = OptionsChainDisplay()
    
    def get_accounts(self) -> Dict[str, Any]:
        """Get list of E*TRADE accounts"""
        try:
            accounts = self.client.get_accounts()
            if accounts is None:
                return {"accounts": [], "count": 0, "error": "Failed to retrieve accounts"}
            if not isinstance(accounts, list):
                accounts = []
            return {
                "accounts": accounts,
                "count": len(accounts)
            }
        except Exception as e:
            return {"accounts": [], "count": 0, "error": str(e)}
    
    def get_account_balance(self, account_id_key: str) -> Dict[str, Any]:
        """Get account balance"""
        balance = self.client.get_account_balance(account_id_key)
        return balance or {"error": "Could not retrieve balance"}
    
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get market quote for a symbol"""
        quote = self.client.get_quote(symbol)
        return quote or {"error": "Could not retrieve quote"}
    
    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None, 
                         strike_count: int = 20, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get options chain for a symbol with neat display
        
        :param symbol: Underlying symbol (e.g., "SPX")
        :param expiry_date: Expiry date in YYYYMMDD format
        :param strike_count: Number of strikes to return
        :param provider: "ETRADE", "CBOE", or None (uses config)
        :return: Options chain data with formatted display
        """
        options = OptionsChain(
            session=self.client.session if provider != "CBOE" else None,
            base_url=self.client.base_url if provider != "CBOE" else None,
            provider_name=provider
        )
        chain = options.get_options_chain(symbol, expiry_date, strike_count)
        
        if chain:
            # Add formatted display
            chain["formatted_display"] = self.options_display.format_options_chain(chain)
            chain["json_format"] = self.options_display.format_json(chain, pretty=True)
        else:
            chain = {"error": "Could not retrieve options chain"}
        
        return chain
    
    def get_spx_options(self, expiry_date: Optional[str] = None,
                       strike_count: int = 20, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get SPX options chain with neat display
        
        :param expiry_date: Expiry date in YYYYMMDD format
        :param strike_count: Number of strikes to return
        :param provider: "ETRADE", "CBOE", or None (uses config)
        :return: SPX options chain data with formatted display
        """
        return self.get_options_chain("SPX", expiry_date, strike_count, provider)
    
    def place_order(self, account_id_key: str, symbol: str, 
                   action: str, quantity: int, 
                   price_type: str = "MARKET",
                   limit_price: Optional[float] = None,
                   order_term: str = "GOOD_FOR_DAY") -> Dict[str, Any]:
        """
        Place a stock or options order
        
        :param account_id_key: Account ID key
        :param symbol: Stock or option symbol
        :param action: "BUY", "SELL", "BUY_TO_COVER", "SELL_SHORT"
        :param quantity: Number of shares/contracts
        :param price_type: "MARKET" or "LIMIT"
        :param limit_price: Limit price (required if price_type is LIMIT)
        :param order_term: "GOOD_FOR_DAY", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"
        :return: Order result
        """
        order_details = {
            "symbol": symbol,
            "order_action": action,
            "quantity": quantity,
            "price_type": price_type,
            "limit_price": limit_price if price_type == "LIMIT" else "",
            "order_term": order_term
        }
        
        result = self.client.place_order(account_id_key, order_details)
        return result
    
    def get_orders(self, account_id_key: str, status: str = "OPEN") -> Dict[str, Any]:
        """
        Get orders for an account by status
        
        :param account_id_key: Account ID key
        :param status: Order status (OPEN, EXECUTED, CANCELLED, REJECTED, EXPIRED, INDIVIDUAL_FILLS)
        :return: Orders data
        """
        orders = self.client.get_orders(account_id_key, status)
        return orders or {"error": "Could not retrieve orders"}
    
    def get_order(self, account_id_key: str, order_id: str) -> Dict[str, Any]:
        """
        Get specific order details by order ID
        
        :param account_id_key: Account ID key
        :param order_id: Order ID
        :return: Order details
        """
        order = self.client.get_order(account_id_key, order_id)
        return order or {"error": "Order not found"}
    
    def cancel_order(self, account_id_key: str, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order
        
        :param account_id_key: Account ID key
        :param order_id: Order ID to cancel
        :return: Cancel result
        """
        result = self.client.cancel_order(account_id_key, order_id)
        return result

