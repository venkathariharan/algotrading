#!/usr/bin/env python
"""
E*TRADE Command Line Interface
Execute all E*TRADE functions directly from Python script
"""
import sys
import os
import json
import argparse
from typing import Optional

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp_server.tools import EtradeTools
from options.options_display import OptionsChainDisplay


def print_json(data, indent=2):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=indent))


def print_formatted_options(chain_data):
    """Print formatted options chain if available"""
    if "formatted_display" in chain_data:
        print("\n" + "=" * 80)
        print("OPTIONS CHAIN")
        print("=" * 80)
        print(chain_data["formatted_display"])
    elif "json_format" in chain_data:
        print("\n" + "=" * 80)
        print("OPTIONS CHAIN (JSON)")
        print("=" * 80)
        print(chain_data["json_format"])
    else:
        print_json(chain_data)


def get_default_account(tools: EtradeTools):
    """Get the first/default account ID key"""
    result = tools.get_accounts()
    if "error" in result or not result.get("accounts"):
        return None
    accounts = result.get("accounts", [])
    if accounts:
        return accounts[0].get("accountIdKey")
    return None


def get_accounts(tools: EtradeTools):
    """Get and display all accounts"""
    print("\n" + "=" * 80)
    print("E*TRADE ACCOUNTS")
    print("=" * 80)
    result = tools.get_accounts()
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return result
    
    accounts = result.get("accounts", [])
    count = result.get("count", 0)
    
    print(f"\nTotal Accounts: {count}\n")
    
    for i, acc in enumerate(accounts, 1):
        print(f"Account {i}: {acc.get('accountName', 'N/A')}")
        print(f"  Account ID: {acc.get('accountId')}")
        print(f"  Account ID Key: {acc.get('accountIdKey')}")
        print(f"  Type: {acc.get('accountDesc')} ({acc.get('accountType')})")
        print(f"  Mode: {acc.get('accountMode')}")
        print(f"  Status: {acc.get('accountStatus')}")
        print()
    
    return result


def get_account_balance(tools: EtradeTools, account_id_key: Optional[str] = None):
    """Get and display account balance"""
    if not account_id_key:
        account_id_key = get_default_account(tools)
        if not account_id_key:
            print("Error: No accounts found and no account_id_key provided")
            return {"error": "No accounts found"}
        print(f"Using default account: {account_id_key}")
    
    print("\n" + "=" * 80)
    print(f"ACCOUNT BALANCE")
    print("=" * 80)
    result = tools.get_account_balance(account_id_key)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return result
    
    print_json(result)
    return result


def get_quote(tools: EtradeTools, symbol: str):
    """Get and display market quote"""
    print("\n" + "=" * 80)
    print(f"MARKET QUOTE: {symbol.upper()}")
    print("=" * 80)
    result = tools.get_quote(symbol.upper())
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return result
    
    print_json(result)
    return result


def get_options_chain(tools: EtradeTools, symbol: str, expiry_date: Optional[str] = None,
                     strike_count: int = 20, provider: Optional[str] = None):
    """Get and display options chain"""
    print("\n" + "=" * 80)
    print(f"OPTIONS CHAIN: {symbol.upper()}")
    print("=" * 80)
    if expiry_date:
        print(f"Expiry Date: {expiry_date}")
    print(f"Strike Count: {strike_count}")
    if provider:
        print(f"Provider: {provider}")
    
    result = tools.get_options_chain(symbol.upper(), expiry_date, strike_count, provider)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return result
    
    print_formatted_options(result)
    return result


def get_spx_options(tools: EtradeTools, expiry_date: Optional[str] = None,
                   strike_count: int = 20, provider: Optional[str] = None):
    """Get and display SPX options chain"""
    return get_options_chain(tools, "SPX", expiry_date, strike_count, provider)


