# E*TRADE Python Client - File Documentation

This document provides detailed documentation for each file in the E*TRADE Python Client codebase.

## Table of Contents

1. [Main Application Files](#main-application-files)
2. [Account Management](#account-management)
3. [Market Data](#market-data)
4. [Order Management](#order-management)
5. [Options Trading](#options-trading)
6. [MCP Server](#mcp-server)
7. [Configuration Files](#configuration-files)
8. [Test Files](#test-files)

---

## Main Application Files

### `etrade_python_client.py`

**Purpose**: Main OAuth authentication script for E*TRADE API access.

**Key Functions**:
- `save_tokens()`: Saves OAuth tokens to `oauth_tokens.json`
- `load_tokens()`: Loads OAuth tokens from file
- `test_token_validity()`: Validates existing tokens by making a test API call
- `oauth()`: Main OAuth 1.0 authentication flow

**Features**:
- Supports both Sandbox and Production environments
- Interactive environment selection
- Token validation and refresh
- Automatic browser opening for authorization
- Token persistence to JSON file

**Dependencies**:
- `rauth`: OAuth 1.0 authentication
- `configparser`: Configuration file reading
- `json`: Token storage

**Usage**:
```bash
python etrade_python_client.py
```

**Output**: Creates `oauth_tokens.json` with authentication credentials.

---

### `etrade_cli.py`

**Purpose**: Command-line interface for E*TRADE operations.

**Key Functions**:
- `get_accounts()`: List all E*TRADE accounts
- `get_account_balance()`: Get account balance
- `get_quote()`: Get market quote for a symbol
- `get_options_chain()`: Get options chain
- `get_spx_options()`: Get SPX options chain
- `place_order()`: Place a stock/options order
- `get_orders()`: Get orders by status
- `get_order()`: Get specific order details
- `cancel_order()`: Cancel an open order
- `interactive_mode()`: Interactive command mode

**Features**:
- Both command-line and interactive modes
- Supports all major E*TRADE operations
- Pretty-printed output with formatted tables
- Error handling and validation

**Command Examples**:
```bash
# Interactive mode
python etrade_cli.py

# Get accounts
python etrade_cli.py accounts

# Get quote
python etrade_cli.py quote AAPL

# Get options chain
python etrade_cli.py options AAPL --strikes 20

# Place order
python etrade_cli.py place --symbol AAPL --action BUY --quantity 10

# Get open orders
python etrade_cli.py orders --status OPEN
```

**Dependencies**:
- `mcp_server.tools.EtradeTools`: Core trading operations
- `options.options_display.OptionsChainDisplay`: Options formatting
- `argparse`: Command-line argument parsing

---

## Account Management

### `accounts/accounts.py`

**Purpose**: Account management operations for E*TRADE accounts.

**Class**: `Accounts`

**Key Methods**:
- `__init__(session, base_url)`: Initialize with authenticated session
- `account_list()`: Retrieve list of all accounts
- `account_balance()`: Get balance for selected account
- `account_portfolio()`: Get portfolio positions

**Features**:
- Account selection interface
- Balance retrieval with real-time NAV
- Portfolio position tracking
- Account filtering (excludes closed accounts)

**API Endpoints Used**:
- `GET /v1/accounts/list.json`: List accounts
- `GET /v1/accounts/{accountIdKey}/balance.json`: Get balance
- `GET /v1/accounts/{accountIdKey}/portfolio.json`: Get portfolio

**Dependencies**:
- `order.order.Order`: For order-related operations
- `logging`: Debug logging

---

## Market Data

### `market/market.py`

**Purpose**: Market data retrieval and quote operations.

**Class**: `Market`

**Key Methods**:
- `__init__(session, base_url)`: Initialize with authenticated session
- `quotes()`: Get market quotes for symbols

**Features**:
- Real-time market quotes
- Support for equities, options, and mutual funds
- Detailed quote information including:
  - Last trade price
  - Bid/Ask prices
  - Volume
  - Change and percentage change
  - High/Low prices
  - Previous close

**API Endpoints Used**:
- `GET /v1/market/quote/{symbol}.json`: Get quote

**Dependencies**:
- `logging`: Debug logging

---

## Order Management

### `order/order.py`

**Purpose**: Order placement, preview, cancellation, and management.

**Class**: `Order`

**Key Methods**:
- `__init__(session, account, base_url)`: Initialize with session and account
- `preview_order()`: Preview order before placement
- `place_order(preview_id)`: Place order using preview ID
- `view_orders()`: View orders by status (OPEN, EXECUTED, CANCELLED, etc.)
- `view_orders_summary()`: Summary view of all orders
- `user_select_order()`: Interactive order selection
- `print_orders(response, status)`: Format and display orders

**Order Types Supported**:
- Equity orders (EQ)
- Market orders
- Limit orders
- Stop orders
- Options orders

**Order Actions**:
- BUY
- SELL
- BUY_TO_COVER
- SELL_SHORT

**Order Terms**:
- GOOD_FOR_DAY
- GOOD_TILL_CANCEL
- IMMEDIATE_OR_CANCEL
- FILL_OR_KILL

**Features**:
- Two-step order process (preview then place)
- Order validation
- Order cancellation
- Order status tracking
- Detailed order information display

**API Endpoints Used**:
- `POST /v1/accounts/{accountIdKey}/orders/preview.json`: Preview order
- `POST /v1/accounts/{accountIdKey}/orders/place.json`: Place order
- `GET /v1/accounts/{accountIdKey}/orders.json`: Get orders
- `PUT /v1/accounts/{accountIdKey}/orders/cancel.json`: Cancel order

**Dependencies**:
- `configparser`: Configuration access
- `logging`: Debug logging
- `random`: Client order ID generation

---

## Options Trading

### `options/options_chain.py`

**Purpose**: Unified options chain interface with multiple provider support.

**Class**: `OptionsChain`

**Key Methods**:
- `__init__(session=None, base_url=None, provider_name=None)`: Initialize with provider
- `get_options_chain(symbol, expiry_date, strike_count)`: Get options chain
- `get_spx_options(expiry_date, strike_count)`: Get SPX options
- `switch_provider(provider_name, session, base_url)`: Switch provider dynamically

**Features**:
- Multi-provider support (E*TRADE, CBOE, AUTO)
- Standardized data format
- Configurable provider selection
- SPX-specific convenience method

**Dependencies**:
- `options.providers.provider_factory.OptionsProviderFactory`: Provider creation

---

### `options/options_display.py`

**Purpose**: Format and display options chain data in a readable table format.

**Class**: `OptionsChainDisplay`

**Key Methods**:
- `format_options_chain(chain_data)`: Format options chain for display
- `create_table(calls, puts, strikes)`: Create formatted table
- `format_price(price)`: Format price values
- `format_volume(volume)`: Format volume values

**Features**:
- Side-by-side calls and puts display
- Formatted prices and volumes
- Strike price alignment
- Bid/Ask spread display
- Open interest information

**Output Format**:
```
STRIKE | CALLS (Bid/Ask/Vol/OI) | PUTS (Bid/Ask/Vol/OI)
```

---

### `options/providers/base_provider.py`

**Purpose**: Abstract base class for options chain providers.

**Class**: `OptionsChainProvider` (ABC)

**Key Methods** (Abstract):
- `get_options_chain(symbol, expiry_date, strike_count)`: Must be implemented
- `provider_name`: Property returning provider name

**Purpose**: Defines the interface that all options providers must implement.

---

### `options/providers/etrade_provider.py`

**Purpose**: E*TRADE API provider for options chain data.

**Class**: `EtradeOptionsProvider(OptionsChainProvider)`

**Key Methods**:
- `__init__(session, base_url)`: Initialize with E*TRADE session
- `get_options_chain(symbol, expiry_date, strike_count)`: Get options from E*TRADE
- `_parse_etrade_response(data, symbol, expiry_date)`: Parse E*TRADE response

**Features**:
- Direct E*TRADE API integration
- Requires authentication
- Real-time options data
- Supports all E*TRADE options symbols

**API Endpoints Used**:
- `GET /v1/market/optionchains.json`: Get options chain

**Dependencies**:
- `options.providers.base_provider.OptionsChainProvider`: Base class

---

### `options/providers/cboe_provider.py`

**Purpose**: CBOE (Chicago Board Options Exchange) provider for options chain data.

**Class**: `CBOEOptionsProvider(OptionsChainProvider)`

**Key Methods**:
- `__init__()`: Initialize CBOE provider
- `get_options_chain(symbol, expiry_date, strike_count)`: Get options from CBOE
- `_fetch_cboe_data(symbol, expiry_date)`: Fetch data from CBOE website
- `_parse_cboe_response(html, symbol)`: Parse CBOE HTML response

**Features**:
- No authentication required
- Web scraping from CBOE website
- Supports SPX and other major indices
- Fallback provider when E*TRADE unavailable

**Dependencies**:
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing
- `pandas`: Data manipulation

---

### `options/providers/nasdaq_provider.py`

**Purpose**: NASDAQ provider for options chain data (placeholder/future implementation).

**Class**: `NasdaqOptionsProvider(OptionsChainProvider)`

**Status**: Placeholder for future NASDAQ integration.

---

### `options/providers/provider_factory.py`

**Purpose**: Factory pattern for creating options chain providers.

**Class**: `OptionsProviderFactory`

**Key Methods**:
- `create_provider(session=None, base_url=None, provider_name=None)`: Create provider instance

**Provider Selection Logic**:
1. If `provider_name` specified, use that provider
2. If `provider_name` is "AUTO":
   - Try E*TRADE first (if session available)
   - Fall back to CBOE if E*TRADE fails
3. Default to CBOE if no session available

**Supported Providers**:
- `"ETRADE"`: E*TRADE API provider
- `"CBOE"`: CBOE web scraping provider
- `"AUTO"`: Automatic provider selection

**Dependencies**:
- `options.providers.etrade_provider.EtradeOptionsProvider`
- `options.providers.cboe_provider.CBOEOptionsProvider`
- `configparser`: Configuration reading

---

## MCP Server

### `mcp_server/server.py`

**Purpose**: Model Context Protocol (MCP) server for E*TRADE trading operations.

**Key Components**:
- JSON-RPC over stdio communication
- Tool registration and discovery
- Request/response handling

**Available Tools**:
1. `get_accounts`: List all accounts
2. `get_account_balance`: Get account balance
3. `get_quote`: Get market quote
4. `get_spx_options_chain`: Get SPX options
5. `get_options_chain`: Get options for any symbol
6. `place_order`: Place stock/options order
7. `get_orders`: Get orders by status
8. `get_order`: Get specific order details
9. `cancel_order`: Cancel an order

**Protocol Methods**:
- `initialize`: Server initialization
- `tools/list`: List available tools
- `tools/call`: Execute a tool

**Features**:
- Lazy initialization of tools (prevents startup failures)
- Error handling and logging
- Standard MCP protocol compliance
- JSON-RPC 2.0 format

**Dependencies**:
- `mcp_server.tools.EtradeTools`: Tool implementations
- `options.options_display.OptionsChainDisplay`: Options formatting

**Usage**: Run as MCP server, communicates via stdin/stdout JSON-RPC.

---

### `mcp_server/tools.py`

**Purpose**: MCP tool implementations for E*TRADE operations.

**Class**: `EtradeTools`

**Key Methods**:
- `__init__()`: Initialize with EtradeClient
- `get_accounts()`: Get list of accounts
- `get_account_balance(account_id_key)`: Get account balance
- `get_quote(symbol)`: Get market quote
- `get_options_chain(symbol, expiry_date, strike_count, provider)`: Get options chain
- `get_spx_options(expiry_date, strike_count, provider)`: Get SPX options
- `place_order(account_id_key, symbol, action, quantity, ...)`: Place order
- `get_orders(account_id_key, status)`: Get orders by status
- `get_order(account_id_key, order_id)`: Get order details
- `cancel_order(account_id_key, order_id)`: Cancel order

**Features**:
- Error handling and validation
- Standardized return formats
- Options chain formatting
- Provider selection support

**Dependencies**:
- `mcp_server.etrade_client.EtradeClient`: API client
- `options.options_chain.OptionsChain`: Options retrieval
- `options.options_display.OptionsChainDisplay`: Options formatting

---

### `mcp_server/etrade_client.py`

**Purpose**: E*TRADE API client wrapper for MCP server.

**Class**: `EtradeClient`

**Key Methods**:
- `__init__()`: Initialize and load session
- `_load_session()`: Load OAuth session from tokens
- `_get_consumer_key()`: Get consumer key from tokens or config
- `get_accounts()`: Get list of accounts
- `get_account_balance(account_id_key)`: Get account balance
- `get_quote(symbol)`: Get market quote
- `place_order(account_id_key, order_details)`: Place order
- `_place_order_simple(order_obj, account, order_details)`: Simplified order placement
- `get_orders(account_id_key, status)`: Get orders by status
- `get_order(account_id_key, order_id)`: Get specific order
- `cancel_order(account_id_key, order_id)`: Cancel order

**Features**:
- OAuth token management
- Session persistence
- Error handling
- Direct API integration

**Dependencies**:
- `rauth.OAuth1Session`: OAuth authentication
- `accounts.accounts.Accounts`: Account operations
- `market.market.Market`: Market operations
- `order.order.Order`: Order operations
- `configparser`: Configuration reading

---

## Configuration Files

### `config.ini`

**Purpose**: Configuration file for E*TRADE API credentials and settings.

**Sections**:
- `[DEFAULT]`:
  - `CONSUMER_KEY`: E*TRADE consumer key
  - `CONSUMER_SECRET`: E*TRADE consumer secret
  - `SANDBOX_BASE_URL`: Sandbox API URL
  - `PROD_BASE_URL`: Production API URL
- `[OPTIONS_CHAIN]`:
  - `DATA_SOURCE`: Provider selection ("ETRADE", "CBOE", "AUTO")
- `[CBOE]`:
  - `API_URL`: CBOE API endpoint
  - `API_KEY`: Optional CBOE API key

**Security Note**: Contains sensitive credentials. Should not be committed to version control.

---

### `config.ini.example`

**Purpose**: Example configuration file template.

**Usage**: Copy to `config.ini` and fill in your credentials.

---

### `oauth_tokens.json`

**Purpose**: Stores OAuth access tokens after authentication.

**Structure**:
```json
{
  "access_token": "...",
  "access_token_secret": "...",
  "base_url": "https://api.etrade.com",
  "consumer_key": "...",
  "consumer_secret": "..."
}
```

**Security Note**: Contains sensitive authentication tokens. Should not be committed to version control.

---

### `oauth_tokens.json.example`

**Purpose**: Example OAuth tokens file template.

---

### `mcp_servers.json.example`

**Purpose**: Example MCP server configuration for Cursor IDE.

**Structure**:
```json
{
  "mcpServers": {
    "etrade-trading": {
      "command": "path/to/python.exe",
      "args": ["path/to/server.py"],
      "env": {
        "PYTHONPATH": "path/to/etrade_python_client"
      }
    }
  }
}
```

---

## Test Files

### `test_mcp_protocol.py`

**Purpose**: Test MCP protocol implementation.

**Features**:
- Tests server initialization
- Tests tool discovery
- Tests tool execution
- Validates JSON-RPC responses

**Usage**:
```bash
python test_mcp_protocol.py
```

---

### `run_full_test.py`

**Purpose**: Comprehensive end-to-end test of MCP server and tools.

**Test Coverage**:
1. MCP Server Initialization
2. Tool Discovery
3. Tool Execution Tests
4. Direct Tools Test
5. CBOE Provider Test

**Features**:
- Subprocess-based server testing
- JSON-RPC protocol validation
- Error handling verification
- Authentication status checking

**Usage**:
```bash
python run_full_test.py
```

---

### `mcp_server/test_tools.py`

**Purpose**: Unit tests for MCP tools.

**Features**:
- Tests individual tool functions
- Validates return formats
- Error handling tests

---

## Module Initialization Files

### `accounts/__init__.py` / `accounts/_init_.py`

**Purpose**: Package initialization for accounts module.

---

### `market/__init__.py` / `market/_init_.py`

**Purpose**: Package initialization for market module.

---

### `order/__init__.py` / `order/_init_.py`

**Purpose**: Package initialization for order module.

---

### `options/__init__.py`

**Purpose**: Package initialization for options module.

---

### `options/providers/__init__.py`

**Purpose**: Package initialization for options providers.

---

### `mcp_server/__init__.py`

**Purpose**: Package initialization for MCP server module.

---

## Additional Files

### `setup.py`

**Purpose**: Python package setup script.

**Features**:
- Package metadata
- Dependency definitions
- Installation configuration

---

### `requirements.txt`

**Purpose**: Python package dependencies.

**Dependencies**:
- `rauth==0.7.3`: OAuth 1.0 authentication
- `pandas>=1.3.0`: Data manipulation
- `numpy>=1.21.0`: Numerical operations
- `requests>=2.31.0`: HTTP requests
- `flask>=2.0.0`: Web framework (if needed)

---

### `README.md`

**Purpose**: Main project documentation and setup instructions.

---

### `ARCHITECTURE.md`

**Purpose**: Detailed architecture documentation.

---

### `CURSOR_MCP_SETUP.md`

**Purpose**: Setup guide for Cursor IDE MCP integration.

---

### `TEST_RESULTS.md`

**Purpose**: Test results and validation documentation.

---

## File Relationships

```
etrade_python_client.py (OAuth Auth)
    ↓
oauth_tokens.json (Generated)
    ↓
mcp_server/etrade_client.py (Uses tokens)
    ↓
mcp_server/tools.py (Uses client)
    ↓
mcp_server/server.py (Exposes tools via MCP)
    ↓
etrade_cli.py (Uses tools for CLI)
```

**Options Chain Flow**:
```
options/options_chain.py
    ↓
options/providers/provider_factory.py
    ↓
options/providers/[etrade|cboe]_provider.py
    ↓
options/options_display.py (Formatting)
```

---

## Common Patterns

### Error Handling
Most files use try-except blocks and return error dictionaries:
```python
try:
    result = operation()
    return result
except Exception as e:
    return {"error": str(e)}
```

### Logging
Files use a shared logger:
```python
logger = logging.getLogger('my_logger')
logger.debug("Debug message")
```

### Configuration
Files read from `config.ini`:
```python
config = configparser.ConfigParser()
config.read('config.ini')
consumer_key = config["DEFAULT"]["CONSUMER_KEY"]
```

---

## Security Considerations

1. **Never commit** `config.ini` or `oauth_tokens.json` to version control
2. **Use `.gitignore`** to exclude sensitive files
3. **Rotate tokens** periodically
4. **Use sandbox** for testing
5. **Validate inputs** before API calls

---

## Dependencies Summary

**Core Dependencies**:
- `rauth`: OAuth 1.0 authentication
- `requests`: HTTP requests
- `beautifulsoup4`: HTML parsing (CBOE provider)
- `pandas`: Data manipulation
- `numpy`: Numerical operations

**Standard Library**:
- `json`: JSON handling
- `configparser`: Configuration files
- `logging`: Logging
- `os`: File operations
- `typing`: Type hints

---

## Version Information

- **Python Version**: 3.7+
- **E*TRADE API Version**: v1
- **MCP Protocol Version**: 2024-11-05

---

## Contributing

When adding new files:
1. Follow existing code patterns
2. Add comprehensive docstrings
3. Include error handling
4. Update this documentation
5. Add appropriate tests

---

*Last Updated: 2025-01-27*

