from typing import Tuple
from pycoingecko import CoinGeckoAPI
from utilities import *
from pandas import DataFrame, read_csv, Series
from datetime import date, timedelta

# init_df = read_csv("Constituents\BINANCE_all_tokens.txt", names=["Token"])
init_df = read_csv("Constituents\FTX_perp_tokens.txt", names=["Token"])
init_df[["Exchange", "Token"]] = init_df["Token"].str.split(':', expand=True)
init_df = init_df[["Exchange", "Token"]]

master_df = DataFrame({"Exchange": [],
                       "Token" : [],
                       "Std. Dev": [],
                       "Price": []})

# First liq. event: 15 May - 20 May EOD -> Bounce (Many had ATH on the 18th)
# Second liq. event: 20 May - Today (26-May) -> Bounce


ftx_client = FtxClient()
data_dic = {}
for index, rows in init_df.iterrows():
    current_exchange = rows["Exchange"]
    current_token = rows["Token"]

    current_date = date.today()
    init_date = current_date - timedelta(days=1)

    current_date = current_date.strftime("%d-%m-%Y")
    init_date = init_date.strftime("%d-%m-%Y")
    
    if(current_exchange == "BINANCE"):
        # get history, get volatility, add to dataframe. 
        df = get_data_binance(current_token, "30m", init_date)["close"]
        df = df.astype(float)
        data_dic[current_token] = df

    elif(current_exchange == "FTX"):
        current_date_unix = str_to_EPOX(current_date)
        init_date_unix = str_to_EPOX(init_date)
        resolution = 60 # 1H
        # limit = 25

        # current_token = current_token.replace("USD", "/USD")
        current_token = current_token.replace("PERP", "-PERP")
        if current_token == "-PERP-PERP":
            current_token = "PERP-PERP"
        
        temp_dic = ftx_client.get_historical_data(current_token, 
                                                  resolution, 
                                                #   limit, 
                                                  init_date_unix, 
                                                  current_date_unix)
        close_vals = Series(x['close'] for x in temp_dic)
        data_dic[current_token] = close_vals
    else: 
        print("Exchange not identified, please make sure you're using 'FTX' ", 
            "or 'BINANCE'")

master_df = DataFrame(data_dic)

final_df = DataFrame({"Ticker": [],
                      "Drawdown": [],
                      "Bounce": [],
                      "Pct from local high": []})

for label, content in master_df.iteritems():
    ticker = label
    max_dd = max_drawdown(content).min()
    max_bnce = max_bounce(content).max()
    pct_from_lh = pct_from_local_high(content)

    temp_df = DataFrame({"Ticker": [ticker],
                         "Drawdown": [max_dd],
                         "Bounce": [max_bnce],
                         "Pct from local high": [pct_from_lh]})
    
    final_df = final_df.append(temp_df)

final_df.to_csv("Stats_MArxch_dip.csv")
