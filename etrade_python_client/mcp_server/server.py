"""MCP Server for E*TRADE Trading Platform - JSON-RPC over stdio"""
import json
import logging
import sys
from typing import Any, Dict, List, Optional

from mcp_server.tools import EtradeTools
from options.options_display import OptionsChainDisplay

logger = logging.getLogger('my_logger')

# Lazy initialization - tools will be created on first use
_tools = None
_display = None

def get_tools():
    """Get or create EtradeTools instance (lazy initialization)"""
    global _tools
    if _tools is None:
        try:
            _tools = EtradeTools()
        except Exception as e:
            logger.error(f"Failed to initialize EtradeTools: {e}")
            # Return a dummy object that will return errors
            class DummyTools:
                def __getattr__(self, name):
                    def error_method(*args, **kwargs):
                        return {"error": f"E*TRADE client not initialized: {str(e)}"}
                    return error_method
            _tools = DummyTools()
    return _tools

def get_display():
    """Get or create OptionsChainDisplay instance (lazy initialization)"""
    global _display
    if _display is None:
        try:
            _display = OptionsChainDisplay()
        except Exception as e:
            logger.error(f"Failed to initialize OptionsChainDisplay: {e}")
            _display = OptionsChainDisplay()  # This should always work
    return _display

# Define available tools
AVAILABLE_TOOLS = {
    "get_accounts": {
        "name": "get_accounts",
        "description": "Get list of E*TRADE accounts",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    "get_account_balance": {
        "name": "get_account_balance",
        "description": "Get account balance for a specific account",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id_key": {
                    "type": "string",
                    "description": "Account ID key from get_accounts"
                }
            },
            "required": ["account_id_key"]
        }
    },
    "get_quote": {
        "name": "get_quote",
        "description": "Get real-time market quote for a symbol",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Stock or option symbol"
                }
            },
            "required": ["symbol"]
        }
    },
    "get_spx_options_chain": {
        "name": "get_spx_options_chain",
        "description": "Get SPX options chain from E*TRADE or CBOE with neat display showing calls and puts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "expiry_date": {
                    "type": "string",
                    "description": "Expiry date in YYYYMMDD format (optional)"
                },
                "strike_count": {
                    "type": "integer",
                    "description": "Number of strikes to return (default: 20)"
                },
                "provider": {
                    "type": "string",
                    "enum": ["ETRADE", "CBOE"],
                    "description": "Data source - ETRADE or CBOE (optional, uses config if not specified)"
                }
            },
            "required": []
        }
    },
    "get_options_chain": {
        "name": "get_options_chain",
        "description": "Get options chain for any symbol from E*TRADE or CBOE with neat display showing calls and puts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "symbol": {
                    "type": "string",
                    "description": "Underlying symbol (e.g., SPX, AAPL)"
                },
                "expiry_date": {
                    "type": "string",
                    "description": "Expiry date in YYYYMMDD format (optional)"
                },
                "strike_count": {
                    "type": "integer",
                    "description": "Number of strikes to return (default: 20)"
                },
                "provider": {
                    "type": "string",
                    "enum": ["ETRADE", "CBOE"],
                    "description": "Data source - ETRADE or CBOE (optional, uses config if not specified)"
                }
            },
            "required": ["symbol"]
        }
    },
    "place_order": {
        "name": "place_order",
        "description": "Place a stock or options order on E*TRADE",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id_key": {
                    "type": "string",
                    "description": "Account ID key (get from get_accounts)"
                },
                "symbol": {
                    "type": "string",
                    "description": "Stock or option symbol"
                },
                "action": {
                    "type": "string",
                    "enum": ["BUY", "SELL", "BUY_TO_COVER", "SELL_SHORT"],
                    "description": "Order action"
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of shares/contracts"
                },
                "price_type": {
                    "type": "string",
                    "enum": ["MARKET", "LIMIT"],
                    "description": "Price type (default: MARKET)"
                },
                "limit_price": {
                    "type": "number",
                    "description": "Limit price (required if price_type is LIMIT)"
                },
                "order_term": {
                    "type": "string",
                    "enum": ["GOOD_FOR_DAY", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"],
                    "description": "Order term (default: GOOD_FOR_DAY)"
                }
            },
            "required": ["account_id_key", "symbol", "action", "quantity"]
        }
    },
    "get_orders": {
        "name": "get_orders",
        "description": "Get orders for an account by status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id_key": {
                    "type": "string",
                    "description": "Account ID key (get from get_accounts)"
                },
                "status": {
                    "type": "string",
                    "enum": ["OPEN", "EXECUTED", "CANCELLED", "REJECTED", "EXPIRED", "INDIVIDUAL_FILLS"],
                    "description": "Order status (default: OPEN)"
                }
            },
            "required": ["account_id_key"]
        }
    },
    "get_order": {
        "name": "get_order",
        "description": "Get specific order details by order ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id_key": {
                    "type": "string",
                    "description": "Account ID key (get from get_accounts)"
                },
                "order_id": {
                    "type": "string",
                    "description": "Order ID"
                }
            },
            "required": ["account_id_key", "order_id"]
        }
    },
    "cancel_order": {
        "name": "cancel_order",
        "description": "Cancel an open order",
        "inputSchema": {
            "type": "object",
            "properties": {
                "account_id_key": {
                    "type": "string",
                    "description": "Account ID key (get from get_accounts)"
                },
                "order_id": {
                    "type": "string",
                    "description": "Order ID to cancel"
                }
            },
            "required": ["account_id_key", "order_id"]
        }
    }
}

