#!/usr/bin/python

# Schedule Library imported
import asyncio
import os
import csv
# import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper.handle import get_price_only
from src.config import settings
from src.functions.utils import read_collection_firebase, delete_document_firebase
from src.forex.handle import send_message_type_text

# Setting background scheduler task
sched = BackgroundScheduler({'apscheduler.timezone': 'Asia/Bangkok'})
print(' * Memo SDK version portable 1.4.6')
print(' * Setting background scheduler task success.')


@sched.scheduled_job('interval', seconds=settings.DELAY_REQUEST)
def system_notify_price_coins():
    print(' * Scanning schedule job')
    MORETHAN, LESSTHAN = 'More than', 'Less than'
    data = read_collection_firebase()
    quote = {}
    print(quote, len(quote))
    for doc in data:

        uid = doc.id
        info = doc.to_dict()

        price = info['PRICE']
        types = info['TYPES']
        symbol = info['SYMBOL'].upper()

        # Get price server from api or web scraping
        if symbol not in quote:
            quote[symbol] = get_price_only(symbol)

        logs = f' * Schedule ID: {uid} is successfully executed.'
        message = f'แจ้งเตือนหมายเลข: {uid}\nเหรียญ: {symbol}\nราคา: {price}'
        if types == MORETHAN and float(price) < float(quote[symbol]):
            print(logs)
            send_message_type_text(message)
            delete_document_firebase(uid)

        elif type == LESSTHAN and float(price) > float(quote[symbol]):
            print(logs)
            send_message_type_text(message)
            delete_document_firebase(uid)


sched.start()

# Shut down the scheduler when exiting the app
# atexit.register(lambda: schedule.shutdown())
