"""Test script for MCP tools (without MCP server)"""
import json
from mcp_server.tools import EtradeTools
from options.options_display import OptionsChainDisplay

def test_tools():
    """Test MCP tools functionality"""
    print("=" * 80)
    print("Testing E*TRADE MCP Tools")
    print("=" * 80)
    
    try:
        tools = EtradeTools()
        display = OptionsChainDisplay()
        
        # Test 1: Get accounts
        print("\n1. Testing get_accounts()...")
        accounts = tools.get_accounts()
        print(f"   Found {accounts.get('count', 0)} accounts")
        if accounts.get('accounts'):
            for acc in accounts['accounts'][:3]:  # Show first 3
                print(f"   - Account: {acc.get('accountIdKey', 'N/A')} ({acc.get('accountStatus', 'N/A')})")
        
        # Test 2: Get quote
        print("\n2. Testing get_quote('AAPL')...")
        quote = tools.get_quote("AAPL")
        if "error" not in quote:
            print("   Quote retrieved successfully")
        else:
            print(f"   Error: {quote.get('error')}")
        
        # Test 3: Get SPX options (E*TRADE)
        print("\n3. Testing get_spx_options() from E*TRADE...")
        spx_options = tools.get_spx_options(strike_count=5, provider="ETRADE")
        if "formatted_display" in spx_options:
            print("   Options chain retrieved successfully")
            print("\n   Sample display:")
            print(spx_options["formatted_display"][:500] + "...")
        elif "error" in spx_options:
            print(f"   Error: {spx_options.get('error')}")
        else:
            print("   Options chain retrieved (no display format)")
        
        # Test 4: Get SPX options (CBOE)
        print("\n4. Testing get_spx_options() from CBOE...")
        spx_options_cboe = tools.get_spx_options(strike_count=5, provider="CBOE")
        if "formatted_display" in spx_options_cboe:
            print("   Options chain retrieved successfully from CBOE")
        elif "error" in spx_options_cboe:
            print(f"   Error: {spx_options_cboe.get('error')}")
        else:
            print("   CBOE provider response received")
        
        # Test 5: Test new order management functions (if accounts available)
        if accounts.get('count', 0) > 0:
            account_id_key = accounts['accounts'][0].get('accountIdKey')
            print(f"\n5. Testing get_orders() with account {account_id_key[:10]}...")
            orders = tools.get_orders(account_id_key, "OPEN")
            if "error" not in orders:
                order_count = len(orders.get("OrdersResponse", {}).get("Order", []))
                print(f"   Found {order_count} open orders")
            else:
                print(f"   Error: {orders.get('error')}")
            
            print(f"\n6. Testing get_order() - checking if any orders exist...")
            if orders and "OrdersResponse" in orders and "Order" in orders["OrdersResponse"]:
                order_list = orders["OrdersResponse"]["Order"]
                if order_list and len(order_list) > 0:
                    order_id = order_list[0].get("orderId")
                    if order_id:
                        order_detail = tools.get_order(account_id_key, str(order_id))
                        if "error" not in order_detail:
                            print(f"   Order {order_id} retrieved successfully")
                        else:
                            print(f"   Error: {order_detail.get('error')}")
                else:
                    print("   No orders available to test get_order()")
            else:
                print("   No orders available to test get_order()")
        else:
            print("\n5. Skipping order management tests (no accounts available)")
            print("   Note: Order management functions require authentication")
        
        print("\n" + "=" * 80)
        print("Tests completed!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tools()

