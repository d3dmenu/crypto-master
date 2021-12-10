import os
import csv

headers_template = ['UID', 'SYMBOL', 'PRICE', 'TYPES', 'STATUS', 'USERID']
params = {
    'UID': 'test',
    'SYMBOL': 'test',
    'PRICE': 'test',
    'TYPES': 'More than',
    'STATUS': 'Pending',
    'USERID': 'test'
}


def init():
    file = 'schedules.csv'  # Add /app/ with heroku server
    if os.path.isfile(file):
        print(' * Reading task from file schedule.')

    else:
        with open(file, mode='w') as csv_file:
            fieldnames = headers_template
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
        print(' * Create schedules files complete.')


def add_row_csv(params: dict):
    init()

    # Open your CSV file in append mode
    # Create a file object for this file
    file = 'schedules.csv'  # Add /app/ with heroku server
    if os.path.isfile(file):
        with open(file, mode='a') as schedules:
            headers = headers_template
            # You will get a object of DictWriter
            writer = csv.DictWriter(schedules, fieldnames=headers)
            # Pass the dictionary as an argument to the Writerow()
            writer.writerow(params)
            # Close the file object

        print(f' * Added schedule job {params["UID"]} success.')
    else:
        print(f' * schedules.csv not found from current path')

init()
add_row_csv(params)