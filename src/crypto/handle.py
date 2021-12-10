import json
import requests

from nested_lookup import nested_lookup
from src.config import settings
from requests.sessions import Session


class CoinMarketCap():
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': settings.API_KEY
    }

    @staticmethod
    def get_all_crypto_coin() -> dict:
        # call api from coin market cap
        parameters = {
            'start': '1',
            'limit': '5000',
            'convert': 'thb'
        }

        response = requests.get(settings.urls['coin-market-all'], params=parameters,
                                headers=CoinMarketCap.headers).json()

        coins = response['data']
        for index in coins:
            slug, symbol = index['slug'], index['symbol']
            print(f"'{symbol}': '{slug}',")

    @staticmethod
    def get_data_crypto(**kwargs) -> dict:

        """
        Readme:     You can find the coin price using api system from coin market cap
        Warnings:   limit requests data with api 333 req / day
        """

        _types = kwargs.get('coin')

        parameters = {
            'symbol': kwargs.get('coin'),
            'convert': kwargs.get('convert')
        }

        # require types check is multiple or single
        if type(_types) != list:
            # Create session
            session = Session()

            # Update header from session
            session.headers.update(CoinMarketCap.headers)

            # request api from url and get response data
            response = session.get(settings.urls['coin-market'], params=parameters)
            json_res = json.loads(response.text)

            # get coin price only from data
            price = CoinMarketCap.format_price_crypto(json_res)
            return {parameters['symbol']: price}

        if type(_types) == list:
            protal = {}
            # Create session
            session = Session()

            # Update header from session
            session.headers.update(CoinMarketCap.headers)

            for crypto_name in parameters['symbol']:
                # request api from url and get response data
                response = session.get(settings.urls['coin-market'], params={
                    'symbol': crypto_name,
                    'convert': parameters['convert']
                })
                json_res = json.loads(response.text)

                protal[crypto_name] = CoinMarketCap.format_price_crypto(json_res)

            return protal

        raise 'Validation type data error'

    @staticmethod
    def format_price_crypto(data: dict):
        """
        API Detail
        Cache | Update frequency: Every 60 seconds
        """

        # Show  price only
        if not data:
            raise 'Validation error!'

        find_price = nested_lookup('price', data)

        return find_price
