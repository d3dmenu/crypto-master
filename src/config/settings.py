import os
import sys

import environ

env = environ.Env()

# API Coin market cap
API_KEY = env.str('API_KEY', '6cf06008-f1d3-45b2-9555-3ff76eec016e')

# Base url path data forex realtime scraping
urls = {
    'forex-market': 'https://scanner.tradingview.com/forex/scan',
    'coin-market-all': 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest',  # get all crypto coin
    'coin-market': 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'  # specific check quote coin
}

# Line Developer
LINE_API = env.str('LINE_API', 'https://api.line.me/v2/bot/message/reply')
CHANNEL_SECRET = env.str('CHANNEL_SECRET', 'c43b870f45352a00e8099fd8712c5f76')
CHANNEL_ACCESS_TOKEN = env.str('CHANNEL_ACCESS_TOKEN',
                               'c507YkAdo2ZuDCuGleZsrgNBFTpXSqXOPyngcTVbRgwfZdM69ve8CtT2d+TLHL3fZV7w+sa69kiDNWiu54cYHRk9wqJHVjRTpWZmBKtM3tLRmSJv1UR2W3i3/tc5SuYJPFk1Q31YG7PGzGDUMtH7SQdB04t89/1O/w1cDnyilFU=')

# Settings delay for request api
DELAY_REQUEST = env.int('DELAY_REQUEST', 60)
DELAY_FOREX = env.int('DELAY_FOREX', 5)
# Load task from csv
DATABASE = env.str('DATABASE', 'schedules.csv')

# Forex currency list

CURRENCY = [
    'AUDCHF', 'AUDGBP', 'AUDNZD', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURCHF', 'EURNZD',
    'GBPCHF', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY',
    'AUDCAD', 'AUDJPY', 'AUDUSD', 'EURAUD', 'EURCAD', 'EURBGP', 'EURJPY', 'EURUSD',
    'GBPAUD', 'GBPCAD', 'GBPJPY', 'USDJPY', 'NZDUSD'
]

# Firebase SDK
SCHEDULES_COLLECTION = env.str('SCHEDULES_COLLECTION', 'schedules')