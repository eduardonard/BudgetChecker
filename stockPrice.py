import yfinance as yf

# Define the ticker symbol and get the data for the stock
tickerSymbol = 'TQQQ'
tickerData = yf.Ticker(tickerSymbol)

# Get the historical prices for the stock
tickerDf = tickerData.history(start='2010-02-09', end='2023-02-28', interval='1mo')

# Calculate the total value of your investment
total_value = 0
for price in tickerDf['Close']:
    total_value += 500 / price

# Print the total value of your investment
print(f"Total value of investment: {total_value:.2f} EUR")