"""CBOE API options chain provider - Updated with better fallback"""
import requests
import json
import configparser
import os
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from options.providers.base_provider import OptionsChainProvider

logger = logging.getLogger('my_logger')

class CBOEOptionsProvider(OptionsChainProvider):
    """CBOE API options chain provider with fallback to alternative sources"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.ini')
        self.config.read(config_path)
        self.api_url = self.config.get('CBOE', 'API_URL', fallback='https://www.cboe.com')
        self.api_key = self.config.get('CBOE', 'API_KEY', fallback='')
        self.provider_name = "CBOE"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def is_available(self) -> bool:
        """Check if CBOE provider is available"""
        return True
    
    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None,
                         strike_count: int = 20) -> Dict[str, Any]:
        """
        Get options chain from CBOE or alternative free sources
        
        Note: CBOE doesn't provide free public API access. This provider
        attempts to use alternative free sources or returns a helpful error.
        """
        try:
            # Try CBOE endpoints first (may require authentication)
            result = self._try_cboe_endpoints(symbol, expiry_date, strike_count)
            if result and "error" not in result:
                return result
            
            # Fallback to alternative free sources
            logger.info(f"CBOE endpoints not accessible, trying alternative sources for {symbol}")
            return self._try_alternative_sources(symbol, expiry_date, strike_count)
            
        except Exception as e:
            logger.error(f"CBOE provider error: {e}")
            return self._create_error_response(symbol, expiry_date, str(e))
    
    def _try_cboe_endpoints(self, symbol: str, expiry_date: Optional[str], strike_count: int) -> Optional[Dict[str, Any]]:
        """Try various CBOE endpoint formats"""
        endpoints = [
            f"{self.api_url}/us/options/market_statistics/options_chain",
            f"{self.api_url}/api/option_chain/v1/{symbol}",
            f"https://api.cboe.com/v1/market/options/chains/{symbol}",
        ]
        
        params = {"symbol": symbol}
        if expiry_date:
            formatted_date = f"{expiry_date[:4]}-{expiry_date[4:6]}-{expiry_date[6:8]}"
            params["expiry"] = formatted_date
        
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, params=params, timeout=5)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data:
                            return self._parse_cboe_json_response(data, symbol, expiry_date)
                    except:
                        pass
            except:
                continue
        
        return None
    
    def _try_alternative_sources(self, symbol: str, expiry_date: Optional[str], strike_count: int) -> Dict[str, Any]:
        """
        Try alternative free sources for options data
        
        Note: Most free APIs have limitations. For production use,
        consider using E*TRADE API or a paid options data service.
        """
        # Try Yahoo Finance (unofficial, may be rate-limited)
        result = self._try_yahoo_finance(symbol, strike_count)
        if result and "error" not in result:
            return result
        
        # Return helpful error message
        return self._create_error_response(
            symbol, 
            expiry_date,
            "CBOE provider is not available. CBOE doesn't provide free public API access, "
            "and Yahoo Finance fallback is rate-limited. "
            "RECOMMENDATION: Use E*TRADE provider instead (you're already authenticated). "
            "Set DATA_SOURCE=ETRADE in config.ini or use provider='ETRADE' parameter."
        )
    
    def _try_yahoo_finance(self, symbol: str, strike_count: int) -> Optional[Dict[str, Any]]:
        """
        Try Yahoo Finance for options data (unofficial API)
        Note: This is rate-limited and may not always work
        """
        try:
            # Yahoo Finance options endpoint (unofficial)
            url = f"https://query1.finance.yahoo.com/v7/finance/options/{symbol}"
            response = self.session.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if "optionChain" in data and "result" in data["optionChain"]:
                    return self._parse_yahoo_finance_response(data, symbol)
            elif response.status_code == 429:
                logger.warning("Yahoo Finance rate-limited (429). Too many requests.")
                return None
        except Exception as e:
            logger.debug(f"Yahoo Finance attempt failed: {e}")
        
        return None
    
    def _parse_yahoo_finance_response(self, data: Dict, symbol: str) -> Dict[str, Any]:
        """Parse Yahoo Finance options response"""
        formatted = {
            "calls": [],
            "puts": [],
            "strikes": [],
            "underlying_price": 0.0,
            "expiry_date": None,
            "provider": "Yahoo Finance (via CBOE provider)",
            "symbol": symbol
        }
        
        try:
            results = data.get("optionChain", {}).get("result", [])
            if not results:
                return formatted
            
            result = results[0]
            quote = result.get("quote", {})
            formatted["underlying_price"] = float(quote.get("regularMarketPrice", 0) or 0)
            
            # Get first expiration's options
            expirations = result.get("expirationDates", [])
            if expirations:
                formatted["expiry_date"] = str(expirations[0])
            
            options = result.get("options", [])
            if options:
                option_data = options[0]
                calls = option_data.get("calls", [])
                puts = option_data.get("puts", [])
                
                # Process calls
                for call in calls[:strike_count]:
                    strike = float(call.get("strike", 0))
                    if strike > 0:
                        formatted["calls"].append({
                            "symbol": call.get("contractSymbol", ""),
                            "strike": strike,
                            "bid": float(call.get("bid", 0) or 0),
                            "ask": float(call.get("ask", 0) or 0),
                            "last": float(call.get("lastPrice", 0) or 0),
                            "volume": int(call.get("volume", 0) or 0),
                            "open_interest": int(call.get("openInterest", 0) or 0),
                            "iv": float(call.get("impliedVolatility", 0) or 0),
                            "delta": float(call.get("delta", 0) or 0),
                            "gamma": float(call.get("gamma", 0) or 0),
                            "theta": float(call.get("theta", 0) or 0),
                            "vega": float(call.get("vega", 0) or 0)
                        })
                        if strike not in formatted["strikes"]:
                            formatted["strikes"].append(strike)
                
                # Process puts
                for put in puts[:strike_count]:
                    strike = float(put.get("strike", 0))
                    if strike > 0:
                        formatted["puts"].append({
                            "symbol": put.get("contractSymbol", ""),
                            "strike": strike,
                            "bid": float(put.get("bid", 0) or 0),
                            "ask": float(put.get("ask", 0) or 0),
                            "last": float(put.get("lastPrice", 0) or 0),
                            "volume": int(put.get("volume", 0) or 0),
                            "open_interest": int(put.get("openInterest", 0) or 0),
                            "iv": float(put.get("impliedVolatility", 0) or 0),
                            "delta": float(put.get("delta", 0) or 0),
                            "gamma": float(put.get("gamma", 0) or 0),
                            "theta": float(put.get("theta", 0) or 0),
                            "vega": float(put.get("vega", 0) or 0)
                        })
                        if strike not in formatted["strikes"]:
                            formatted["strikes"].append(strike)
            
            formatted["strikes"].sort()
            return formatted
            
        except Exception as e:
            logger.error(f"Error parsing Yahoo Finance response: {e}")
            return None
    
    def _parse_cboe_json_response(self, data: Dict, symbol: str, expiry_date: Optional[str]) -> Dict[str, Any]:
        """Parse CBOE JSON API response to standard format"""
        formatted = {
            "calls": [],
            "puts": [],
            "strikes": [],
            "underlying_price": 0.0,
            "expiry_date": expiry_date,
            "provider": self.provider_name,
            "symbol": symbol
        }
        
        if "data" in data:
            for option in data["data"]:
                strike = float(option.get("strike", 0))
                option_type = option.get("type", "").upper()
                
                if strike not in formatted["strikes"]:
                    formatted["strikes"].append(strike)
                
                option_data = {
                    "symbol": option.get("symbol", ""),
                    "strike": strike,
                    "bid": float(option.get("bid", 0) or 0),
                    "ask": float(option.get("ask", 0) or 0),
                    "last": float(option.get("last", 0) or 0),
                    "volume": int(option.get("volume", 0) or 0),
                    "open_interest": int(option.get("open_interest", option.get("openInterest", 0)) or 0),
                    "iv": float(option.get("implied_volatility", option.get("iv", 0)) or 0),
                    "delta": float(option.get("delta", 0) or 0),
                    "gamma": float(option.get("gamma", 0) or 0),
                    "theta": float(option.get("theta", 0) or 0),
                    "vega": float(option.get("vega", 0) or 0)
                }
                
                if option_type == "CALL" or option_type == "C":
                    formatted["calls"].append(option_data)
                elif option_type == "PUT" or option_type == "P":
                    formatted["puts"].append(option_data)
        
        if "underlying_price" in data:
            formatted["underlying_price"] = float(data["underlying_price"])
        elif "underlyingPrice" in data:
            formatted["underlying_price"] = float(data["underlyingPrice"])
        
        formatted["strikes"].sort()
        return formatted
    
    def _create_error_response(self, symbol: str, expiry_date: Optional[str], error_msg: str) -> Dict[str, Any]:
        """Create a standardized error response"""
        return {
            "calls": [],
            "puts": [],
            "strikes": [],
            "underlying_price": 0.0,
            "expiry_date": expiry_date,
            "provider": self.provider_name,
            "symbol": symbol,
            "error": error_msg
        }
