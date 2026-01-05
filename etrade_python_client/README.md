# E*TRADE MCP Server

A Model Context Protocol (MCP) server for E*TRADE trading platform integration with Cursor IDE.

## Features

- **Order Management**: Place, retrieve, and cancel orders
- **Account Management**: View accounts and balances
- **Market Data**: Real-time quotes and options chain data
- **Multi-Provider Options**: Support for E*TRADE, CBOE, and NASDAQ options data
- **MCP Integration**: Seamless integration with Cursor IDE

## Setup

### 1. Install Dependencies

```bash
cd etrade_python_client
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### 2. Configure Credentials

Copy the example configuration files and fill in your credentials:

```bash
cp config.ini.example config.ini
cp oauth_tokens.json.example oauth_tokens.json
```

Edit `config.ini` with your E*TRADE API credentials:
- `CONSUMER_KEY`: Your E*TRADE consumer key
- `CONSUMER_SECRET`: Your E*TRADE consumer secret

### 3. Authenticate

Run the authentication script to generate `oauth_tokens.json`:

```bash
python etrade_python_client.py
```

Follow the prompts to authenticate with E*TRADE.

### 4. Configure Cursor IDE

See `CURSOR_MCP_SETUP.md` for detailed setup instructions.

## Command Line Interface

You can execute all E*TRADE functions directly from Python using the CLI script:

### Interactive Mode

```bash
python etrade_cli.py
```

This starts an interactive session where you can type commands:
- `accounts` - List all accounts
- `quote AAPL` - Get market quote
- `options AAPL` - Get options chain
- `place <account_id> AAPL BUY 1 MARKET` - Place an order
- `orders <account_id>` - Get orders
- `help` - Show all commands

### Command Line Mode

```bash
# Get accounts
python etrade_cli.py accounts

# Get quote
python etrade_cli.py quote AAPL

# Get options chain
python etrade_cli.py options AAPL --strikes 20 --provider CBOE

# Get SPX options
python etrade_cli.py spx --strikes 30

# Place market order (account_id_key is optional - uses first account if not provided)
python etrade_cli.py place --symbol AAPL --action BUY --quantity 1

# Place limit order
python etrade_cli.py place --symbol AAPL --action BUY --quantity 1 --price-type LIMIT --limit-price 150.00

# Get orders (uses first account by default)
python etrade_cli.py orders --status OPEN

# Get order details
python etrade_cli.py order --order-id <order_id>

# Cancel order
python etrade_cli.py cancel --order-id <order_id>

# If you have multiple accounts and want to specify one:
python etrade_cli.py place --account-id <account_id_key> --symbol AAPL --action BUY --quantity 1
```

## Available MCP Tools

1. `get_accounts` - Get list of E*TRADE accounts
2. `get_account_balance` - Get account balance
3. `get_quote` - Get market quote for a symbol
4. `get_options_chain` - Get options chain for any symbol
5. `get_spx_options_chain` - Get SPX options chain
6. `place_order` - Place a stock or options order
7. `get_orders` - Get orders by status
8. `get_order` - Get specific order details
9. `cancel_order` - Cancel an order

## Documentation

- `ARCHITECTURE.md` - Complete architecture and data flow documentation
- `CURSOR_MCP_SETUP.md` - Cursor IDE integration guide

## Security

**IMPORTANT**: Never commit sensitive files to version control:
- `config.ini` - Contains API credentials
- `oauth_tokens.json` - Contains OAuth tokens
- `*.log` - May contain sensitive information

These files are automatically ignored by `.gitignore`.

## License

[Your License Here]








