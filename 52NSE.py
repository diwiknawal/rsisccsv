# %%
url = 'https://nsearchives.nseindia.com/content/CM_52_wk_High_low_25012024.csv'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
}

# %%
import requests
import pandas as pd
from io import StringIO

# %%
response = requests.get(url, headers=headers)
data = StringIO(response.text.replace('"Disclaimer - The Data provided in the adjusted 52 week high and adjusted 52 week low columns  are adjusted for corporate actions (bonus, splits & rights).For actual (unadjusted) 52 week high & low prices, kindly refer bhavcopy."\n"Effective for 25-Jan-2024"\n', ''))
df = pd.read_csv(data)
print(df)
df.to_csv("52.csv", index=False)
