"""Base provider interface for options chain data"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger('my_logger')

class OptionsChainProvider(ABC):
    """Abstract base class for options chain data providers"""
    
    @abstractmethod
    def get_options_chain(self, symbol: str, expiry_date: Optional[str] = None, 
                         strike_count: int = 20) -> Dict[str, Any]:
        """
        Get options chain data
        
        :param symbol: Underlying symbol (e.g., "SPX")
        :param expiry_date: Expiry date in YYYYMMDD format
        :param strike_count: Number of strikes to return
        :return: Dictionary with options chain data
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider is available/configured
        
        :return: True if provider can be used
        """
        pass
    
    def _format_response(self, raw_data: Any) -> Dict[str, Any]:
        """
        Format provider-specific response to standard format
        
        :param raw_data: Raw data from provider
        :return: Standardized options chain format
        """
        return {
            "calls": [],
            "puts": [],
            "strikes": [],
            "underlying_price": 0.0,
            "expiry_date": None,
            "provider": self.__class__.__name__
        }