def place_order(tools: EtradeTools, symbol: str, action: str,
               quantity: int, account_id_key: Optional[str] = None,
               price_type: str = "MARKET", limit_price: Optional[float] = None,
               order_term: str = "GOOD_FOR_DAY"):
    """Place an order"""
    if not account_id_key:
        account_id_key = get_default_account(tools)
        if not account_id_key:
            print("Error: No accounts found and no account_id_key provided")
            return {"error": "No accounts found"}
        print(f"Using default account: {account_id_key}")
    
    print("\n" + "=" * 80)
    print("PLACE ORDER")
    print("=" * 80)
    print(f"Account: {account_id_key}")
    print(f"Symbol: {symbol.upper()}")
    print(f"Action: {action}")
    print(f"Quantity: {quantity}")
    print(f"Price Type: {price_type}")
    if limit_price:
        print(f"Limit Price: ${limit_price:.2f}")
    print(f"Order Term: {order_term}")
    print("\nPlacing order...")
    
    result = tools.place_order(
        account_id_key, symbol.upper(), action, quantity,
        price_type, limit_price, order_term
    )
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    elif result.get("success"):
        print("\n[SUCCESS] Order placed!")
        print(f"Order ID: {result.get('order_id')}")
        print(f"Preview ID: {result.get('preview_id')}")
    else:
        print_json(result)
    
    return result


def get_orders(tools: EtradeTools, status: str = "OPEN", account_id_key: Optional[str] = None):
    """Get orders for an account"""
    if not account_id_key:
        account_id_key = get_default_account(tools)
        if not account_id_key:
            print("Error: No accounts found and no account_id_key provided")
            return {"error": "No accounts found"}
        print(f"Using default account: {account_id_key}")
    
    print("\n" + "=" * 80)
    print(f"ORDERS (Status: {status})")
    print("=" * 80)
    result = tools.get_orders(account_id_key, status)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return result
    
    orders = result.get("OrdersResponse", {}).get("Order", [])
    if not orders:
        print(f"No {status.lower()} orders found.")
    else:
        print(f"Found {len(orders)} order(s):\n")
        for i, order in enumerate(orders, 1):
            print(f"Order {i}:")
            print(f"  Order ID: {order.get('orderId', 'N/A')}")
            
            # Parse order details - structure is Order -> OrderDetail[] -> Instrument[] -> Product
            symbol = 'N/A'
            action = 'N/A'
            quantity = 'N/A'
            price_type = 'N/A'
            limit_price = 'N/A'
            order_status = 'N/A'
            
            if "OrderDetail" in order and order["OrderDetail"]:
                details = order["OrderDetail"][0] if isinstance(order["OrderDetail"], list) else order["OrderDetail"]
                if "Instrument" in details and details["Instrument"]:
                    instrument = details["Instrument"][0] if isinstance(details["Instrument"], list) else details["Instrument"]
                    if "Product" in instrument and "symbol" in instrument["Product"]:
                        symbol = instrument["Product"]["symbol"]
                    if "orderAction" in instrument:
                        action = instrument["orderAction"]
                    if "orderedQuantity" in instrument:
                        quantity = instrument["orderedQuantity"]
                    elif "quantity" in instrument:
                        quantity = instrument["quantity"]
                
                if "priceType" in details:
                    price_type = details["priceType"]
                if "limitPrice" in details:
                    limit_price = f"${details['limitPrice']:.2f}" if details['limitPrice'] else 'N/A'
                if "status" in details:
                    order_status = details["status"]
            
            print(f"  Symbol: {symbol}")
            print(f"  Action: {action}")
            print(f"  Quantity: {quantity}")
            print(f"  Price Type: {price_type}")
            if limit_price != 'N/A':
                print(f"  Limit Price: {limit_price}")
            print(f"  Status: {order_status}")
            print()
    
    return result


