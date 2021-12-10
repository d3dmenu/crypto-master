import pytz
import json
import asyncio
import requests
from operator import itemgetter
from datetime import datetime
from src.config import settings

data, notify = [], []
url = 'https://scanner.tradingview.com/forex/scan'
CURRENCY = [
    'AUDCHF', 'AUDGBP', 'AUDNZD', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURCHF', 'EURNZD',
    'GBPCHF', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDUSD', 'USDCAD', 'USDCHF', 'USDJPY',
    'AUDCAD', 'AUDJPY', 'AUDUSD', 'EURAUD', 'EURCAD', 'EURGBP', 'EURJPY', 'EURUSD',
    'GBPAUD', 'GBPCAD', 'GBPJPY', 'USDJPY', 'NZDUSD'
]


async def get_data_from_trading_view(c: str, t: str):
    headers = {'Content-type': 'application/json', 'User-Agent': 'PostmanRuntime/7.28.4'}
    object = {"symbols": {"tickers": [f"FX_IDC:{c}"], f"query": {"types": ["forex"]}},
              "columns": [f"Recommend.Other|{t}", f"Recommend.All|{t}", f"Recommend.MA|{t}", f"RSI|{t}", f"RSI[1]|{t}",
                          f"Stoch.K|{t}", f"Stoch.D|{t}", f"Stoch.K[1]|{t}", f"Stoch.D[1]|{t}", f"CCI20|{t}",
                          f"CCI20[1]|{t}",
                          f"ADX|{t}", f"ADX+DI|{t}", f"ADX-DI|{t}", f"ADX+DI[1]|{t}", f"ADX-DI[1]|{t}", f"AO|{t}",
                          f"AO[1]|{t}",
                          f"Stoch.RSI.K|{t}", f"Rec.WR|{t}", f"W.R|{t}", f"Rec.BBPower|{t}", f"BBPower|{t}",
                          f"Rec.UO|{t}", f"UO|{t}",
                          f"EMA10|{t}", f"close|{t}", f"SMA10|{t}", f"EMA20|{t}", f"SMA20|{t}", f"EMA30|{t}",
                          f"SMA30|{t}",
                          f"EMA50|{t}", f"SMA50|{t}", f"EMA100|{t}", f"SMA100|{t}", f"EMA200|{t}", f"SMA200|{t}",
                          f"Rec.Ichimoku|{t}",
                          f"Ichimoku.BLine|{t}", f"Rec.VWMA|{t}", f"VWMA|{t}", f"Rec.HullMA9|{t}", f"HullMA9|{t}",
                          f"Pivot.M.Classic.S3|{t}", f"Pivot.M.Classic.S2|{t}", f"Pivot.M.Classic.S1|{t}",
                          f"Pivot.M.Classic.Middle|{t}", f"Pivot.M.Classic.R1|{t}", f"Pivot.M.Classic.R2|{t}",
                          f"Pivot.M.Classic.R3|{t}", f"Pivot.M.Fibonacci.S3|{t}", f"Pivot.M.Fibonacci.S2|{t}",
                          f"Pivot.M.Fibonacci.S1|{t}", f"Pivot.M.Fibonacci.Middle|{t}", f"Pivot.M.Fibonacci.R1|{t}",
                          f"Pivot.M.Fibonacci.R2|{t}", f"Pivot.M.Fibonacci.R3|{t}", f"Pivot.M.Camarilla.S3|{t}",
                          f"Pivot.M.Camarilla.S2|{t}", f"Pivot.M.Camarilla.S1|{t}", f"Pivot.M.Camarilla.Middle|{t}",
                          f"Pivot.M.Camarilla.R1|{t}", f"Pivot.M.Camarilla.R2|{t}", f"Pivot.M.Camarilla.R3|{t}",
                          f"Pivot.M.Woodie.S3|{t}", f"Pivot.M.Woodie.S2|{t}", f"Pivot.M.Woodie.S1|{t}",
                          f"Pivot.M.Woodie.Middle|{t}", f"Pivot.M.Woodie.R1|{t}", f"Pivot.M.Woodie.R2|{t}",
                          f"Pivot.M.Woodie.R3|{t}", f"Pivot.M.Demark.S1|{t}", f"Pivot.M.Demark.Middle|{t}",
                          f"Pivot.M.Demark.R1|{t}"]}

    r = requests.post(url, data=json.dumps(object), headers=headers)
    res = json.loads(r.text)
    indicator = res['data'][0]
    rsi = indicator['d'][3]
    data.append({'currency': c, 'timeframe': t, 'rsi': rsi})


async def main():
    coroutine = []
    for currency in CURRENCY:
        coroutine.append(get_data_from_trading_view(currency, 5))
        coroutine.append(get_data_from_trading_view(currency, 15))
        coroutine.append(get_data_from_trading_view(currency, 30))
        coroutine.append(get_data_from_trading_view(currency, 60))
        coroutine.append(get_data_from_trading_view(currency, 120))
        coroutine.append(get_data_from_trading_view(currency, 240))
    results = await asyncio.wait(coroutine)

    print(f' * There are found total of {len(data)} currency pairs for scan during each period.')
    for val in data:
        if float(val['rsi']) >= 70 or float(val['rsi']) <= 30:
            notify.append(val)

    # Sort dictionary in list
    _filter = sorted(notify, key=itemgetter('timeframe'), reverse=True)

    today = datetime.now(tz=pytz.timezone('Asia/Bangkok'))
    timestamp: str = today.strftime("%d.%m.%Y %H:%M")
    script = f'📣Signal {timestamp}'
    if len(data):
        for ins in _filter:
            script += f'\n✅{ins["currency"]} | {second_to_time_frame(ins["timeframe"])} | {"%.2f" % float(ins["rsi"])}'
        script += f'\n\n📈พบคู่เงินน่าสนใจ {len(_filter)} รายการ'
        send_message_type_text(script)
    else:
        script = 'In these 5 minutes, there are no pairs to buy.'
        send_message_type_text(script)


def second_to_time_frame(time: str):
    compare = {5: 'M5', 15: 'M15', 30: 'M30', 60: 'H1', 120: 'H2', 240: 'H4'}
    return compare[time]


def run():
    print(' * Run task scanning forex indicator')
    asyncio.run(main())
    print(' * Scanning complete')


def send_message_type_text(text: str):
    script = {
        "messages":[
            {
              "type": "text",
              "text": text
            }
        ]
    }

    url = 'https://api.line.me/v2/bot/message/broadcast'
    channels = 'Bearer ' + settings.CHANNEL_ACCESS_TOKEN
    headers = {'Content-type': 'application/json', 'Authorization': channels}
    # data = json.loads(script)
    r = requests.post(url, data=json.dumps(script), headers=headers)