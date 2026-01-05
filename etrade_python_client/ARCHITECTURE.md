# E*TRADE MCP Server - Architecture & Data Flow Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Architecture](#component-architecture)
4. [Data Flow - End to End](#data-flow---end-to-end)
5. [MCP Protocol Flow](#mcp-protocol-flow)
6. [E*TRADE API Integration](#etrade-api-integration)
7. [Order Management Flow](#order-management-flow)
8. [Options Chain Flow](#options-chain-flow)
9. [Authentication Flow](#authentication-flow)
10. [Error Handling](#error-handling)
11. [Configuration](#configuration)
12. [File Structure](#file-structure)
13. [API Reference](#api-reference)

---

## System Overview

The E*TRADE MCP Server is a Model Context Protocol (MCP) server that provides a bridge between Cursor IDE (or other MCP-compatible clients) and the E*TRADE trading platform. It enables natural language interaction for trading operations, account management, market data retrieval, and options chain analysis.

### Key Features

- **Order Management**: Place, retrieve, and cancel orders
- **Account Management**: View accounts and balances
- **Market Data**: Real-time quotes and options chain data
- **Multi-Provider Options**: Support for E*TRADE, CBOE, and NASDAQ options data
- **MCP Integration**: Seamless integration with Cursor IDE via Model Context Protocol

### Technology Stack

- **Language**: Python 3.7+
- **Protocol**: MCP (Model Context Protocol) over JSON-RPC via stdio
- **Authentication**: OAuth 1.0 (E*TRADE API)
- **Transport**: Standard Input/Output (stdio)
- **Dependencies**: rauth, pandas, numpy, requests

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Cursor IDE                               │
│                    (MCP Client)                                  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             │ JSON-RPC over stdio
                             │ (MCP Protocol)
                             │
┌───────────────────────────▼─────────────────────────────────────┐
│                    MCP Server (server.py)                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Protocol Handler                                         │  │
│  │  - initialize                                             │  │
│  │  - tools/list                                             │  │
│  │  - tools/call                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Tool Handler (handle_tool_call)                          │  │
│  │  - Routes tool calls to appropriate handlers              │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Method calls
                             │
┌───────────────────────────▼─────────────────────────────────────┐
│                    Tools Layer (tools.py)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  EtradeTools                                             │  │
│  │  - get_accounts()                                        │  │
│  │  - get_account_balance()                                 │  │
│  │  - get_quote()                                           │  │
│  │  - place_order()                                         │  │
│  │  - get_orders()                                          │  │
│  │  - get_order()                                           │  │
│  │  - cancel_order()                                        │  │
│  │  - get_options_chain()                                   │  │
│  │  - get_spx_options()                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                             │
                             │ Client calls
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ EtradeClient  │   │ OptionsChain  │   │OptionsDisplay│
│               │   │               │   │               │
│ - Accounts    │   │ - Provider    │   │ - Formatting  │
│ - Orders      │   │   Factory     │   │ - Display     │
│ - Quotes      │   │ - Providers   │   │               │
└───────┬───────┘   └───────┬───────┘   └───────────────┘
        │                   │
        │                   │
        ▼                   ▼
┌───────────────┐   ┌───────────────┐
│  E*TRADE API  │   │ Options       │
│               │   │ Providers     │
│ - OAuth 1.0   │   │ - E*TRADE     │
│ - REST API    │   │ - CBOE        │
│               │   │ - NASDAQ      │
└───────────────┘   └───────────────┘
```

---

## Component Architecture

### 1. MCP Server Layer (`mcp_server/server.py`)

**Purpose**: Handles MCP protocol communication and routes tool calls.

**Key Components**:
- **Protocol Handler**: Manages JSON-RPC messages (initialize, tools/list, tools/call)
- **Tool Registry**: Defines available tools with schemas
- **Request Router**: Routes tool calls to appropriate handlers

**Responsibilities**:
- Parse JSON-RPC requests from stdin
- Validate tool schemas
- Route tool calls to `EtradeTools`
- Format responses as MCP content
- Handle errors and exceptions

### 2. Tools Layer (`mcp_server/tools.py`)

**Purpose**: High-level interface for trading operations.

**Key Class**: `EtradeTools`

**Methods**:
- Account operations: `get_accounts()`, `get_account_balance()`
- Market data: `get_quote()`
- Order management: `place_order()`, `get_orders()`, `get_order()`, `cancel_order()`
- Options: `get_options_chain()`, `get_spx_options()`

**Responsibilities**:
- Coordinate between client and display layers
- Format responses for MCP
- Handle business logic
- Integrate options chain providers

### 3. Client Layer (`mcp_server/etrade_client.py`)

**Purpose**: Low-level E*TRADE API wrapper.

**Key Class**: `EtradeClient`

**Methods**:
- `get_accounts()`: Retrieve account list
- `get_account_balance()`: Get account balance
- `get_quote()`: Get market quote
- `place_order()`: Place trading order
- `get_orders()`: Retrieve orders by status
- `get_order()`: Get specific order details
- `cancel_order()`: Cancel an order

**Responsibilities**:
- Manage OAuth session
- Make authenticated API calls
- Handle API responses
- Error handling and retries

### 4. Options Chain System

**Components**:
- **OptionsChain** (`options/options_chain.py`): Unified interface
- **Provider Factory** (`options/providers/provider_factory.py`): Creates providers
- **Providers**: E*TRADE, CBOE, NASDAQ implementations
- **Display** (`options/options_display.py`): Formatting and display

**Provider Hierarchy**:
```
OptionsChainProvider (Abstract Base)
├── EtradeOptionsProvider
├── CBOEOptionsProvider
└── NASDAQOptionsProvider
```

### 5. Supporting Modules

- **Accounts** (`accounts/accounts.py`): Account management
- **Market** (`market/market.py`): Market data operations
- **Order** (`order/order.py`): Order operations (legacy, used by EtradeClient)

---

## Data Flow - End to End

### High-Level Flow

```
User Request (Cursor IDE)
    │
    ▼
MCP Protocol (JSON-RPC)
    │
    ▼
MCP Server (server.py)
    │
    ├─► Parse JSON-RPC request
    ├─► Validate tool schema
    └─► Route to tool handler
    │
    ▼
Tools Layer (tools.py)
    │
    ├─► Business logic
    ├─► Format request
    └─► Call client layer
    │
    ▼
Client Layer (etrade_client.py)
    │
    ├─► Load OAuth session
    ├─► Build API request
    └─► Make HTTP call
    │
    ▼
E*TRADE API
    │
    ├─► Authenticate (OAuth 1.0)
    ├─► Process request
    └─► Return response
    │
    ▼
Response flows back through layers
    │
    ▼
Formatted MCP Response
    │
    ▼
Cursor IDE (Display to user)
```

### Detailed Request Flow

#### 1. User Initiates Request

**Example**: User types "Show me my E*TRADE accounts" in Cursor IDE

```
Cursor IDE
    │
    ├─► Natural language processing
    ├─► Identifies tool: get_accounts
    └─► Constructs JSON-RPC request
```

#### 2. MCP Protocol Communication

**JSON-RPC Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "get_accounts",
    "arguments": {}
  }
}
```

**Transport**: Written to server's stdin

#### 3. Server Processing

**server.py**:
```python
# Read from stdin
request = json.loads(sys.stdin.readline())

# Route to handler
if request["method"] == "tools/call":
    tool_name = request["params"]["name"]
    arguments = request["params"]["arguments"]
    result = handle_tool_call(tool_name, arguments)
```

#### 4. Tool Execution

**tools.py**:
```python
def get_accounts(self):
    accounts = self.client.get_accounts()
    return {"accounts": accounts, "count": len(accounts)}
```

#### 5. Client API Call

**etrade_client.py**:
```python
def get_accounts(self):
    url = self.base_url + "/v1/accounts/list.json"
    response = self.session.get(url, header_auth=True)
    # Process response
    return accounts
```

#### 6. Response Flow

**Response Path**:
```
E*TRADE API Response
    │
    ▼
EtradeClient.get_accounts()
    │
    ▼
EtradeTools.get_accounts()
    │
    ▼
handle_tool_call()
    │
    ▼
MCP Response Format
    │
    ▼
JSON-RPC Response (stdout)
    │
    ▼
Cursor IDE
```

**JSON-RPC Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"accounts\": [...], \"count\": 3}"
    }]
  }
}
```

---

## MCP Protocol Flow

### Protocol Initialization

**Sequence**:
1. Cursor IDE starts MCP server process
2. Server reads from stdin, writes to stdout
3. Cursor sends `initialize` request
4. Server responds with capabilities

**Initialize Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {
      "name": "cursor",
      "version": "1.0.0"
    }
  }
}
```

**Initialize Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
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
```

### Tool Discovery

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "get_accounts",
        "description": "Get list of E*TRADE accounts",
        "inputSchema": {...}
      },
      ...
    ]
  }
}
```

### Tool Execution

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "get_accounts",
    "arguments": {}
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"accounts\": [...], \"count\": 3}"
    }]
  }
}
```

---

## E*TRADE API Integration

### Authentication Flow

**OAuth 1.0 Process**:

1. **Token Loading**:
   ```python
   # Load from oauth_tokens.json
   {
     "access_token": "...",
     "access_token_secret": "...",
     "consumer_key": "...",
     "consumer_secret": "...",
     "base_url": "https://api.etrade.com"
   }
   ```

2. **Session Creation**:
   ```python
   session = OAuth1Session(
       consumer_key=consumer_key,
       consumer_secret=consumer_secret,
       access_token=access_token,
       access_token_secret=access_token_secret
   )
   ```

3. **API Request**:
   ```python
   response = session.get(url, header_auth=True)
   ```

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/accounts/list.json` | GET | Get account list |
| `/v1/accounts/{id}/balance.json` | GET | Get account balance |
| `/v1/market/quote/{symbol}.json` | GET | Get market quote |
| `/v1/accounts/{id}/orders/preview.json` | POST | Preview order |
| `/v1/accounts/{id}/orders/place.json` | POST | Place order |
| `/v1/accounts/{id}/orders.json` | GET | Get orders |
| `/v1/accounts/{id}/orders/cancel.json` | PUT | Cancel order |
| `/v1/market/optionchains.json` | GET | Get options chain |

### Request/Response Format

**Example: Get Accounts**:
```http
GET /v1/accounts/list.json HTTP/1.1
Host: api.etrade.com
Authorization: OAuth oauth_consumer_key="...", oauth_token="...", ...
```

**Response**:
```json
{
  "AccountListResponse": {
    "Accounts": {
      "Account": [
        {
          "accountId": "823145980",
          "accountIdKey": "dBZOKt9xDrtRSAOl4MSiiA",
          "accountStatus": "ACTIVE",
          ...
        }
      ]
    }
  }
}
```

---

## Order Management Flow

### Place Order Flow

```
User Request: "Buy 10 shares of AAPL"
    │
    ▼
1. Tool Call: place_order()
   Parameters:
   - account_id_key: "dBZOKt9xDrtRSAOl4MSiiA"
   - symbol: "AAPL"
   - action: "BUY"
   - quantity: 10
   - price_type: "MARKET"
    │
    ▼
2. EtradeClient.place_order()
   - Validates account
   - Builds order structure
    │
    ▼
3. Preview Order API Call
   POST /v1/accounts/{id}/orders/preview.json
   XML Payload:
   <PreviewOrderRequest>
     <orderType>EQ</orderType>
     <Order>
       <priceType>MARKET</priceType>
       <Instrument>
         <Product>
           <symbol>AAPL</symbol>
         </Product>
         <orderAction>BUY</orderAction>
         <quantity>10</quantity>
       </Instrument>
     </Order>
   </PreviewOrderRequest>
    │
    ▼
4. Receive Preview ID
   Response: {"PreviewOrderResponse": {"PreviewIds": [{"previewId": "12345"}]}}
    │
    ▼
5. Place Order API Call
   POST /v1/accounts/{id}/orders/place.json
   XML Payload:
   <PlaceOrderRequest>
     <previewId>12345</previewId>
   </PlaceOrderRequest>
    │
    ▼
6. Receive Order ID
   Response: {"PlaceOrderResponse": {"OrderIds": [{"orderId": "67890"}]}}
    │
    ▼
7. Return Success Response
   {
     "success": true,
     "order_id": "67890",
     "symbol": "AAPL",
     "action": "BUY",
     "quantity": "10"
   }
```

### Get Orders Flow

```
User Request: "Show me my open orders"
    │
    ▼
1. Tool Call: get_orders()
   Parameters:
   - account_id_key: "dBZOKt9xDrtRSAOl4MSiiA"
   - status: "OPEN"
    │
    ▼
2. EtradeClient.get_orders()
   - Builds API request
    │
    ▼
3. API Call
   GET /v1/accounts/{id}/orders.json?status=OPEN
    │
    ▼
4. Process Response
   - Parse JSON
   - Extract order details
   - Format response
    │
    ▼
5. Return Orders
   {
     "OrdersResponse": {
       "Order": [
         {
           "orderId": "67890",
           "OrderDetail": [...],
           ...
         }
       ]
     }
   }
```

### Cancel Order Flow

```
User Request: "Cancel order 67890"
    │
    ▼
1. Tool Call: cancel_order()
   Parameters:
   - account_id_key: "dBZOKt9xDrtRSAOl4MSiiA"
   - order_id: "67890"
    │
    ▼
2. EtradeClient.cancel_order()
   - Builds cancel request
    │
    ▼
3. API Call
   PUT /v1/accounts/{id}/orders/cancel.json
   XML Payload:
   <CancelOrderRequest>
     <orderId>67890</orderId>
   </CancelOrderRequest>
    │
    ▼
4. Process Response
   - Check success
   - Extract order ID
    │
    ▼
5. Return Result
   {
     "success": true,
     "order_id": "67890",
     "message": "Order 67890 successfully cancelled"
   }
```

---

## Options Chain Flow

### Options Chain Request Flow

```
User Request: "Get SPX options chain"
    │
    ▼
1. Tool Call: get_spx_options_chain()
   Parameters:
   - strike_count: 20 (default)
   - provider: None (uses config)
    │
    ▼
2. EtradeTools.get_spx_options()
   - Calls get_options_chain("SPX", ...)
    │
    ▼
3. OptionsChain.get_options_chain()
   - Determines provider (from config or parameter)
   - Creates provider instance
    │
    ▼
4. Provider Factory
   OptionsProviderFactory.create_provider()
   - Reads config.ini
   - Creates appropriate provider:
     * E*TRADE (if authenticated)
     * NASDAQ (fallback)
     * CBOE (fallback)
    │
    ▼
5. Provider.get_options_chain()
   ┌─────────────────────────────────────┐
   │ E*TRADE Provider                    │
   │ GET /v1/market/optionchains.json    │
   │ ?symbol=SPX&strikeCount=20         │
   └─────────────────────────────────────┘
   OR
   ┌─────────────────────────────────────┐
   │ CBOE/NASDAQ Provider                │
   │ GET external API endpoints           │
   └─────────────────────────────────────┘
    │
    ▼
6. Format Response
   - Standardize format
   - Extract calls/puts
   - Calculate Greeks (if available)
    │
    ▼
7. OptionsDisplay.format_options_chain()
   - Create formatted table
   - Add JSON format
    │
    ▼
8. Return Formatted Response
   {
     "calls": [...],
     "puts": [...],
     "underlying_price": 4500.00,
     "formatted_display": "=== OPTIONS CHAIN ===\n...",
     "json_format": "{...}"
   }
```

### Provider Selection Logic

```
AUTO Mode (Default):
    │
    ├─► Try E*TRADE Provider
    │   ├─► Has session? → Yes → Use E*TRADE
    │   └─► No session? → Try NASDAQ
    │
    ├─► Try NASDAQ Provider
    │   ├─► Available? → Yes → Use NASDAQ
    │   └─► Not available? → Try CBOE
    │
    └─► Try CBOE Provider
        ├─► Available? → Yes → Use CBOE
        └─► Not available? → Error
```

---

## Authentication Flow

### Initial Authentication (One-Time Setup)

```
1. User runs authentication script
   (etrade_python_client.py - not in current codebase)
    │
    ▼
2. OAuth 1.0 Flow
   ├─► Get request token
   ├─► User authorizes in browser
   ├─► User enters verification code
   └─► Exchange for access token
    │
    ▼
3. Save Tokens
   oauth_tokens.json:
   {
     "access_token": "...",
     "access_token_secret": "...",
     "consumer_key": "...",
     "consumer_secret": "...",
     "base_url": "https://api.etrade.com"
   }
```

### Session Loading (Runtime)

```
1. EtradeClient.__init__()
    │
    ▼
2. _load_session()
   - Read oauth_tokens.json
   - Extract tokens
    │
    ▼
3. Create OAuth1Session
   session = OAuth1Session(
       consumer_key=...,
       consumer_secret=...,
       access_token=...,
       access_token_secret=...
   )
    │
    ▼
4. Session Ready
   - All API calls use this session
   - OAuth 1.0 signing handled automatically
```

---

## Error Handling

### Error Flow

```
API Error
    │
    ▼
EtradeClient catches exception
    │
    ▼
Returns error dict: {"error": "message"}
    │
    ▼
EtradeTools receives error
    │
    ▼
Returns error in response
    │
    ▼
handle_tool_call() catches exception
    │
    ▼
Logs error: logger.error(...)
    │
    ▼
Returns MCP error response
    │
    ▼
Cursor IDE displays error
```

### Error Types

1. **Authentication Errors**:
   - Missing tokens
   - Invalid tokens
   - Expired tokens

2. **API Errors**:
   - HTTP errors (400, 401, 403, 500)
   - Invalid parameters
   - Rate limiting

3. **Validation Errors**:
   - Missing required parameters
   - Invalid parameter values
   - Account not found

4. **Network Errors**:
   - Connection timeout
   - DNS resolution failure
   - SSL errors

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "{\"error\": \"Order not found\"}"
    }]
  }
}
```

---

## Configuration

### Configuration Files

#### 1. `config.ini`

```ini
[DEFAULT]
CONSUMER_KEY = your_consumer_key
CONSUMER_SECRET = your_consumer_secret
SANDBOX_BASE_URL = https://apisb.etrade.com
PROD_BASE_URL = https://api.etrade.com

