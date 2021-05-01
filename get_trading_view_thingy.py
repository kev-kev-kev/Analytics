from pycoingecko import CoinGeckoAPI
from utilities import *
from pandas import DataFrame, read_csv, Series
from datetime import date, timedelta


init_df = read_csv("BINANCE_tokens.txt", names=["Token"])
init_df[["Exchange", "Token"]] = init_df["Token"].str.split(':', expand=True)
init_df = init_df[["Exchange", "Token"]]

master_df = DataFrame({"Exchange": [],
                       "Token" : [],
                       "Std. Dev": [],
                       "Price": []})

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
        # get history, get volatility, add to dataframe. 
        df = get_data_binance(current_token, "1d", init_date)["close"]
        df = df.astype(float)
        deviation = df.std()
        current_price = df.mean()
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
        deviation = close_vals.std()
        current_price = close_vals.mean()
    else: 
        continue

    rows["Std. Dev"] = round(deviation, 3)
    rows["Price"] = current_price
    master_df = master_df.append(rows)

master_df["Ratio Equal"] = 100  / master_df["Price"]
master_df["Ratio Vol"] = 100 * master_df["Std. Dev"] / (master_df["Std. Dev"].sum() * master_df["Price"])


master_str_equal = ""
master_str_vol = ""
for _, rows in master_df.iterrows():
    ratio_equal = round(rows["Ratio Equal"], 2)
    ratio_vol = round(rows["Ratio Vol"], 2)
    master_str_equal = master_str_equal + ((str(ratio_equal) + "*"
                                        + rows["Exchange"] + ":"
                                        + rows["Token"] + "+"))
    ratio = round(rows["Ratio Equal"], 2)
    master_str_vol = master_str_vol + ((str(ratio_vol) + "*"
                                    + rows["Exchange"] + ":"
                                    + rows["Token"] + "+"))

master_str_equal = master_str_equal[:-1]
master_str_vol = master_str_vol[:-1]

print("equal \n", master_str_equal)
print("vol \n", master_str_vol)