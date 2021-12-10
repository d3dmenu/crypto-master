#!/usr/bin/python

# Schedule Library imported
import asyncio
import os
import csv
# import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper.handle import get_price_only
from src.config import settings
from src.functions.utils import update_row_csv
from src.forex.handle import send_message_type_text

# Setting background scheduler task
schedule = BackgroundScheduler({'apscheduler.timezone': 'Asia/Bangkok'})
print(' * Memo SDK version portable 1.3.5')
print(' * Setting background scheduler task success.')


# @schedule.scheduled_job('cron', hour='00', minute='00')
# def system_repair_data():
#     # get information
#     with open('schedules.csv', 'r') as file:
#         value = csv.reader(file)
#         data = list(value)
#     file.close()
#
#     # repair data
#     for index in range(len(data)):
#         if data[index][4] == 'Activate':
#             del data[index]
#
#     # save data
#     with open('schedules.csv', 'w', encoding='UTF8') as f:
#         writer = csv.writer(f)
#         # write multiple rows
#         writer.writerows(data)
#     f.close()


@schedule.scheduled_job('interval', seconds=settings.DELAY_REQUEST)
def system_notify_price_coin():
    MORETHAN, LESSTHAN = 'More than', 'Less than'
    path = os.getcwd() + '/' + settings.DATABASE
    if os.path.isfile(path):
        tasks = []
        with open(settings.DATABASE, 'r') as file:
            schedule = csv.DictReader(file)

            # Filter data field status
            for row in schedule:
                if row['STATUS'] != 'Activate':
                    tasks.append(row)

            for get in tasks:
                # Get data from csv schedule
                uid = get['UID']
                symbol = get['SYMBOL']
                price = get['PRICE']
                types = get['TYPES']

                # Get price server from api or web scraping
                server = get_price_only(symbol.upper())

                logs = f' * Schedule ID: {uid} is successfully executed.'
                message = f'แจ้งเตือนหมายเลข: {uid}\nเหรียญ: {symbol}\nราคา: {price}'
                if types == MORETHAN and float(price) < float(server):
                    print(logs)
                    send_message_type_text(message)
                    # Change status to disabled
                    update_row_csv(uid)

                elif type == LESSTHAN and float(price) > float(server):
                    print(logs)
                    send_message_type_text(message)
                    # Change status to disabled
                    update_row_csv(uid)


# Shut down the scheduler when exiting the app
# atexit.register(lambda: schedule.shutdown())
