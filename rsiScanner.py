import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Step 2: Fetch and sort stock data for each code
days_ago = 1120  # Number of days to look back
end_date = datetime.today().date()
start_date = end_date - timedelta(days=days_ago)

def get_last_500_sessions(symbol):
    """Fetch the last 500 trading days of closing prices for the given stock symbol."""
    # Append '.NS' for NSE stocks
    full_symbol = f"{symbol}.NS"
    stock_data = yf.download(full_symbol, start=start_date, end=end_date,interval='1d')  # Last 500 days
    stock_data = stock_data[['Close']]  # Select only the 'Close' column
    stock_data.reset_index(inplace=True)  # Reset index to have 'Date' as a column
    
    # Check if data is empty
    if stock_data.empty:
        print(f"No data found for {full_symbol}.")
        return pd.DataFrame()  # Return empty DataFrame if no data is found

    # Calculate Gain and Loss
    stock_data['Gain'] = stock_data['Close'].diff().clip(lower=0)  # Positive changes
    stock_data['Loss'] = stock_data['Close'].diff().clip(upper=0).abs()  # Absolute value of negative changes

    # Initialize Average Gain and Average Loss
    stock_data['Average Gain'] = 0.0
    stock_data['Average Loss'] = 0.0

    # Calculate Average Gain and Average Loss for the first 14 days
    stock_data.loc[13, 'Average Gain'] = stock_data['Gain'][:14].mean()  # First 14 days' average gain
    stock_data.loc[13, 'Average Loss'] = stock_data['Loss'][:14].mean()  # First 14 days' average loss

    # Apply the formulas: 
    # Average Gain: (Previous day Average Gain * 13 + Current Gain) / 14
    # Average Loss: (Previous day Average Loss * 13 + Current Loss) / 14
    for i in range(14, len(stock_data)):
        stock_data.loc[i, 'Average Gain'] = (stock_data.loc[i-1, 'Average Gain'] * 13 + stock_data.loc[i, 'Gain']) / 14
        stock_data.loc[i, 'Average Loss'] = (stock_data.loc[i-1, 'Average Loss'] * 13 + stock_data.loc[i, 'Loss']) / 14

    # Calculate Relative Strength (RS)
    stock_data['RS'] = stock_data['Average Gain'] / stock_data['Average Loss'].replace(0, pd.NA)  # Replace 0 to avoid division by zero

    # Calculate RSI
    stock_data['RSI'] = 100 - (100 / (1 + stock_data['RS'].replace(0, pd.NA)))  # Replace 0 to avoid division by zero

    # Return the last session data
    return stock_data.iloc[-1]  # Return only the latest available session

def main():
    # Load stock symbols from CSV
    stocks_df = pd.read_csv('nse_stocks.csv')  # Update the filename as needed
    stock_symbols = stocks_df['Symbol']

    # Load the existing data to update
    existing_data = pd.read_csv('nse_stocks.csv')  # Update the filename as needed

    # Loop through each stock symbol and fetch data
    for symbol in stock_symbols:
        try:
            # Get last session data of the stock
            latest_data = get_last_500_sessions(symbol)
            
            # Check if latest_data is empty
            if latest_data.empty:
                continue  # Skip to the next stock if no data is available
            
            # Update the corresponding row in the existing data
            # Find the index of the row with the matching symbol
            index = existing_data[existing_data['Symbol'] == symbol].index
            
            if not index.empty:
                # Update the row with new data
                existing_data.loc[index[0], 'Close'] = round(latest_data['Close'], 3)
                existing_data.loc[index[0], 'Gain'] = round(latest_data['Gain'], 3)
                existing_data.loc[index[0], 'Loss'] = round(latest_data['Loss'], 3)
                existing_data.loc[index[0], 'Average Gain'] = round(latest_data['Average Gain'], 3)
                existing_data.loc[index[0], 'Average Loss'] = round(latest_data['Average Loss'], 3)
                existing_data.loc[index[0], 'RS'] = round(latest_data['RS'], 3)
                existing_data.loc[index[0], 'RSI'] = round(latest_data['RSI'], 3)
                if((round(latest_data['RSI'], 3) < 35 and round(latest_data['RSI'], 3) > 29)):
                    existing_data.loc[index[0], 'Action'] =   "Open the eyes"
                else:
                    existing_data.loc[index[0], 'Action'] =  "Wait"

            else:
                print(f"Symbol {symbol} not found in existing data.")

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")

    # Save the updated data back to the CSV file
    existing_data.to_csv('nse_stocks.csv', index=False)  # Save updated data to the same CSV file

    

if __name__ == "__main__":
    main()
