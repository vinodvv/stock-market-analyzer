# Import necessary libraries
# (yfinance for stock data, datetime for timestamps)
import yfinance as yf
from datetime import datetime

# Function to calculate Simple Moving Average (SMA)
def calculate_sma(prices, period):
    """
    :param prices: a pandas Series of closing  prices
    :param period: number of days to average (e.g., 20, 50, 200)
    :return:
    """
    return prices.rolling(window=period).mean()


# Print header
print("Stock Price Tracker")
print("===================")

# Get ticker symbols from user
# (comma-separated, convert to uppercase list)
tickers_input = input("Enter stock tickers (comma-separated): ")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

# Print status message
print("\nFetching stock data...\n")

# Create empty list to store stock data
stocks_data = []

# Loop through each ticker
for ticker in tickers:
    # Create stock object
    stock = yf.Ticker(ticker)
    # Get stock info dictionary
    info = stock.info

    # Extract current price and previous close
    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
    previous_close = info.get('previousClose', 0)

    # Calculate change and change percentage
    if previous_close > 0:
        change = current_price - previous_close
        change_percent = (change / previous_close) * 100
    else:
        change = 0
        change_percent = 0

    # Extract volume, market cap, and 52-week range
    volume = info.get('volume', 0)
    market_cap = info.get('marketCap', 0)
    week_52_high = info.get('fiftyTwoWeekHigh', 0)
    week_52_low = info.get('fiftyTwoWeekLow', 0)

    # Store data in dictionary
    stocks_data.append({
        'ticker': ticker,
        'price': current_price,
        'change': change,
        'change_percent': change_percent,
        'volume': volume,
        'market_cap': market_cap,
        'week_52_high': week_52_high,
        'week_52_low': week_52_low
    })

    # Fetch 1 year of daily historical data
    hist = stock.history(period="1y")
    closes = hist['Close']  # pandas Series of closing prices

    # Calculate SMAs
    sma_20 = calculate_sma(closes, 20)
    sma_50 = calculate_sma(closes, 50)

    print("Simple Moving Average:")
    # .iloc[-1] gets the most recent value
    print(f"SMA(20): {sma_20.iloc[-1]:.2f}")
    print(f"SMA(50): {sma_50.iloc[-1]:.2f}\n")


# Print table header
print("Stock Market Data")
print("-" * 80)
print(f"{'Ticker':<17} {'Price':<12} {'Change':<12} {'Change%':<10} {'Volume':<14} {'Market Cap'}")
print("-" * 80)

# Loop through stocks and print formatted data
for stock in stocks_data:
    price_str = f"{stock['price']:.2f}"  # Format price
    change_str = f"{'+' if stock['change'] >= 0 else ''}{stock['change']:.2f}"  # Format change (with + or - sign)
    change_pct_str = f"{'+' if stock['change_percent'] >= 0 else ''}{stock['change_percent']:.2f}%"

    volume_str = f"{stock['volume'] / 1_000_000:.1f}M" if stock['volume'] > 0 else "N/A"  # Format volume (in millions)

    # Format market cap (T/B/M suffix)
    if stock['market_cap'] >= 1_000_000_000_000:
        market_cap_str = f"{stock['market_cap'] / 1_000_000_000_000:.2f}T"
    elif stock['market_cap'] >= 1_000_000_000:
        market_cap_str = f"{stock['market_cap'] / 1_000_000_000:.2f}B"
    elif stock['market_cap'] >= 1_000_000:
        market_cap_str = f"{stock['market_cap'] / 1_000_000:.2f}M"
    else:
        market_cap_str = "N/A"

    # Print row
    print(f"{stock['ticker']:<17} {price_str:<12} {change_str:<11} {change_pct_str:<10} {volume_str:<14} {market_cap_str}")

print("-" * 80)

# Print 52-week ranges
print("\n52-Week Range:")
for stock in stocks_data:
    if stock['week_52_low'] > 0 and stock['week_52_high'] > 0:
        print(f"{stock['ticker']}: {stock['week_52_low']:.2f} - {stock['week_52_high']:.2f}")

# Print timestamp
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"\nLast Updated: {now} IST")
