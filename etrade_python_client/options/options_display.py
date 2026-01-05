"""Neat display module for options chain data"""
from typing import Dict, Any, Optional
import json

class OptionsChainDisplay:
    """Display options chain data in a neat, readable format"""
    
    @staticmethod
    def format_options_chain(chain_data: Dict[str, Any], max_strikes: Optional[int] = None) -> str:
        """
        Format options chain data for neat display
        
        :param chain_data: Options chain data dictionary
        :param max_strikes: Maximum number of strikes to display (None for all)
        :return: Formatted string representation
        """
        if not chain_data or "error" in chain_data:
            error_msg = chain_data.get("error", "No data available") if chain_data else "No data available"
            return f"Error: {error_msg}"
        
        symbol = chain_data.get("symbol", "N/A")
        expiry = chain_data.get("expiry_date", "N/A")
        underlying_price = chain_data.get("underlying_price", 0.0)
        provider = chain_data.get("provider", "Unknown")
        
        # Format expiry date if provided
        if expiry and expiry != "N/A" and len(expiry) == 8:
            expiry_formatted = f"{expiry[:4]}-{expiry[4:6]}-{expiry[6:8]}"
        else:
            expiry_formatted = expiry
        
        output = []
        output.append("=" * 100)
        output.append(f"OPTIONS CHAIN: {symbol} | Expiry: {expiry_formatted} | Underlying: ${underlying_price:.2f}")
        output.append(f"Data Source: {provider}")
        output.append("=" * 100)
        output.append("")
        
        calls = chain_data.get("calls", [])
        puts = chain_data.get("puts", [])
        strikes = chain_data.get("strikes", [])
        
        if not strikes:
            return "\n".join(output) + "\nNo options data available.\n"
        
        # Limit strikes if requested
        if max_strikes and len(strikes) > max_strikes:
            # Show strikes around ATM
            if underlying_price > 0:
                atm_strikes = sorted(strikes, key=lambda x: abs(x - underlying_price))[:max_strikes]
                strikes = sorted(atm_strikes)
            else:
                strikes = strikes[:max_strikes]
        
        # Create dictionaries for quick lookup
        calls_dict = {opt["strike"]: opt for opt in calls}
        puts_dict = {opt["strike"]: opt for opt in puts}
        
        # Header
        output.append(f"{'Strike':<10} | {'CALLS':<45} | {'PUTS':<45}")
        output.append("-" * 100)
        output.append(f"{'':<10} | {'Bid':<8} {'Ask':<8} {'Last':<8} {'Vol':<6} {'OI':<6} {'IV':<6} | "
                     f"{'Bid':<8} {'Ask':<8} {'Last':<8} {'Vol':<6} {'OI':<6} {'IV':<6}")
        output.append("-" * 100)
        
        # Display each strike
        for strike in strikes:
            call = calls_dict.get(strike, {})
            put = puts_dict.get(strike, {})
            
            # Format call data
            call_bid = f"{call.get('bid', 0):.2f}" if call else "-"
            call_ask = f"{call.get('ask', 0):.2f}" if call else "-"
            call_last = f"{call.get('last', 0):.2f}" if call else "-"
            call_vol = f"{call.get('volume', 0):,}" if call else "-"
            call_oi = f"{call.get('open_interest', 0):,}" if call else "-"
            call_iv = f"{call.get('iv', 0):.2%}" if call and call.get('iv', 0) > 0 else "-"
            
            # Format put data
            put_bid = f"{put.get('bid', 0):.2f}" if put else "-"
            put_ask = f"{put.get('ask', 0):.2f}" if put else "-"
            put_last = f"{put.get('last', 0):.2f}" if put else "-"
            put_vol = f"{put.get('volume', 0):,}" if put else "-"
            put_oi = f"{put.get('open_interest', 0):,}" if put else "-"
            put_iv = f"{put.get('iv', 0):.2%}" if put and put.get('iv', 0) > 0 else "-"
            
            # Highlight ATM strike
            strike_str = f"${strike:.2f}"
            if underlying_price > 0 and abs(strike - underlying_price) < (underlying_price * 0.01):
                strike_str = f"*{strike_str}*"  # Mark ATM
            
            output.append(f"{strike_str:<10} | "
                         f"{call_bid:<8} {call_ask:<8} {call_last:<8} {call_vol:<6} {call_oi:<6} {call_iv:<6} | "
                         f"{put_bid:<8} {put_ask:<8} {put_last:<8} {put_vol:<6} {put_oi:<6} {put_iv:<6}")
        
        output.append("-" * 100)
        output.append("* = At-the-Money (within 1% of underlying price)")
        output.append("")
        
        return "\n".join(output)
    
    @staticmethod
    def format_detailed_option(option_data: Dict[str, Any], option_type: str = "CALL") -> str:
        """
        Format detailed information for a single option
        
        :param option_data: Single option data dictionary
        :param option_type: "CALL" or "PUT"
        :return: Formatted string
        """
        output = []
        output.append(f"{option_type} Option Details:")
        output.append("-" * 60)
        output.append(f"Symbol: {option_data.get('symbol', 'N/A')}")
        output.append(f"Strike: ${option_data.get('strike', 0):.2f}")
        output.append(f"Bid: ${option_data.get('bid', 0):.2f}")
        output.append(f"Ask: ${option_data.get('ask', 0):.2f}")
        output.append(f"Last: ${option_data.get('last', 0):.2f}")
        output.append(f"Volume: {option_data.get('volume', 0):,}")
        output.append(f"Open Interest: {option_data.get('open_interest', 0):,}")
        output.append(f"Implied Volatility: {option_data.get('iv', 0):.2%}")
        output.append("")
        output.append("Greeks:")
        output.append(f"  Delta: {option_data.get('delta', 0):.4f}")
        output.append(f"  Gamma: {option_data.get('gamma', 0):.6f}")
        output.append(f"  Theta: {option_data.get('theta', 0):.4f}")
        output.append(f"  Vega: {option_data.get('vega', 0):.4f}")
        
        if 'time_value' in option_data:
            output.append(f"Time Value: ${option_data.get('time_value', 0):.2f}")
        if 'intrinsic_value' in option_data:
            output.append(f"Intrinsic Value: ${option_data.get('intrinsic_value', 0):.2f}")
        
        return "\n".join(output)
    
    @staticmethod
    def format_json(chain_data: Dict[str, Any], pretty: bool = True) -> str:
        """
        Format options chain as JSON
        
        :param chain_data: Options chain data
        :param pretty: Whether to format with indentation
        :return: JSON string
        """
        if pretty:
            return json.dumps(chain_data, indent=2, default=str)
        else:
            return json.dumps(chain_data, default=str)