[OPTIONS_CHAIN]
# Options: "ETRADE", "CBOE", "NASDAQ", "AUTO"
DATA_SOURCE = AUTO

[CBOE]
API_URL = https://www.cboe.com
API_KEY = 
```

#### 2. `oauth_tokens.json`

```json
{
  "access_token": "...",
  "access_token_secret": "...",
  "consumer_key": "...",
  "consumer_secret": "...",
  "base_url": "https://api.etrade.com"
}
```

#### 3. `mcp.json` (Cursor Configuration)

```json
{
  "mcpServers": {
    "etrade-trading": {
      "command": "C:\\...\\venv\\Scripts\\python.exe",
      "args": ["C:\\...\\mcp_server\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\...\\etrade_python_client"
      }
    }
  }
}
```

---

## File Structure

```
etrade_python_client/
├── mcp_server/              # MCP server implementation
│   ├── __init__.py
│   ├── server.py            # MCP protocol handler
│   ├── tools.py             # High-level tool interface
│   ├── etrade_client.py     # E*TRADE API client
│   └── test_tools.py        # Testing utilities
│
├── accounts/                # Account management
│   ├── __init__.py
│   └── accounts.py
│
├── market/                  # Market data
│   ├── __init__.py
│   └── market.py
│
├── order/                   # Order operations
│   ├── __init__.py
│   └── order.py
│
├── options/                 # Options chain system
│   ├── __init__.py
│   ├── options_chain.py     # Unified interface
│   ├── options_display.py   # Formatting
│   └── providers/           # Data providers
│       ├── __init__.py
│       ├── base_provider.py
│       ├── etrade_provider.py
│       ├── cboe_provider.py
│       ├── nasdaq_provider.py
│       └── provider_factory.py
│
├── config.ini               # Configuration
├── oauth_tokens.json        # Authentication tokens
├── mcp_servers.json.example # MCP config example
├── CURSOR_MCP_SETUP.md      # Setup instructions
└── ARCHITECTURE.md          # This document
```

---

## API Reference

### MCP Tools

#### 1. get_accounts

**Description**: Get list of E*TRADE accounts

**Parameters**: None

**Returns**:
```json
{
  "accounts": [
    {
      "accountId": "823145980",
      "accountIdKey": "dBZOKt9xDrtRSAOl4MSiiA",
      "accountStatus": "ACTIVE",
      ...
    }
  ],
  "count": 3
}
```

#### 2. get_account_balance

**Description**: Get account balance

**Parameters**:
- `account_id_key` (string, required)

**Returns**: Account balance details

#### 3. get_quote

**Description**: Get market quote

**Parameters**:
- `symbol` (string, required)

**Returns**: Market quote data

#### 4. place_order

**Description**: Place a stock or options order

**Parameters**:
- `account_id_key` (string, required)
- `symbol` (string, required)
- `action` (string, required): "BUY", "SELL", "BUY_TO_COVER", "SELL_SHORT"
- `quantity` (integer, required)
- `price_type` (string, optional): "MARKET" or "LIMIT" (default: "MARKET")
- `limit_price` (number, optional): Required if price_type is "LIMIT"
- `order_term` (string, optional): "GOOD_FOR_DAY", "IMMEDIATE_OR_CANCEL", "FILL_OR_KILL" (default: "GOOD_FOR_DAY")

**Returns**:
```json
{
  "success": true,
  "order_id": "67890",
  "symbol": "AAPL",
  "action": "BUY",
  "quantity": "10"
}
```

#### 5. get_orders

**Description**: Get orders by status

**Parameters**:
- `account_id_key` (string, required)
- `status` (string, optional): "OPEN", "EXECUTED", "CANCELLED", "REJECTED", "EXPIRED", "INDIVIDUAL_FILLS" (default: "OPEN")

**Returns**: Orders list

#### 6. get_order

**Description**: Get specific order details

**Parameters**:
- `account_id_key` (string, required)
- `order_id` (string, required)

**Returns**: Order details

#### 7. cancel_order

**Description**: Cancel an order

**Parameters**:
- `account_id_key` (string, required)
- `order_id` (string, required)

**Returns**:
```json
{
  "success": true,
  "order_id": "67890",
  "message": "Order 67890 successfully cancelled"
}
```

#### 8. get_options_chain

**Description**: Get options chain for any symbol

**Parameters**:
- `symbol` (string, required)
- `expiry_date` (string, optional): YYYYMMDD format
- `strike_count` (integer, optional): Default 20
- `provider` (string, optional): "ETRADE", "CBOE" (uses config if not specified)

**Returns**: Options chain with formatted display

#### 9. get_spx_options_chain

**Description**: Get SPX options chain

**Parameters**:
- `expiry_date` (string, optional): YYYYMMDD format
- `strike_count` (integer, optional): Default 20
- `provider` (string, optional): "ETRADE", "CBOE"

**Returns**: SPX options chain with formatted display

---

## Data Formats

### Account Format

```json
{
  "accountId": "823145980",
  "accountIdKey": "dBZOKt9xDrtRSAOl4MSiiA",
  "accountMode": "IRA",
  "accountDesc": "Brokerage",
  "accountName": "NickName-1",
  "accountType": "MARGIN",
  "institutionType": "BROKERAGE",
  "accountStatus": "ACTIVE"
}
```

### Order Format

```json
{
  "orderId": "67890",
  "OrderDetail": [{
    "priceType": "MARKET",
    "orderTerm": "GOOD_FOR_DAY",
    "Instrument": [{
      "Product": {
        "symbol": "AAPL",
        "securityType": "EQ"
      },
      "orderAction": "BUY",
      "quantity": 10
    }]
  }]
}
```

### Options Chain Format

```json
{
  "calls": [
    {
      "strike": 4500.0,
      "bid": 105.50,
      "ask": 106.00,
      "last": 105.75,
      "volume": 1234,
      "openInterest": 5678,
      "impliedVolatility": 15.2
    }
  ],
  "puts": [...],
  "underlying_price": 4500.00,
  "expiry_date": "20241220",
  "provider": "ETRADE",
  "formatted_display": "=== OPTIONS CHAIN ===\n...",
  "json_format": "{...}"
}
```

---

## Performance Considerations

### Caching

- OAuth session is cached for the lifetime of `EtradeClient` instance
- No response caching currently implemented

### Rate Limiting

- E*TRADE API has rate limits
- No explicit rate limiting in current implementation
- Consider adding rate limiting for production use

### Concurrency

- MCP server handles one request at a time (stdio-based)
- No concurrent request handling
- Each tool call is synchronous

---

## Security Considerations

### Token Storage

- `oauth_tokens.json` contains sensitive credentials
- Should be excluded from version control (use .gitignore)
- Consider encrypting tokens for production

### API Security

- OAuth 1.0 provides request signing
- HTTPS used for all API calls
- Consumer keys stored in config.ini

### Input Validation

- Tool schemas validate input types
- Additional validation in client layer
- SQL injection not applicable (no database)

---

## Troubleshooting

### Common Issues

1. **"No saved tokens found"**
   - Run authentication script to generate `oauth_tokens.json`

2. **"Account not found"**
   - Verify account_id_key is correct
   - Use `get_accounts` to get valid account IDs

3. **"Order preview failed"**
   - Check symbol is valid
   - Verify account has sufficient funds
   - Check market hours

4. **Options chain returns empty**
   - Verify symbol supports options
   - Check provider availability
   - Try different provider

### Debugging

Enable logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check server output:
- Server writes to stdout (MCP responses)
- Errors logged to logger
- Check Cursor IDE console for MCP errors

---

## Future Enhancements

### Potential Improvements

1. **Response Caching**: Cache frequently accessed data
2. **Rate Limiting**: Implement rate limiting for API calls
3. **WebSocket Support**: Real-time market data updates
4. **Order Status Polling**: Automatic order status updates
5. **Portfolio Analytics**: Additional portfolio analysis tools
6. **Multi-Account Operations**: Batch operations across accounts

---

## Conclusion

This architecture provides a clean separation of concerns:

- **MCP Layer**: Protocol handling
- **Tools Layer**: Business logic
- **Client Layer**: API integration
- **Provider Layer**: Data source abstraction

The system is designed for:
- **Extensibility**: Easy to add new tools
- **Maintainability**: Clear separation of concerns
- **Reliability**: Error handling at each layer
- **Flexibility**: Multiple options data providers

For setup instructions, see `CURSOR_MCP_SETUP.md`.









