# From: https://github.com/quan-digital/ftx/blob/v1.1/ftx/api.py

from time import time, mktime
from datetime import datetime
import urllib.parse
from typing import Optional, Dict, Any, List

from requests import Request, Session, Response
import hmac

key = "tJiM28KoZUBb_ESuw9bLSCCKesm0xQ8kEX4gAthO"
secret = "BIAT0328EvQhP4n_-ZoX44rwSSO15XAGEDLpnUW0"

def str_to_EPOX(date: str) -> int:
    epox_int = mktime(datetime.strptime(date, "%d-%m-%Y").timetuple())
    epox_int = int(epox_int)
    return epox_int

class FtxClient:

    _ENDPOINT = 'https://ftx.com/api/'

    def __init__(self, base_url=None, api_key=None, api_secret=None, subaccount_name=None) -> None:
        self._session = Session()
        self._api_key = key
        self._api_secret = secret
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
        return self._get(f'markets/{market_name}/candles', dict(resolution=resolution,limit=limit,start_time=start_time,end_time=end_time))

