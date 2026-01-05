"""NASDAQ options chain provider"""
import requests
import json
import logging
from typing import Dict, Optional, Any
from options.providers.base_provider import OptionsChainProvider

logger = logging.getLogger('my_logger')

class NASDAQOptionsProvider(OptionsChainProvider):
    """NASDAQ options chain provider"""
    
    def __init__(self):
        self.provider_name = "NASDAQ"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nasdaq.com/'
        })
        self.base_url = "https://api.nasdaq.com"
    
    def is_available(self) -> bool:
        """Check if NASDAQ provider is available"""
        return True
    
    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None,
                         strike_count: int = 20) -> Dict[str, Any]:
        """
        Get options chain from NASDAQ
        
        NASDAQ provides options data via their API
        """
        try:
            # Try NASDAQ API endpoints
            result = self._try_nasdaq_api(symbol, expiry_date, strike_count)
            if result and "error" not in result:
                return result
            
            # Try alternative NASDAQ endpoints
            result = self._try_nasdaq_alternative(symbol, expiry_date, strike_count)
            if result and "error" not in result:
                return result
            
            # Return error if all attempts fail
            return self._create_error_response(
                symbol,
                expiry_date,
                "NASDAQ API endpoints not accessible. "
                "NASDAQ may require authentication or the endpoints have changed. "
                "RECOMMENDATION: Use E*TRADE provider (you're already authenticated)."
            )
            
        except Exception as e:
            logger.error(f"NASDAQ provider error: {e}")
            return self._create_error_response(symbol, expiry_date, str(e))
    
    def _try_nasdaq_api(self, symbol: str, expiry_date: Optional[str], strike_count: int) -> Optional[Dict[str, Any]]:
        """Try NASDAQ's main API endpoint"""
        try:
            # NASDAQ options chain API endpoint
            url = f"{self.base_url}/api/quote/{symbol}/options"
            
            params = {
                "assetclass": "stocks",
                "limit": strike_count
            }
            
            if expiry_date:
                # Format: YYYY-MM-DD
                formatted_date = f"{expiry_date[:4]}-{expiry_date[4:6]}-{expiry_date[6:8]}"
                params["expiry"] = formatted_date
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    return self._parse_nasdaq_response(data, symbol, expiry_date, strike_count)
                except json.JSONDecodeError:
                    logger.warning("NASDAQ returned non-JSON response")
                    return None
            else:
                logger.debug(f"NASDAQ API returned status {response.status_code}")
                return None
                
        except Exception as e:
            logger.debug(f"NASDAQ API attempt failed: {e}")
            return None
    
    def _try_nasdaq_alternative(self, symbol: str, expiry_date: Optional[str], strike_count: int) -> Optional[Dict[str, Any]]:
        """Try alternative NASDAQ endpoints and web scraping"""
        # Try alternative API endpoints
        alternatives = [
            f"https://www.nasdaq.com/api/v1/options/{symbol}",
            f"https://api.nasdaq.com/api/v1/options/{symbol}",
            f"https://www.nasdaq.com/api/quote/{symbol}/options",
            f"https://api.nasdaq.com/api/quote/{symbol}/options",
        ]
        
        for url in alternatives:
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if data:
                            return self._parse_nasdaq_response(data, symbol, expiry_date, strike_count)
                    except:
                        pass
            except:
                continue
        
        # Try web scraping approach (last resort)
        try:
            return self._try_nasdaq_scraping(symbol, strike_count)
        except Exception as e:
            logger.debug(f"NASDAQ scraping attempt failed: {e}")
        
        return None
    
    def _try_nasdaq_scraping(self, symbol: str, strike_count: int) -> Optional[Dict[str, Any]]:
        """Try to scrape options data from NASDAQ website"""
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.warning("BeautifulSoup4 not installed. Install with: pip install beautifulsoup4 lxml")
            return None
        
        try:
            # NASDAQ options page URL
            url = f"https://www.nasdaq.com/market-activity/stocks/{symbol}/option-chain"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for JSON data embedded in the page
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'optionChain' in script.string.lower():
                        # Try to extract JSON data
                        import re
                        json_match = re.search(r'\{.*"optionChain".*\}', script.string, re.DOTALL)
                        if json_match:
                            try:
                                data = json.loads(json_match.group())
                                return self._parse_nasdaq_response(data, symbol, None, strike_count)
                            except:
                                pass
                
                # Alternative: Look for data attributes
                data_divs = soup.find_all('div', {'data-options': True})
                if data_divs:
                    for div in data_divs:
                        try:
                            data = json.loads(div['data-options'])
                            return self._parse_nasdaq_response(data, symbol, None, strike_count)
                        except:
                            pass
        except Exception as e:
            logger.debug(f"NASDAQ scraping error: {e}")
        
        return None
    
    def _parse_nasdaq_response(self, data: Dict, symbol: str, expiry_date: Optional[str], strike_count: int) -> Dict[str, Any]:
        """Parse NASDAQ API response to standard format"""
        formatted = {
            "calls": [],
            "puts": [],
            "strikes": [],
            "underlying_price": 0.0,
            "expiry_date": expiry_date,
            "provider": self.provider_name,
            "symbol": symbol
        }
        
        try:
            # NASDAQ response format can vary - handle common structures
            # Try different possible response structures
            
            # Structure 1: data.options or data.optionChain
            options_data = None
            if "data" in data:
                options_data = data["data"]
                if isinstance(options_data, dict):
                    if "options" in options_data:
                        options_data = options_data["options"]
                    elif "optionChain" in options_data:
                        options_data = options_data["optionChain"]
            
            # Structure 2: Direct options array
            if not options_data and "options" in data:
                options_data = data["options"]
            
            # Structure 3: optionChain at root
            if not options_data and "optionChain" in data:
                options_data = data["optionChain"]
            
            # Get underlying price
            if "quote" in data:
                quote = data["quote"]
                formatted["underlying_price"] = float(quote.get("lastSalePrice", 
                                                               quote.get("price", 
                                                                       quote.get("last", 0))) or 0)
            elif "underlying" in data:
                underlying = data["underlying"]
                formatted["underlying_price"] = float(underlying.get("price", 
                                                                     underlying.get("last", 0)) or 0)
            
            # Process options if we found them
            if options_data:
                if isinstance(options_data, list):
                    # Direct list of options
                    for option in options_data[:strike_count * 2]:  # Get enough for calls and puts
                        self._process_option(option, formatted)
                elif isinstance(options_data, dict):
                    # Structured format with calls/puts
                    calls = options_data.get("calls", [])
                    puts = options_data.get("puts", [])
                    
                    for call in calls[:strike_count]:
                        self._process_option(call, formatted, "CALL")
                    
                    for put in puts[:strike_count]:
                        self._process_option(put, formatted, "PUT")
            
            # Sort strikes
            formatted["strikes"].sort()
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error parsing NASDAQ response: {e}")
            return None
    
    def _process_option(self, option: Dict, formatted: Dict, option_type: Optional[str] = None):
        """Process a single option and add it to formatted data"""
        try:
            # Determine option type
            if not option_type:
                option_type = option.get("type", option.get("optionType", "")).upper()
                if not option_type:
                    # Try to infer from symbol or other fields
                    symbol = option.get("symbol", "")
                    if "C" in symbol[-2:]:
                        option_type = "CALL"
                    elif "P" in symbol[-2:]:
                        option_type = "PUT"
            
            strike = float(option.get("strike", option.get("strikePrice", 0)) or 0)
            if strike <= 0:
                return
            
            option_data = {
                "symbol": option.get("symbol", option.get("contractSymbol", "")),
                "strike": strike,
                "bid": float(option.get("bid", option.get("bidPrice", 0)) or 0),
                "ask": float(option.get("ask", option.get("askPrice", 0)) or 0),
                "last": float(option.get("last", option.get("lastPrice", option.get("lastTradePrice", 0))) or 0),
                "volume": int(option.get("volume", option.get("totalVolume", 0)) or 0),
                "open_interest": int(option.get("openInterest", option.get("open_interest", 0)) or 0),
                "iv": float(option.get("impliedVolatility", option.get("iv", option.get("implied_volatility", 0))) or 0),
                "delta": float(option.get("delta", 0) or 0),
                "gamma": float(option.get("gamma", 0) or 0),
                "theta": float(option.get("theta", 0) or 0),
                "vega": float(option.get("vega", 0) or 0)
            }
            
            if option_type == "CALL" or option_type == "C":
                formatted["calls"].append(option_data)
            elif option_type == "PUT" or option_type == "P":
                formatted["puts"].append(option_data)
            
            if strike not in formatted["strikes"]:
                formatted["strikes"].append(strike)
                
        except Exception as e:
            logger.debug(f"Error processing option: {e}")
    
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