def get_order(tools: EtradeTools, order_id: str, account_id_key: Optional[str] = None):
    """Get specific order details"""
    if not account_id_key:
        account_id_key = get_default_account(tools)
        if not account_id_key:
            print("Error: No accounts found and no account_id_key provided")
            return {"error": "No accounts found"}
        print(f"Using default account: {account_id_key}")
    
    print("\n" + "=" * 80)
    print(f"ORDER DETAILS: {order_id}")
    print("=" * 80)
    result = tools.get_order(account_id_key, order_id)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return result
    
    print_json(result)
    return result


def cancel_order(tools: EtradeTools, order_id: str, account_id_key: Optional[str] = None):
    """Cancel an order"""
    if not account_id_key:
        account_id_key = get_default_account(tools)
        if not account_id_key:
            print("Error: No accounts found and no account_id_key provided")
            return {"error": "No accounts found"}
        print(f"Using default account: {account_id_key}")
    
    print("\n" + "=" * 80)
    print(f"CANCEL ORDER: {order_id}")
    print("=" * 80)
    print("Cancelling order...")
    
    result = tools.cancel_order(account_id_key, order_id)
    
    if "error" in result:
        print(f"\nError: {result['error']}")
    else:
        print("\n[SUCCESS] Order cancelled!")
        print_json(result)
    
    return result