def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle tool calls"""
    try:
        tools = get_tools()
        if name == "get_accounts":
            result = tools.get_accounts()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "get_account_balance":
            account_id_key = arguments.get("account_id_key")
            result = tools.get_account_balance(account_id_key)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "get_quote":
            symbol = arguments.get("symbol")
            result = tools.get_quote(symbol)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "get_spx_options_chain":
            expiry_date = arguments.get("expiry_date")
            strike_count = arguments.get("strike_count", 20)
            provider = arguments.get("provider")
            result = tools.get_spx_options(expiry_date, strike_count, provider)
            
            # Return formatted display
            if "formatted_display" in result:
                return {"content": [{"type": "text", "text": result["formatted_display"]}]}
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "get_options_chain":
            symbol = arguments.get("symbol")
            expiry_date = arguments.get("expiry_date")
            strike_count = arguments.get("strike_count", 20)
            provider = arguments.get("provider")
            result = tools.get_options_chain(symbol, expiry_date, strike_count, provider)
            
            # Return formatted display
            if "formatted_display" in result:
                return {"content": [{"type": "text", "text": result["formatted_display"]}]}
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "place_order":
            account_id_key = arguments.get("account_id_key")
            symbol = arguments.get("symbol")
            action = arguments.get("action")
            quantity = arguments.get("quantity")
            price_type = arguments.get("price_type", "MARKET")
            limit_price = arguments.get("limit_price")
            order_term = arguments.get("order_term", "GOOD_FOR_DAY")
            
            result = tools.place_order(
                account_id_key, symbol, action, quantity,
                price_type, limit_price, order_term
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "get_orders":
            account_id_key = arguments.get("account_id_key")
            status = arguments.get("status", "OPEN")
            result = tools.get_orders(account_id_key, status)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "get_order":
            account_id_key = arguments.get("account_id_key")
            order_id = arguments.get("order_id")
            result = tools.get_order(account_id_key, order_id)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif name == "cancel_order":
            account_id_key = arguments.get("account_id_key")
            order_id = arguments.get("order_id")
            result = tools.cancel_order(account_id_key, order_id)
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        else:
            return {"content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"})}]}
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}]}

def main():
    """Run the MCP server using JSON-RPC over stdio"""
    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            
            # Handle MCP protocol messages
            if request.get("method") == "initialize":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "etrade-trading-server",
                            "version": "1.0.0"
                        }
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            elif request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": list(AVAILABLE_TOOLS.values())
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            elif request.get("method") == "tools/call":
                tool_name = request.get("params", {}).get("name")
                arguments = request.get("params", {}).get("arguments", {})
                
                result = handle_tool_call(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
                print(json.dumps(response))
                sys.stdout.flush()
            
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {request.get('method')}"
                    }
                }
                print(json.dumps(response))
                sys.stdout.flush()
        
        except json.JSONDecodeError:
            # Skip invalid JSON
            continue
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(response))
            sys.stdout.flush()

if __name__ == "__main__":
    main()
