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


# Function to calculate Exponential Moving Average
def calculate_ema(prices, period):
    """
    :param prices: a pandas Series of closing prices
    :param period: number of days (e.g., 12, 26 are standard for MACD)
    adjust=False means it uses the recursive EMA formula
    :return:
    """
    return prices.ewm(span=period, adjust=False).mean()


# Function to calculate Moving Average Convergence Divergence
def calculate_macd(prices):
    """
    :param prices: a pandas Series of closing prices
    :return: macd_line, signal_line, histogram (all pandas Series)
    """
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)

    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


# Function to calculate Relative Strength Index
def calculate_rsi(prices, period=14):
    """
    :param prices: a pandas Series of closing prices
    :param period: lookback period (14 is the universal standard)
    :return:
    """
    delta = prices.diff()

    gains = delta.where(delta > 0, 0)
    losses = delta.where(delta < 0, 0)

    avg_gain = gains.ewm(span=period, adjust=False).mean()
    avg_loss = losses.ewm(span=period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


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

    # Calculate EMAs
    ema_12 = calculate_ema(closes, 12)
    ema_26 = calculate_ema(closes, 26)

    print("Exponential Moving Average")
    print(f"EMA(12): {ema_12.iloc[-1]:.2f}")
    print(f"EMA(26): {ema_26.iloc[-1]:.2f}\n")

    # MACD get values
    macd_line, signal_line, histogram = calculate_macd(closes)

    print("Moving Average Convergence Divergence")
    print(f"MACD line:    {macd_line.iloc[-1]:.4f}")
    print(f"Signal line:  {signal_line.iloc[-1]:.4f}")
    print(f"Histogram:    {histogram.iloc[-1]:.4f}\n")

    # Calculate and show RSI
    print("Relative Strength Index")

    rsi = calculate_rsi(closes)
    rsi_value = rsi.iloc[-1]

    print(f"RSI(14): {rsi_value:.2f}", end="  ")

    if rsi_value >= 70:
        print("⚠️ Overbought")
    elif rsi_value <= 30:
        print("🟢 Oversold")
    else:
        print("✅ Neutral\n")


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
    print(f"{stock['ticker']:<17} {price_str:<12} {change_str:<12} {change_pct_str:<10} {volume_str:<14} {market_cap_str}")

print("-" * 80)

# Print 52-week ranges
print("\n52-Week Range:")
for stock in stocks_data:
    if stock['week_52_low'] > 0 and stock['week_52_high'] > 0:
        print(f"{stock['ticker']}: {stock['week_52_low']:.2f} - {stock['week_52_high']:.2f}")

# Print timestamp
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"\nLast Updated: {now} IST")
