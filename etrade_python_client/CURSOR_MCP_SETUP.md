# Cursor IDE MCP Integration Guide

## ✅ Yes! Cursor Supports MCP

Cursor IDE has built-in support for Model Context Protocol (MCP) servers. You can integrate your E*TRADE trading MCP server directly into Cursor!

## Prerequisites

1. **Cursor IDE installed** - You're already using it! ✅
2. **Your MCP server** - Already set up and working ✅
3. **Python environment** - Already configured ✅

## Step 1: Open Cursor Settings

1. **Open Cursor Settings:**
   - Press `Ctrl+Shift+J` (Windows/Linux) or `Cmd+Shift+J` (Mac)
   - OR click the gear icon (⚙️) → Settings
   - OR go to File → Preferences → Settings

2. **Navigate to MCP Settings:**
   - Look for "MCP" or "Model Context Protocol" in the settings
   - OR search for "MCP" in the settings search bar

## Step 2: Add MCP Server Configuration

1. **Click "Add MCP Server" or "Add new global MCP server"**
   - This will open the `mcp.json` configuration file

2. **Edit the `mcp.json` file** with your E*TRADE server configuration:

```json
{
  "mcpServers": {
    "etrade-trading": {
      "command": "C:\\Cursor-coding\\algotrading\\etrade_python_client\\venv\\Scripts\\python.exe",
      "args": [
        "C:\\Cursor-coding\\algotrading\\etrade_python_client\\mcp_server\\server.py"
      ],
      "env": {
        "PYTHONPATH": "C:\\Cursor-coding\\algotrading\\etrade_python_client"
      }
    }
  }
}
```

**Important Notes:**
- Use double backslashes (`\\`) in Windows paths
- Make sure paths match your actual installation
- The `command` should point to your venv Python executable
- The `args` should point to your `server.py` file

## Step 3: Verify Paths

Before configuring, verify your paths are correct:

```powershell
# Get Python path
cd C:\Cursor-coding\algotrading\etrade_python_client
Resolve-Path "venv\Scripts\python.exe"

# Get server path
Resolve-Path "mcp_server\server.py"
```

## Step 4: Save and Restart

1. **Save the `mcp.json` file**
2. **Restart Cursor** to apply the changes
3. The MCP server should be automatically loaded

## Step 5: Verify Integration

1. **Check MCP Tools:**
   - Open the MCP Tools section in Cursor (if available)
   - Ensure your MCP server is listed and enabled

2. **Test the Integration:**
   - Open the chat panel in Cursor (usually `Ctrl+L` or `Cmd+L`)
   - Try prompts like:
     - "Show me my E*TRADE accounts"
     - "Get SPX options chain"
     - "What's the price of AAPL?"

## Alternative: Manual Config File Location

If you can't find the MCP settings in the UI, you can manually create/edit the config file:

**Windows:**
```
%APPDATA%\Cursor\mcp.json
```
or
```
%USERPROFILE%\.cursor\mcp.json
```

**macOS:**
```
~/Library/Application Support/Cursor/mcp.json
```

**Linux:**
```
~/.config/Cursor/mcp.json
```

## Available MCP Tools in Cursor

Once integrated, you can use these tools in Cursor's chat:

1. **get_accounts** - List all E*TRADE accounts
2. **get_account_balance** - Get balance for specific account
3. **get_quote** - Get market quote for symbol
4. **get_spx_options_chain** - Get SPX options (calls & puts)
5. **get_options_chain** - Get options for any symbol
6. **place_order** - Place stock/options order

## Example Usage in Cursor

Once set up, you can use natural language in Cursor's chat:

**You:** "Show me my E*TRADE accounts"
**Cursor:** [Uses get_accounts tool] Shows your 3 accounts

**You:** "Get SPX options chain with 30 strikes"
**Cursor:** [Uses get_spx_options_chain tool] Shows formatted options table

**You:** "What's the current price of Microsoft stock?"
**Cursor:** [Uses get_quote tool] Shows MSFT quote

**You:** "Get options chain for Apple with 25 strikes"
**Cursor:** [Uses get_options_chain tool] Shows AAPL options

## Troubleshooting

### MCP Settings Not Visible

1. **Check Cursor Version:**
   - Make sure you have the latest version of Cursor
   - MCP support may require a recent version

2. **Check Settings Location:**
   - Try searching for "MCP" in settings
   - Look in Advanced Settings or Extensions

3. **Manual Config:**
   - Create the config file manually (see paths above)

### Server Won't Start

1. **Verify Python path:**
   ```powershell
   C:\Cursor-coding\algotrading\etrade_python_client\venv\Scripts\python.exe --version
   ```

2. **Check server file exists:**
   ```powershell
   Test-Path "C:\Cursor-coding\algotrading\etrade_python_client\mcp_server\server.py"
   ```

3. **Test server manually:**
   ```powershell
   cd C:\Cursor-coding\algotrading\etrade_python_client
   $env:PYTHONPATH="C:\Cursor-coding\algotrading\etrade_python_client"
   echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | .\venv\Scripts\python.exe mcp_server\server.py
   ```

### Tools Not Appearing

1. **Restart Cursor completely**
2. **Check Cursor logs** for MCP-related errors
3. **Verify config JSON syntax** is valid
4. **Check authentication** - make sure `oauth_tokens.json` exists

## Benefits of Using MCP in Cursor

✅ **Integrated Development:**
- Access trading tools directly from your IDE
- No need to switch between applications

✅ **Code-Aware Trading:**
- Ask Cursor about market data while coding
- Get options chain data in your development workflow

✅ **Natural Language:**
- Use plain English to interact with trading tools
- Cursor understands context from your code

✅ **Seamless Workflow:**
- Everything in one place
- No external tools needed

## Quick Reference

**Config File:**
```
%APPDATA%\Cursor\mcp.json
```

**Python Path:**
```
C:\Cursor-coding\algotrading\etrade_python_client\venv\Scripts\python.exe
```

**Server Path:**
```
C:\Cursor-coding\algotrading\etrade_python_client\mcp_server\server.py
```

**Your Account IDs:**
- `dBZOKt9xDrtRSAOl4MSiiA` (Brokerage)
- `vQMsebA1H5WltUfDkJP48g` (Complete Savings)
- `6_Dpy0rmuQ9cu9IbTfvF2A` (INDIVIDUAL)

## Next Steps

1. Open Cursor Settings (`Ctrl+Shift+J`)
2. Find MCP settings
3. Add your E*TRADE server configuration
4. Restart Cursor
5. Start chatting with your trading tools!

## Additional Resources

- [Cursor MCP Documentation](https://docs.cursor.com/context/model-context-protocol)
- Your MCP server is already tested and working ✅
- All tools are functional and ready to use ✅

Enjoy trading directly from Cursor! 🚀














