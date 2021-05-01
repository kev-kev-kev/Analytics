# Utilities
from pandas import DataFrame
from time import time, mktime
from datetime import datetime
import urllib.parse
from typing import Optional, Dict, Any, List
from binance.client import Client
from pandas import to_datetime
import pathlib
from requests import Request, Session, Response
import hmac

CURRENT_PATH = str(pathlib.Path(__file__).parent)

def get_data_binance(symbol: str, kline_size: str, init_date: str, save=False) -> DataFrame:
    """ This function downloads the data available for the given symbol and
    given timeframe. It also writes the data to the computer if it is
    necessary.

    :param symbol str:     The coin from which we want to download the data.
    :param kline_size str: The timeframe that we want to download the data.
    :param save bool:      A boolean denoting whether we require the data
                           to be saved. Default is False.
    :param init_date str: "01-01-2020" <- how it should look like
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
    oldest_point = datetime.strptime(init_date, "%d-%m-%Y")
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

def str_to_EPOX(date: str) -> int:
    epox_int = mktime(datetime.strptime(date, "%d-%m-%Y").timetuple())
    epox_int = int(epox_int)
    return epox_int

# From: https://github.com/quan-digital/ftx/blob/v1.1/ftx/api.py
class FtxClient:

    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, 
                 api_key="tJiM28KoZUBb_ESuw9bLSCCKesm0xQ8kEX4gAthO", 
                 api_secret="BIAT0328EvQhP4n_-ZoX44rwSSO15XAGEDLpnUW0", 
                 subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = api_key
        self._api_secret = api_secret
        self._subaccount_name = subaccount_name

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('GET', path, params=params)

    def _post(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('POST', path, json=params)

    def _delete(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        return self._request('DELETE', path, json=params)

    def _request(self, method: str, path: str, **kwargs) -> Any:
        request = Request(method, self._ENDPOINT + path, **kwargs)
        self._sign_request(request)
        response = self._session.send(request.prepare())
        return self._process_response(response)

    def _sign_request(self, request: Request) -> None:
        ts = int(time() * 1000)
        prepared = request.prepare()
        signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
        if prepared.body:
            signature_payload += prepared.body
        signature = hmac.new(self._api_secret.encode(), signature_payload, 'sha256').hexdigest()
        request.headers['FTX-KEY'] = self._api_key
        request.headers['FTX-SIGN'] = signature
        request.headers['FTX-TS'] = str(ts)
        if self._subaccount_name:
            request.headers['FTX-SUBACCOUNT'] = urllib.parse.quote(self._subaccount_name)

    def _process_response(self, response: Response) -> Any:
        try:
            data = response.json()
        except ValueError:
            response.raise_for_status()
            raise
        else:
            if not data['success']:
                raise Exception(data['error'])
            return data['result']


    # start_time + resolution
    def get_historical_data(self, market_name: str, 
                                resolution: int, 
                                limit: int, 
                                start_time: float, 
                                end_time: float) -> dict:
        """""
        market_name: name of the market
        resolution: timeframe (in seconds)
        limit: request per second (do 35)
        start_time: Initial date 
        end_time: Final Date
        """""
        params = dict(resolution=resolution,
                      limit=limit,
                      start_time=start_time,
                      end_time=end_time)
        return self._get(f'markets/{market_name}/candles', params)

