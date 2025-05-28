from flask import Flask, render_template, request, redirect, flash
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import threading

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key')

SPREADSHEET_ID = '1a4HlzykDhstUvZtR4LPtWEBl-4No2yCAZ_2G1XYWQAU'
RANGE_NAME = 'Sheet1!A1:H'

# Load credentials from environment variable
service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Thread-safe counter
submit_count_lock = threading.Lock()
submit_count = None

def initialize_submit_count():
    global submit_count
    result = sheet.values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    values = result.get('', [])
    submit_count = max(len(values) - 1, 0) if values else 0

# Initialize the count at startup
initialize_submit_count()

@app.route('/', methods=['GET', 'POST'])
def index():
    global submit_count
    if request.method == 'POST':
        try:
            values = [[
                request.form.get('fullname'),
                request.form.get('domain'),
                request.form.get('college'),
                request.form.get('passout'),
                request.form.get('contact'),
                request.form.get('email'),
                request.form.get('option'),
                request.form.get('queries')
            ]]
            body = {'values': values}
            response = sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            # Optimistically increment the counter
            with submit_count_lock:
                submit_count += 1
            flash('Data saved to Google Sheet!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        return redirect('/')
    # No API call here; just use the cached count
    with submit_count_lock:
        count = submit_count
    return render_template('tsbridge.html', submit_count=count)

if __name__ == '__main__':
    app.run(debug)

