"""E*TRADE API options chain provider"""
import json
import configparser
import os
import logging
from typing import Dict, Optional, Any, List
from options.providers.base_provider import OptionsChainProvider

logger = logging.getLogger('my_logger')

class EtradeOptionsProvider(OptionsChainProvider):
    """E*TRADE API options chain provider"""
    
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.ini')
        self.config.read(config_path)
        self.provider_name = "E*TRADE"
    
    def is_available(self) -> bool:
        """Check if E*TRADE provider is available"""
        return self.session is not None and self.base_url is not None
    
    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None,
                         strike_count: int = 20) -> Dict[str, Any]:
        """
        Get options chain from E*TRADE API
        """
        url = self.base_url + "/v1/market/optionchains.json"
        
        params = {
            "symbol": symbol,
            "strikeCount": strike_count,
            "includeWeekly": "true"
        }
        
        if expiry_date:
            params["expiryDate"] = expiry_date
        
        headers = {
            "consumerkey": self.config["DEFAULT"]["CONSUMER_KEY"]
        }
        
        try:
            response = self.session.get(
                url,
                header_auth=True,
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_etrade_response(data, symbol, expiry_date)
            else:
                logger.error(f"E*TRADE API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"E*TRADE provider error: {e}")
            return None
    
    def _parse_etrade_response(self, data: Dict, symbol: str, expiry_date: Optional[str]) -> Dict[str, Any]:
        """Parse E*TRADE API response to standard format"""
        formatted = {
            "calls": [],
            "puts": [],
            "strikes": [],
            "underlying_price": 0.0,
            "expiry_date": expiry_date,
            "provider": self.provider_name,
            "symbol": symbol
        }
        
        if "OptionChainResponse" in data:
            chain = data["OptionChainResponse"]
            
            # Get underlying price if available
            if "underlyingPrice" in chain:
                formatted["underlying_price"] = float(chain["underlyingPrice"])
            
            if "OptionPair" in chain:
                for pair in chain["OptionPair"]:
                    strike = float(pair.get("strikePrice", 0))
                    formatted["strikes"].append(strike)
                    
                    # Parse call option
                    if "Call" in pair and pair["Call"]:
                        call = pair["Call"]
                        formatted["calls"].append({
                            "symbol": call.get("symbol", ""),
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
                            "vega": float(call.get("vega", 0) or 0),
                            "time_value": float(call.get("timeValue", 0) or 0),
                            "intrinsic_value": float(call.get("intrinsicValue", 0) or 0)
                        })
                    
                    # Parse put option
                    if "Put" in pair and pair["Put"]:
                        put = pair["Put"]
                        formatted["puts"].append({
                            "symbol": put.get("symbol", ""),
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
                            "vega": float(put.get("vega", 0) or 0),
                            "time_value": float(put.get("timeValue", 0) or 0),
                            "intrinsic_value": float(put.get("intrinsicValue", 0) or 0)
                        })
        
        # Sort strikes
        formatted["strikes"].sort()
        
        return formatted

