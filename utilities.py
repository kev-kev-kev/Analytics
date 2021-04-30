# Utilities
from pandas import DataFrame

def get_data_binance(symbol: str, kline_size: str, init_date: str, save=False) -> DataFrame:
    """ This function downloads the data available for the given symbol and
    given timeframe. It also writes the data to the computer if it is
    necessary.

    :param symbol str:     The coin from which we want to download the data.
    :param kline_size str: The timeframe that we want to download the data.
    :param save bool:      A boolean denoting whether we require the data
                           to be saved. Default is False.
    :param init_date str: "1 Jan 2020" <- how it should look like
    :return data_df: A dataframe containing all the data corresponding
                     to the coin.
    :rtype: DataFrame
    """

    # API data to download the data from Binance. Use your own api codes.
    # (You might want to set up a ghost account for security reasons)
    binance_api_key = '7FI9XE4umGVm5oBvLX8geXRQdEMcx32VcZ4v1mlr9dDivOPhBrvJfmXTd5yXIP3m'
    binance_api_secret = '0n6ZBxkspZR9UH1FbHAIFnpuQoLmVKUa5SgVEbgN2lqv75WX4ypdj85W16PBlyMe'
    binance_client = Client(api_key=binance_api_key,
                            api_secret=binance_api_secret)

    newest_point = to_datetime(binance_client.get_klines(
        symbol=symbol, interval=kline_size)[-1][0], unit='ms')
    newest_point = newest_point.strftime("%d %b %Y %H:%M:%S")
    # oldest_point = datetime.strptime('1 Jan 2017', '%d %b %Y')
    oldest_point = datetime.strptime(init_date, '%d %b %Y')
    oldest_point = oldest_point.strftime("%d %b %Y %H:%M:%S")

    filename = (CURRENT_PATH +
                '/data/historical_coin_data/%s-%s-data.csv' % (symbol, kline_size))
    data_df = DataFrame()

    print('Downloading all available %s data for %s. Be patient..!' %
          (kline_size, symbol))

    klines = binance_client.get_historical_klines(symbol, kline_size,
                                                  oldest_point, newest_point)

    data = DataFrame(klines, columns=['timestamp',
                                      'open',
                                      'high',
                                      'low',
                                      'close',
                                      'volume',
                                      'close_time',
                                      'quote_av',
                                      'trades',
                                      'tb_base_av',
                                      'tb_quote_av',
                                      'ignore'])
    data['timestamp'] = to_datetime(data['timestamp'], unit='ms')

    if len(data_df) > 0:
        temp_df = DataFrame(data)
        data_df = data_df.append(temp_df)
    else:
        data_df = data
    data_df.set_index('timestamp', inplace=True)

    if save:
        data_df.to_csv(filename)
    print('All caught up..!')

    return data_df

# Get past two weeks