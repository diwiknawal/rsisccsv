import yfinance as yf
import pandas as pd

def get_52_week_high_low(stock_symbol):
    # Fetch historical data for the past year
    stock_data = yf.Ticker(stock_symbol)
    hist = stock_data.history(period="1y")
    
    # Check if historical data is available
    if hist.empty:
        return {
            "Stock": stock_symbol,
            "52 Week High": None,
            "Date of High": None,
            "52 Week Low": None,
            "Date of Low": None,
            "Current Close": None,
            "Difference (High - Close)": None,
            "Status": None
        }
    
    # Calculate 52-week high and low
    high_52_week = hist['High'].max()
    low_52_week = hist['Low'].min()
    
    # Get the date of the 52-week high and low
    date_high = hist['High'].idxmax() if high_52_week is not None else None
    date_low = hist['Low'].idxmin() if low_52_week is not None else None
    
    # Get the current close price
    current_close = hist['Close'][-1] if not hist['Close'].empty else None
    
    # Calculate the difference (52-week high - current close)
    difference = high_52_week - current_close if high_52_week is not None and current_close is not None else None
    
    # Determine status
    status = "OK" if low_52_week < high_52_week and (difference is not None and difference < 60) else "Wait"

    return {
        "Stock": stock_symbol,
        "52 Week High": high_52_week,
        "Date of High": date_high.date() if date_high else None,
        "52 Week Low": low_52_week,
        "Date of Low": date_low.date() if date_low else None,
        "Current Close": current_close,
        "Difference (High - Close)": difference,
        "Status": status
    }

if __name__ == "__main__":
    # Replace with the stock symbols you are interested in
    stocks_df = pd.read_csv('nse_stocks.csv')  # Update the filename as needed
    nse_stocks = stocks_df['Symbol']
    #nse_stocks = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']  # Example stock symbols
    
    # List to store results
    results = []

    for stock in nse_stocks:
        result = get_52_week_high_low(stock+".NS")
        results.append(result)
    
    # Create a DataFrame from the results
    df = pd.DataFrame(results)
    
    # Save the DataFrame to a CSV file
    df.to_csv("52_week_high_low_stocks.csv", index=False)
    
    print("Data saved to 52_week_high_low_stocks.csv")
