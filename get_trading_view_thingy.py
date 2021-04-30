from pycoingecko import CoinGeckoAPI
from utilities import get_data_binance
from pandas import DataFrame, read_csv
from datetime import date, timedelta


init_df = read_csv("CEX_tokens.txt", names=["Token"])
init_df[["Exchange", "Token"]] = init_df["Token"].str.split(':', expand=True)
init_df = init_df[["Exchange", "Token"]]



for index, rows in init_df.iterrows():
    current_exchange = rows["Exchange"]
    current_token = rows["Token"]

    current_date = date.today()
    init_date = current_date - timedelta(days=7)

    current_date = current_date.strftime("%d-%m-%Y")
    init_date = init_date.strftime("%d-%m-%Y")
    
    if(current_exchange == "Binance"):
        # get history, get volatility, add to dataframe. 
        df = get_data_binance(current_token, "1d", init_date)
        print(df)






coin_list = ["BNBUSDT",
            "FTTUSDT"]

1. get prices of all for last week
2. get volatiliy
3. compute inverse wights.
4. create massive string for each :D