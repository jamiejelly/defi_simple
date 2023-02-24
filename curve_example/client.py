import hmac
import os
import requests
from urllib.parse import urlencode

from utils import get_timestamp_ms, make_get_request

# api's
EXCHANGE_TO_BASE_URL = {
    'BINANCE': 'https://api.binance.com/api/v3',
    'BINANCE_FUTURES_USDM': 'https://fapi.binance.com/fapi/v1',
    'BINANCE_FUTURES_COINM': 'https://dapi.binance.com',
    'BINANCE_US': 'https://api.binance.us',
    'BITFINEX': 'https://api-pub.bitfinex.com/v2',
    'COINBASE': 'https://api.pro.coinbase.com',
    'COINGECKO': 'https://api.coingecko.com/api/v3',
    'DEFILLAMA': 'https://api.llama.fi',
    'DERIBIT': 'wss://www.deribit.com/ws/api/v2',
    'KRAKEN': 'https://api.kraken.com/0/public',
}


class BinanceGateway:
    
    def __init__(self, exchange, api_key, api_secret):
        self.base_url = EXCHANGE_TO_BASE_URL[exchange.upper()]
        self.api_key = api_key
        self.api_secret = api_secret

    def hashing(self, query_string):
        return hmac.new(self.api_secret.encode("utf-8"), query_string.encode("utf-8"), 'sha256').hexdigest()

    def make_signed_request(self, method, endpoint, body_in={}, verbose=False):
        url = os.path.join(self.base_url, endpoint)

        body = dict(body_in)
        body['timestamp'] = get_timestamp_ms() 

        # headers
        headers = {
            'X-MBX-APIKEY': self.api_key,  
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8;',
        }

        if method == 'GET':
            path = urlencode(body)
            signature = self.hashing(path)
            url = url + f"?{path}&signature={signature}"
            if verbose: 
                print(url)
            resp = requests.get(url, headers=headers)

        elif method == 'POST':
            body['signature'] = self.hashing(urlencode(body))
            resp = requests.post(url, headers=headers, data=body)

        elif method == 'DELETE':
            path = urlencode(body)
            signature = self.hashing(path)
            url = url + f"?{path}&signature={signature}"
            if verbose:
                print(url)
            resp = requests.delete(url, headers=headers)

        print(url)
        # print(resp)
        return resp.json()
    
    def make_public_request(self, endpoint, **args):
        return make_get_request(self.base_url, endpoint, **args)
    
    def get_account(self):
        return self.make_signed_request("GET", "account")
    
    def get_order_book(self, symbol, limit=10):
        return self.make_public_request("depth", symbol=symbol, limit=limit)
    
    def post_order(self, symbol, side, type_, quantity, price, timeInForce):
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": type_.upper(),
            "quantity": quantity,
            "price": price,
            "timeInForce": timeInForce,
        }
        return self.make_signed_request("POST", "order", body_in=params)
    
    def cancel_open_orders(self, symbol):
        """
        symbol (use base), ie BTC , function converts to BTCUSDT
        """
        return self.make_signed_request("DELETE", "allOpenOrders", body_in={'symbol': f'{symbol}USDT'})
    
    def get_spot(self, symbs):
        if isinstance(symbs, str):
            symbs = [symbs]
        binance_prices = requests.get(f"https://api.binance.com/api/v3/ticker/price").json()
        return {s: float(d['price']) for d in binance_prices for s in symbs if d['symbol'] == f'{s}USDT'}
    
    def get_open_futs_positions(self, ignore_usdt_in_key=False):
        position = self.get_account()['positions']
        open_futs = {d['symbol']: float(d['positionAmt']) for d in position if abs(float(d['positionAmt'])) > 0}
        if ignore_usdt_in_key:
            open_futs = {k[:-4]: v for k, v in open_futs.items()}
        return open_futs

    
    
    
    
    