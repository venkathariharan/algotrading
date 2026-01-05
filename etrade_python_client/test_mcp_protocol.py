"""Test MCP server protocol directly"""
import json
import subprocess
import sys
import os

def test_mcp_protocol():
    """Test MCP server protocol communication"""
    print("=" * 80)
    print("Testing MCP Server Protocol")
    print("=" * 80)
    
    # Get paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = os.path.join(script_dir, "venv", "Scripts", "python.exe")
    server_script = os.path.join(script_dir, "mcp_server", "server.py")
    
    if not os.path.exists(python_exe):
        print(f"ERROR: Python executable not found at {python_exe}")
        return False
    
    if not os.path.exists(server_script):
        print(f"ERROR: Server script not found at {server_script}")
        return False
    
    # Set environment
    env = os.environ.copy()
    env["PYTHONPATH"] = script_dir
    
    try:
        # Start server process
        print("\n1. Starting MCP server...")
        process = subprocess.Popen(
            [python_exe, server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
            cwd=script_dir
        )
        
        # Test 1: Initialize
        print("\n2. Testing initialize...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        init_response = process.stdout.readline()
        if init_response:
            init_data = json.loads(init_response.strip())
            if init_data.get("result", {}).get("serverInfo", {}).get("name") == "etrade-trading-server":
                print("   [OK] Initialize successful")
            else:
                print(f"   [FAIL] Initialize failed: {init_data}")
                return False
        
        # Test 2: List tools
        print("\n3. Testing tools/list...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        process.stdin.write(json.dumps(list_request) + "\n")
        process.stdin.flush()
        
        list_response = process.stdout.readline()
        if list_response:
            list_data = json.loads(list_response.strip())
            tools = list_data.get("result", {}).get("tools", [])
            tool_names = [t.get("name") for t in tools]
            print(f"   [OK] Found {len(tools)} tools")
            print(f"   Tools: {', '.join(tool_names[:5])}...")
            
            # Verify new tools are present
            expected_tools = ["get_accounts", "get_orders", "get_order", "cancel_order", "place_order"]
            missing = [t for t in expected_tools if t not in tool_names]
            if missing:
                print(f"   [FAIL] Missing tools: {missing}")
                return False
            else:
                print("   [OK] All expected tools present")
        
        # Test 3: Call get_accounts (may fail without auth, but should handle gracefully)
        print("\n4. Testing tools/call (get_accounts)...")
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_accounts",
                "arguments": {}
            }
        }
        process.stdin.write(json.dumps(call_request) + "\n")
        process.stdin.flush()
        
        call_response = process.stdout.readline()
        if call_response:
            call_data = json.loads(call_response.strip())
            if "result" in call_data or "error" in call_data:
                print("   [OK] Tool call handled (may return error if not authenticated)")
            else:
                print(f"   [FAIL] Unexpected response: {call_data}")
        
        # Cleanup
        process.stdin.close()
        process.terminate()
        process.wait(timeout=5)
        
        print("\n" + "=" * 80)
        print("MCP Protocol Tests Completed!")
        print("=" * 80)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        if 'process' in locals():
            process.terminate()
        return False

if __name__ == "__main__":
    success = test_mcp_protocol()
    sys.exit(0 if success else 1)

