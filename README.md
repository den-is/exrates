Basic example on how to grab Currency Exchange Rates from different web sources and upload received data to a Google Spreadsheet

Using [Google Sheets API V4](https://developers.google.com/sheets/api)

# Usage
- make sure that you have **Python 3** installed on your system
- I suggest you to use `venv`, `docker` or `virtualenv` to run this project in isolated clean environment
- Install dependencies from included `requirements.txt` - `pip install -U -r requirements.txt`
- Follow [instructions](https://developers.google.com/sheets/api/quickstart/python) to get your Google Sheets API key, i.e. get `credentials.json` and put it in the same directory.
- In `ukr.py` update `SPREADSHEET_URL` with link to your Google Spreadsheet
- Run scripts directly `./ukr.py` or `python urk.py`
