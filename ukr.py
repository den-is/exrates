#!/usr/bin/env python

import requests
import re
import os

from datetime import datetime, date
from pprint import pprint
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# TODO: Update with proper URL to your Google spreadsheet/sheet or provide URL using ENV variable

SPREADSHEET_URL = ''

if os.getenv('SPREADSHEET_URL'):
    _THIS_URL = os.getenv('SPREADSHEET_URL')
elif SPREADSHEET_URL != '':
    _THIS_URL = SPREADSHEET_URL
else:
    print("Link to spreadsheet doesn't exist. Provide one.")

def uah_rates():
    url = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json"
    resp = requests.get(url)
    rates  = resp.json()

    output = {}

    for rate in rates:
        if rate['cc'] in ['USD', 'GBP', 'EUR']:
            rate_date = datetime.strptime(rate['exchangedate'], '%d.%m.%Y')

            print('UAH for', rate['cc'], '-', rate['rate'], '-', rate_date.strftime('%d/%m/%Y'))

            output[rate['cc']] = {
                'rate': rate['rate'],
                'date': rate_date.strftime('%d/%m/%Y')
            }

    return output


def usd_rates():
    # https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html

    output = {}

    urls = [
        'https://api.exchangeratesapi.io/latest?base=EUR&symbols=USD',
        'https://api.exchangeratesapi.io/latest?base=GBP&symbols=USD'
    ]

    for url in urls:
        resp  = requests.get(url)
        resp_json = resp.json()

        cc = resp_json['base']
        rate_date = datetime.strptime(resp_json['date'], '%Y-%m-%d')

        print('USD for', cc, '-', resp_json['rates']['USD'], '-', rate_date.strftime('%d/%m/%Y'))

        output[cc] = {
            'rate': resp_json['rates']['USD'],
            'date': rate_date.strftime('%d/%m/%Y')
        }

    return output


def get_spreadsheet_id(url):
    """Getting spreadsheet and sheet ID from the Google Docs URL to that spreadsheet's sheet

    Just copy address from browser's address bar when you open appropriate Sheet of the Spreadsheet
    """

    result = re.match(r'^.*/d/([a-zA-Z0-9-_]+).*gid=([0-9]+)', url)

    return dict(
        spreadsheet_id = result.group(1),
        sheet_id       = result.group(2)
    )


def get_last_row_data(svc, spreadsheet_id, sheet_name):

    dimmensions_req = svc.spreadsheets().values().append(
        spreadsheetId    = spreadsheet_id,
        range            = sheet_name,
        valueInputOption = 'RAW',
        insertDataOption = 'INSERT_ROWS',
        body             =  {}
    )

    dimmensions_resp = dimmensions_req.execute()

    last_row_cell = re.match(r'^.*:([A-Z]+)([0-9]+)', dimmensions_resp['tableRange'])

    request = svc.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range= "'{}'!A{}:{}{}".format(sheet_name, last_row_cell.group(2), last_row_cell.group(1), last_row_cell.group(2)),
        valueRenderOption='FORMATTED_VALUE',
        dateTimeRenderOption='SERIAL_NUMBER'
    )
    response = request.execute()

    if response.get('values', False):
        return response['values'][0]



def google_sheets_append(svc, spreadsheet_id, sheet_range, row_data):

    table = {
        'majorDimension': 'ROWS',
        'values': [
            row_data
        ]
    }

    request = svc.spreadsheets().values().append(
        spreadsheetId    = spreadsheet_id,
        range            = sheet_range,
        valueInputOption = 'USER_ENTERED',
        insertDataOption = 'INSERT_ROWS',
        body             = table
    )

    response = request.execute()

    return response


def google_auth_sheets(scopes):
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    return service


if __name__ == "__main__":

    uah = uah_rates()
    usd = usd_rates()

    spreadsheet_id  = get_spreadsheet_id(_THIS_URL)['spreadsheet_id']

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

    sheets_svc = google_auth_sheets(SCOPES)

    existing_last_row = get_last_row_data(sheets_svc, spreadsheet_id, '_course')
    print('Existing last row has data:', existing_last_row)

    append_result = google_sheets_append(
        sheets_svc,
        spreadsheet_id,
        '_course',
        [
            date.today().strftime('%d/%m/%Y'),
            "{:.3f}".format( usd['EUR']['rate'] ),
            "{:.3f}".format( 1/uah['USD']['rate'] ),
            "{:.3f}".format( usd['GBP']['rate'] ),
        ]
    )

    pprint(append_result)
