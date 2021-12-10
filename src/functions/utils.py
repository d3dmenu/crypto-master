import re
import os
import csv
import json
import uuid
import requests

from src.functions.reference import *
from src.config.base import coins
from src.config import settings
from src.crypto.handle import CoinMarketCap
from src.scraper.handle import get_data_crypto
from datetime import datetime
from src.forex import handle


headers_template = ['UID', 'SYMBOL', 'PRICE', 'TYPES', 'STATUS', 'USERID']


def decision(data: dict) -> str:
    intent = data['intent']
    temp = data

    if intent == GET_QUOTE_CRYPTO:
        info = get_coin_name(data['message'])
        if len(info) > 1:
            return 'ระบบการค้นหาหลายเหรียญยังไม่พร้อมใช้งาน\n\nFunction search multiple-coin is not yet available.'

        if len(info) == 0:
            return 'ตรวจไม่พบเหรียญคริปโตนี้ในระบบ\n\nCrypto coin not found in system. Please try again.'

        # Input data info to dictionary
        for value in info:
            temp['crypto'] = {value: None}
        temp['count'] = len(info)

        # Get coin with API coin market cap
        """
        object = CoinMarketCap()
        response = object.get_data_crypto(coin=info, convert='thb')
        """
        # Get coin with Web Scraping
        temp = get_data_crypto(temp)
        # Validate flex type
        response = validate_type(temp)

        return response

    elif intent == NOTIFY_TYPE_MORE_THAN:
        symbol = get_coin_name(data['message'])
        if not symbol:
            return 'กรุณาระบุชื่อเหรียญด้วยครับ'

        user_price = get_price_value(data['message'])
        key = uuid.uuid4().hex[:6].upper()
        params = {
            'UID': key,
            'SYMBOL': symbol[0],
            'PRICE': user_price,
            'TYPES': 'More than',
            'STATUS': 'Pending',
            'USERID': data['user_id']
        }
        add_row_csv(params)
        response = {
            'flex-mock': get_flex_mock('message_add_schedule.json'),
            'script': symbol[0]
        }
        return f'🔰 ระบบแจ้งเตือน\nหมายเลขเตือน: {key}\nประเภท: แจ้งเตือนเมื่อราคาขึ้น\n\nระบบบันทึกการแจ้งเตือนเรียบร้อย'

    elif intent == NOTIFY_TYPE_LESS_THAN:
        symbol = get_coin_name(data['message'])
        if not symbol:
            return 'กรุณาระบุชื่อเหรียญด้วยครับ'

        user_price = get_price_value(data['message'])
        key = uuid.uuid4().hex[:6].upper()
        params = {
            'UID': key,
            'SYMBOL': symbol[0],
            'PRICE': user_price,
            'TYPES': 'Less than',
            'STATUS': 'Pending',
            'USERID': data['user_id']
        }
        add_row_csv(params)
        return f'🔰 ระบบแจ้งเตือน\nหมายเลขเตือน: {key}\nประเภท: แจ้งเตือนเมื่อราคาลง\n\nระบบบันทึกการแจ้งเตือนเรียบร้อย'

    elif intent == RESET_NOTIFY:
        with open(settings.DATABASE, mode='w') as csv_file:
            fieldnames = headers_template
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
        print(' * Reset schedules files complete.')

    elif intent == GET_SIGNALS:
        handle.run()

    return None


def extract_data(data: dict) -> dict:
    object = {
        'intent': get_intent_name(data),
        'message': get_message(data),
        'reply_token': get_reply_token(data),
        'user_id': get_user_id(data),
    }
    return object


def get_reply_token(data: dict) -> str:
    return data['originalDetectIntentRequest']['payload']['data']['replyToken']


def get_message(data: dict) -> str:
    return data['originalDetectIntentRequest']['payload']['data']['message']['text']


def get_intent_name(data: dict) -> str:
    return data["queryResult"]["intent"]["displayName"]


def get_user_id(data: dict) -> str:
    return data['originalDetectIntentRequest']['payload']['data']['source']['userId']


def get_coin_name(msg: str) -> list:
    get_name = msg.split()
    reg = re.compile(r'[a-zA-Z]')
    info = []
    for msg in get_name:
        if reg.match(msg) and msg.upper() in coins:
            info.append(msg.upper())

    if len(info) == 0:
        return False
    return info


def get_price_value(msg: str) -> float:
    price = None
    get_price = msg.split()
    reg = re.compile(r"^(?=.?\d)\d*[.,]?\d*$|^((\d){1,3},*){1,5}\.(\d){2}$")
    for msg in get_price:
        if reg.match(msg):
            price = msg.replace('฿', '')
    return float(price)


def validate_type(data: dict):
    # Variable
    # Request single coin
    count = data['count']
    intent = data['intent']

    if count == 1 and intent == GET_QUOTE_CRYPTO:
        return request_single_coin(data)


def get_flex_mock(file_name: str):
    files = 'src/config/template/' + file_name

    with open(files, "r") as script:
        code = json.load(script)
        string = json.dumps(code, ensure_ascii=False)
        data = string
    script.close()
    return data


def request_single_coin(data: dict) -> str:
    today = datetime.now()

    # Create format for JSON Template
    coin_name: str = None
    symbol: str = None
    credit: str = 'CoinMarketCap.com'
    timestamp: str = today.strftime("%Y.%m.%d %H:%M")
    url: str = data['url']

    data['flex-type'] = COMPARE[GET_QUOTE_CRYPTO]
    files = 'src/config/template/' + data['flex-type']

    with open(files, "r") as script:
        code = json.load(script)
        string = json.dumps(code, ensure_ascii=False)
        data['flex-mock'] = string

    # Added script to dictionary
    for key, value in safe_get(data, 'crypto').items():
        coin_name = str(coins[key].upper())
        symbol = key.upper()

    price = data['crypto'][symbol]['price']
    high = data['crypto'][symbol]['high']
    low = data['crypto'][symbol]['low']
    data['script'] = (coin_name, symbol, price, credit, timestamp, high, low, url)

    return data


def safe_get(dct, *keys):
    for key in keys:
        try:
            dct = dct[key]
        except KeyError:
            return None
    return dct


def init_file():
    file = settings.DATABASE  # Add /app/ with heroku server
    if os.path.isfile(file):
        print(' * Reading task from file schedule.')

    else:
        with open(settings.DATABASE, mode='w') as csv_file:
            fieldnames = headers_template
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
        print(' * Create schedules files complete.')


def add_row_csv(params: dict):
    init_file()

    # Open your CSV file in append mode
    # Create a file object for this file
    file = settings.DATABASE  # Add /app/ with heroku server
    if os.path.isfile(file):
        with open(settings.DATABASE, mode='a') as schedules:
            headers = headers_template
            # You will get a object of DictWriter
            writer = csv.DictWriter(schedules, fieldnames=headers)
            # Pass the dictionary as an argument to the Writerow()
            writer.writerow(params)
            # Close the file object

        print(f' * Added schedule job {params["UID"]} success.')
    else:
        print(f' * schedules.csv not found from current path')


def update_row_csv(uid: str):
    # get information
    with open(settings.DATABASE, 'r') as file:
        value = csv.reader(file)
        data = list(value)

    for index in data:
        if index[0] == uid:
            index[4] = 'Activate'

    with open(settings.DATABASE, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        # write multiple rows
        writer.writerows(data)

