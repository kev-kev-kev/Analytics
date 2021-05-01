from pycoingecko import CoinGeckoAPI
from utilities import *
from pandas import DataFrame, read_csv, Series
from datetime import date, timedelta


init_df = read_csv("CEX_tokens.txt", names=["Token"])
init_df[["Exchange", "Token"]] = init_df["Token"].str.split(':', expand=True)
init_df = init_df[["Exchange", "Token"]]

master_df = DataFrame({"Exchange": [],
                       "Token" : [],
                       "Std. Dev": [],
                       "Ratio": []})

ftx_client = FtxClient()

master_str = ""
for index, rows in init_df.iterrows():
    current_exchange = rows["Exchange"]
    current_token = rows["Token"]

    current_date = date.today()
    init_date = current_date - timedelta(days=7)

    current_date = current_date.strftime("%d-%m-%Y")
    init_date = init_date.strftime("%d-%m-%Y")
    
    if(current_exchange == "BINANCE"):
        continue
    elif(current_exchange == "FTX"):
        current_date_unix = str_to_EPOX(current_date)
        init_date_unix = str_to_EPOX(init_date)
        resolution = 86400 # 1 day (60*60*24)
        limit = 25

        if("USD" in current_token):
            current_token = current_token.replace("USD", "/USD")
        elif("PERP" in current_token):
            current_token = current_token.replace("PERP", "-PERP")
        temp_dic = ftx_client.get_historical_data(current_token, 
                                       resolution, 
                                       limit, 
                                       init_date_unix, 
                                       current_date_unix)
        close_vals = Series(x['close'] for x in temp_dic)
        close_vals.
    else: 
        continue
