from os import truncate
import requests
from bs4 import BeautifulSoup
from src.config.base import coins


def get_price_only(symbol: str, url: str = 'https://coinmarketcap.com/th/currencies/') -> float:
    isalnum = ['$', '฿', ',']
    try:
        if coins[symbol]:
            name = coins[symbol]
            load = requests.get(url + name)
            soup = BeautifulSoup(load.content, 'lxml')

            # Get price currency
            for div in soup.findAll('div', {'class': 'priceValue'}):
                quote = str(div.text)[1:]
                return float(quote.replace(',', ''))

    except Exception as e:
        return 'The structure of the website has changed.'


def get_data_crypto(temp: dict = None, url: str = 'https://coinmarketcap.com/th/currencies/') -> dict:
    quote_hl, data = [], []
    if not temp:
        return None

    # get name crypto from field crypto
    for key, value in safe_get(temp, 'crypto').items():
        data.append(key)

    for name in data:
        try:
            if coins[name]:
                value = coins[name]
                load = requests.get(url + value)
                soup = BeautifulSoup(load.content, 'lxml')
                # add url
                temp['url'] = url + value

                # Get price currency
                for div in soup.findAll('div', {'class': 'priceValue'}):
                    quote = str(div.text)
                    temp['crypto'][name] = {'price': quote.replace('฿', '฿ ')}

                # Get 24h High / Low
                for div in soup.findAll('span', {'class': 'n78udj-5'}):
                    quote = str(div.text)
                    quote_hl.append(quote.replace('฿', '฿ '))

                temp['crypto'][name]['low'] = quote_hl[0]
                temp['crypto'][name]['high'] = quote_hl[1]

        except Exception as e:
            return e
    return temp


def safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct
