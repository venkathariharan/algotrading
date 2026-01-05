"""Unified options chain interface with multiple provider support"""
import logging
from typing import Dict, Optional, Any
from options.providers.provider_factory import OptionsProviderFactory

logger = logging.getLogger('my_logger')

class OptionsChain:
    """Unified options chain interface with multiple provider support"""
    
    def __init__(self, session=None, base_url=None, provider_name: Optional[str] = None):
        """
        Initialize options chain with configurable provider
        
        :param session: E*TRADE session (for E*TRADE provider)
        :param base_url: E*TRADE base URL (for E*TRADE provider)
        :param provider_name: Override provider selection ("ETRADE", "CBOE", "AUTO")
        """
        self.provider = OptionsProviderFactory.create_provider(
            session=session,
            base_url=base_url,
            provider_name=provider_name
        )
        logger.info(f"Using options chain provider: {self.provider.provider_name}")
    
    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None,
                         strike_count: int = 20) -> Dict[str, Any]:
        """
        Get options chain using configured provider
        
        :param symbol: Underlying symbol (e.g., "SPX")
        :param expiry_date: Expiry date in YYYYMMDD format
        :param strike_count: Number of strikes to return
        :return: Standardized options chain data
        """
        return self.provider.get_options_chain(symbol, expiry_date, strike_count)
    
    def get_spx_options(self, expiry_date: Optional[str] = None,
                       strike_count: int = 20) -> Dict[str, Any]:
        """Get SPX options chain"""
        return self.get_options_chain("SPX", expiry_date, strike_count)
    
    def switch_provider(self, provider_name: str, session=None, base_url=None):
        """
        Dynamically switch provider
        
        :param provider_name: "ETRADE" or "CBOE"
        :param session: E*TRADE session (if switching to E*TRADE)
        :param base_url: E*TRADE base URL (if switching to E*TRADE)
        """
        self.provider = OptionsProviderFactory.create_provider(
            session=session,
            base_url=base_url,
            provider_name=provider_name
        )
        logger.info(f"Switched to provider: {self.provider.provider_name}")