def interactive_mode():
    """Interactive command mode"""
    tools = EtradeTools()
    
    print("=" * 80)
    print("E*TRADE Command Line Interface - Interactive Mode")
    print("=" * 80)
    print("\nAvailable commands:")
    print("  1. accounts              - List all accounts")
    print("  2. balance [id_key]      - Get account balance (uses default if not provided)")
    print("  3. quote <symbol>        - Get market quote")
    print("  4. options <symbol>      - Get options chain")
    print("  5. spx                   - Get SPX options chain")
    print("  6. place <symbol> <action> <qty> [id_key] [price_type] [limit_price]")
    print("  7. orders [id_key] [status] - Get orders (uses default account if not provided)")
    print("  8. order <order_id> [id_key] - Get order details")
    print("  9. cancel <order_id> [id_key] - Cancel order")
    print("  10. help                 - Show this help")
    print("  11. exit                 - Exit")
    print("\nNote: Account ID key is optional - will use first account if not provided")
    print("\nExample: quote AAPL")
    print("Example: place AAPL BUY 1 MARKET")
    print("Example: orders OPEN")
    print("=" * 80)
    
    while True:
        try:
            cmd = input("\n> ").strip().split()
            if not cmd:
                continue
            
            command = cmd[0].lower()
            
            if command == "exit" or command == "quit":
                print("Goodbye!")
                break
            elif command == "help":
                print("\nAvailable commands:")
                print("  accounts              - List all accounts")
                print("  balance [id_key]      - Get account balance (uses default if not provided)")
                print("  quote <symbol>        - Get market quote")
                print("  options <symbol> [expiry] [strikes] [provider] - Get options chain")
                print("  spx [expiry] [strikes] [provider] - Get SPX options")
                print("  place <symbol> <action> <qty> [id_key] [price_type] [limit_price] [term]")
                print("  orders [id_key] [status] - Get orders (uses default account if not provided)")
                print("  order <order_id> [id_key] - Get order details")
                print("  cancel <order_id> [id_key] - Cancel order")
                print("  exit                  - Exit")
                print("\nNote: Account ID key is optional - will use first account if not provided")
            elif command == "accounts":
                get_accounts(tools)
            elif command == "balance":
                account_id = cmd[1] if len(cmd) > 1 else None
                get_account_balance(tools, account_id)
            elif command == "quote":
                if len(cmd) < 2:
                    print("Error: Missing symbol")
                    print("Usage: quote <symbol>")
                else:
                    get_quote(tools, cmd[1])
            elif command == "options":
                if len(cmd) < 2:
                    print("Error: Missing symbol")
                    print("Usage: options <symbol> [expiry_date] [strike_count] [provider]")
                else:
                    expiry = cmd[2] if len(cmd) > 2 else None
                    strikes = int(cmd[3]) if len(cmd) > 3 else 20
                    provider = cmd[4] if len(cmd) > 4 else None
                    get_options_chain(tools, cmd[1], expiry, strikes, provider)
            elif command == "spx":
                expiry = cmd[1] if len(cmd) > 1 else None
                strikes = int(cmd[2]) if len(cmd) > 2 else 20
                provider = cmd[3] if len(cmd) > 3 else None
                get_spx_options(tools, expiry, strikes, provider)
            elif command == "place":
                if len(cmd) < 4:
                    print("Error: Missing required parameters")
                    print("Usage: place <symbol> <action> <quantity> [account_id_key] [price_type] [limit_price] [order_term]")
                else:
                    symbol = cmd[1]
                    action = cmd[2]
                    quantity = int(cmd[3])
                    # Check if 4th arg is account_id or price_type
                    if len(cmd) > 4:
                        # If 4th arg looks like an account_id (long string), it's account_id
                        if len(cmd[4]) > 20:
                            account_id = cmd[4]
                            price_type = cmd[5] if len(cmd) > 5 else "MARKET"
                            limit_price = float(cmd[6]) if len(cmd) > 6 and price_type == "LIMIT" else None
                            order_term = cmd[7] if len(cmd) > 7 else "GOOD_FOR_DAY"
                        else:
                            # 4th arg is price_type
                            account_id = None
                            price_type = cmd[4]
                            limit_price = float(cmd[5]) if len(cmd) > 5 and price_type == "LIMIT" else None
                            order_term = cmd[6] if len(cmd) > 6 else "GOOD_FOR_DAY"
                    else:
                        account_id = None
                        price_type = "MARKET"
                        limit_price = None
                        order_term = "GOOD_FOR_DAY"
                    place_order(tools, symbol, action, quantity, account_id, price_type, limit_price, order_term)
            elif command == "orders":
                # Check if first arg is account_id or status
                if len(cmd) > 1:
                    if len(cmd[1]) > 20:  # Looks like account_id
                        account_id = cmd[1]
                        status = cmd[2] if len(cmd) > 2 else "OPEN"
                    else:  # First arg is status
                        account_id = None
                        status = cmd[1]
                else:
                    account_id = None
                    status = "OPEN"
                get_orders(tools, status, account_id)
            elif command == "order":
                if len(cmd) < 2:
                    print("Error: Missing order_id")
                    print("Usage: order <order_id> [account_id_key]")
                else:
                    order_id = cmd[1]
                    account_id = cmd[2] if len(cmd) > 2 else None
                    get_order(tools, order_id, account_id)
            elif command == "cancel":
                if len(cmd) < 2:
                    print("Error: Missing order_id")
                    print("Usage: cancel <order_id> [account_id_key]")
                else:
                    order_id = cmd[1]
                    account_id = cmd[2] if len(cmd) > 2 else None
                    cancel_order(tools, order_id, account_id)
            else:
                print(f"Unknown command: {command}")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="E*TRADE Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python etrade_cli.py

  # Get accounts
  python etrade_cli.py accounts

  # Get quote
  python etrade_cli.py quote AAPL

  # Get options chain
  python etrade_cli.py options AAPL --strikes 20

  # Place order
  python etrade_cli.py place --account-id <id> --symbol AAPL --action BUY --quantity 1

  # Get orders
  python etrade_cli.py orders --account-id <id> --status OPEN
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Accounts command
    subparsers.add_parser("accounts", help="List all accounts")
    
    # Balance command
    balance_parser = subparsers.add_parser("balance", help="Get account balance")
    balance_parser.add_argument("--account-id", help="Account ID key (optional, uses first account if not provided)")
    
    # Quote command
    quote_parser = subparsers.add_parser("quote", help="Get market quote")
    quote_parser.add_argument("symbol", help="Stock symbol")
    
    # Options command
    options_parser = subparsers.add_parser("options", help="Get options chain")
    options_parser.add_argument("symbol", help="Underlying symbol")
    options_parser.add_argument("--expiry", help="Expiry date (YYYYMMDD)")
    options_parser.add_argument("--strikes", type=int, default=20, help="Number of strikes (default: 20)")
    options_parser.add_argument("--provider", choices=["ETRADE", "CBOE"], help="Data provider")
    
    # SPX options command
    spx_parser = subparsers.add_parser("spx", help="Get SPX options chain")
    spx_parser.add_argument("--expiry", help="Expiry date (YYYYMMDD)")
    spx_parser.add_argument("--strikes", type=int, default=20, help="Number of strikes (default: 20)")
    spx_parser.add_argument("--provider", choices=["ETRADE", "CBOE"], help="Data provider")
    
    # Place order command
    place_parser = subparsers.add_parser("place", help="Place an order")
    place_parser.add_argument("--account-id", help="Account ID key (optional, uses first account if not provided)")
    place_parser.add_argument("--symbol", required=True, help="Stock symbol")
    place_parser.add_argument("--action", required=True, choices=["BUY", "SELL", "BUY_TO_COVER", "SELL_SHORT"], help="Order action")
    place_parser.add_argument("--quantity", type=int, required=True, help="Number of shares/contracts")
    place_parser.add_argument("--price-type", default="MARKET", choices=["MARKET", "LIMIT"], help="Price type")
    place_parser.add_argument("--limit-price", type=float, help="Limit price (required if price-type is LIMIT)")
    place_parser.add_argument("--order-term", default="GOOD_FOR_DAY", choices=["GOOD_FOR_DAY", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL"], help="Order term")
    
    # Orders command
    orders_parser = subparsers.add_parser("orders", help="Get orders")
    orders_parser.add_argument("--account-id", help="Account ID key (optional, uses first account if not provided)")
    orders_parser.add_argument("--status", default="OPEN", choices=["OPEN", "EXECUTED", "CANCELLED", "REJECTED", "EXPIRED", "INDIVIDUAL_FILLS"], help="Order status")
    
    # Order command
    order_parser = subparsers.add_parser("order", help="Get order details")
    order_parser.add_argument("--account-id", help="Account ID key (optional, uses first account if not provided)")
    order_parser.add_argument("--order-id", required=True, help="Order ID")
    
    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an order")
    cancel_parser.add_argument("--account-id", help="Account ID key (optional, uses first account if not provided)")
    cancel_parser.add_argument("--order-id", required=True, help="Order ID")
    
    args = parser.parse_args()
    
    # If no command provided, start interactive mode
    if not args.command:
        interactive_mode()
        return
    
    # Initialize tools
    tools = EtradeTools()
    
    # Execute command
    try:
        if args.command == "accounts":
            get_accounts(tools)
        elif args.command == "balance":
            get_account_balance(tools, getattr(args, 'account_id', None))
        elif args.command == "quote":
            get_quote(tools, args.symbol)
        elif args.command == "options":
            get_options_chain(tools, args.symbol, args.expiry, args.strikes, args.provider)
        elif args.command == "spx":
            get_spx_options(tools, args.expiry, args.strikes, args.provider)
        elif args.command == "place":
            if args.price_type == "LIMIT" and not args.limit_price:
                print("Error: --limit-price is required when --price-type is LIMIT")
                sys.exit(1)
            place_order(tools, args.symbol, args.action, args.quantity,
                       getattr(args, 'account_id', None), args.price_type, args.limit_price, args.order_term)
        elif args.command == "orders":
            get_orders(tools, args.status, getattr(args, 'account_id', None))
        elif args.command == "order":
            get_order(tools, args.order_id, getattr(args, 'account_id', None))
        elif args.command == "cancel":
            cancel_order(tools, args.order_id, getattr(args, 'account_id', None))
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

