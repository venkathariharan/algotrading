"""Factory to create and manage options chain providers"""
import configparser
import os
import logging
from typing import Optional
from options.providers.base_provider import OptionsChainProvider
from options.providers.etrade_provider import EtradeOptionsProvider
from options.providers.cboe_provider import CBOEOptionsProvider
from options.providers.nasdaq_provider import NASDAQOptionsProvider

logger = logging.getLogger('my_logger')

class OptionsProviderFactory:
    """Factory to create and manage options chain providers"""
    
    @staticmethod
    def create_provider(session=None, base_url=None, 
                       provider_name: Optional[str] = None) -> OptionsChainProvider:
        """
        Create options chain provider based on configuration
        
        :param session: E*TRADE session (required for E*TRADE provider)
        :param base_url: E*TRADE base URL (required for E*TRADE provider)
        :param provider_name: Override config - "ETRADE", "CBOE", or "AUTO"
        :return: OptionsChainProvider instance
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.ini')
        config.read(config_path)
        
        # Get provider preference from config or parameter
        if provider_name is None:
            provider_name = config.get('OPTIONS_CHAIN', 'DATA_SOURCE', fallback='AUTO')
        
        provider_name = provider_name.upper()
        
        if provider_name == "ETRADE":
            if session and base_url:
                provider = EtradeOptionsProvider(session, base_url)
                if provider.is_available():
                    return provider
                else:
                    logger.warning("E*TRADE provider not available, falling back to NASDAQ")
                    return NASDAQOptionsProvider()
            else:
                logger.warning("E*TRADE provider requires session and base_url")
                return NASDAQOptionsProvider()
        
        elif provider_name == "CBOE":
            return CBOEOptionsProvider()
        
        elif provider_name == "NASDAQ":
            return NASDAQOptionsProvider()
        
        elif provider_name == "AUTO":
            # Try E*TRADE first, fall back to NASDAQ, then CBOE
            if session and base_url:
                etrade_provider = EtradeOptionsProvider(session, base_url)
                if etrade_provider.is_available():
                    return etrade_provider
            
            # Try NASDAQ
            nasdaq_provider = NASDAQOptionsProvider()
            if nasdaq_provider.is_available():
                logger.info("Using NASDAQ provider as fallback")
                return nasdaq_provider
            
            # Fall back to CBOE
            cboe_provider = CBOEOptionsProvider()
            if cboe_provider.is_available():
                logger.info("Using CBOE provider as fallback")
                return cboe_provider
            else:
                raise Exception("No available options chain provider")
        
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    @staticmethod
    def get_available_providers() -> list:
        """Get list of available provider names"""
        return ["ETRADE", "NASDAQ", "CBOE", "AUTO"]

