import requests
import pandas as pd
from io import StringIO
import yfinance as yf
from datetime import datetime

# NSE CSV file URL
url = 'https://nsearchives.nseindia.com/content/CM_52_wk_High_low_25012024.csv'

# Headers for the request
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

# Make the GET request to download the CSV
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Remove unwanted disclaimer from the data
    data = StringIO(response.text.replace('"Disclaimer - The Data provided in the adjusted 52 week high and adjusted 52 week low columns  are adjusted for corporate actions (bonus, splits & rights).For actual (unadjusted) 52 week high & low prices, kindly refer bhavcopy."\n"Effective for 25-Jan-2024"\n', ''))
    
    # Read CSV data and limit to the first 100 rows for testing
    df = pd.read_csv(data).head(100)
    
    # Rename columns for clarity
    df.columns = ['SYMBOL', 'SERIES', 'Adjusted 52_Week_High', '52_Week_High_Date', 'Adjusted 52_Week_Low', '52_Week_Low_Date']
    
    # Filter the DataFrame for only 'EQ' series
    eq_df = df[df['SERIES'] == 'EQ'].copy()

    # Function to fetch the close price and volume for each stock using yfinance
    def fetch_close_price_and_volume(symbol, idx):
        current_time = datetime.now().strftime('%H:%M:%S')  # Get the current time in HH:MM:SS format
        print(f"Processing {idx + 1}: Fetching data for {symbol} at {current_time}...")
        try:
            stock = yf.Ticker(f"{symbol}.NS")  # NSE stocks on yfinance have the ".NS" suffix
            hist = stock.history(period="1d")  # Get the latest available close price and volume
            if not hist.empty:
                close_price = hist['Close'].iloc[-1]  # Get the last close price
                volume = hist['Volume'].iloc[-1]     # Get the last volume
                return close_price, volume
            else:
                return None, None
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None, None

    # Add new columns for close price and volume
    close_prices = []
    volumes = []
    
    # Iterate over the filtered DataFrame (only EQ series) to fetch close price and volume for each stock
    for idx, symbol in enumerate(eq_df['SYMBOL']):
        close_price, volume = fetch_close_price_and_volume(symbol, idx)
        close_prices.append(close_price)
        volumes.append(volume)
    
    # Add the data to the filtered DataFrame
    eq_df['Close_Price'] = close_prices
    eq_df['Volume'] = volumes

    # Drop rows where Close_Price or Volume is None (due to errors or no data available)
    eq_df.dropna(subset=['Close_Price', 'Volume'], inplace=True)

    # Convert 'Adjusted 52_Week_High' and 'Close_Price' to numeric
    eq_df['Adjusted 52_Week_High'] = pd.to_numeric(eq_df['Adjusted 52_Week_High'], errors='coerce')
    eq_df['Close_Price'] = pd.to_numeric(eq_df['Close_Price'], errors='coerce')

    # Apply the filtering condition: Close_Price > 60 and Volume > 60,000
    filtered_df = eq_df[(eq_df['Close_Price'] > 60) & (eq_df['Volume'] > 60000)]

    # Round the Close_Price and Volume to 3 decimal places
    filtered_df['Close_Price'] = filtered_df['Close_Price'].round(3)
    filtered_df['Volume'] = filtered_df['Volume'].round(3)

    # Calculate Difference (Adjusted 52-Week High - Close_Price)
    filtered_df['Difference'] = filtered_df['Adjusted 52_Week_High'] - filtered_df['Close_Price']

    # Calculate Percentage Difference
    filtered_df['Percentage_Difference'] = (filtered_df['Difference'] / filtered_df['Adjusted 52_Week_High']) * 100

    # Round Difference and Percentage Difference to 3 decimal places
    filtered_df['Difference'] = filtered_df['Difference'].round(3)
    filtered_df['Percentage_Difference'] = filtered_df['Percentage_Difference'].round(3)

    # Add the 'Status' column based on the new Percentage Difference condition (-2% to -10%)
    filtered_df['Status'] = filtered_df['Percentage_Difference'].apply(
        lambda x: "NEED TO LOOK" if -10 <= x <= -2 else "WAIT"
    )

    # Save the filtered DataFrame to a new CSV file for all data
    filtered_df.to_csv("52weeks_status.csv", index=False)
    print("Data saved to 52weeks_status.csv")

    # Extract rows where the Status is "NEED TO LOOK"
    need_to_look_df = filtered_df[filtered_df['Status'] == "NEED TO LOOK"]

    # Save the "NEED TO LOOK" data to another Excel file
    need_to_look_df.to_excel("need_to_look_stocks.xlsx", index=False)
    print("Data saved to need_to_look_stocks.xlsx")
else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
