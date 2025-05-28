from flask import Flask, render_template, request, redirect, flash
from google.oauth2 import service_account  # type: ignore
from googleapiclient.discovery import build  # type: ignore
import os
import json

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key')

# Google Sheets setup
SPREADSHEET_ID = '1a4HlzykDhstUvZtR4LPtWEBl-4No2yCAZ_2G1XYWQAU'
RANGE_NAME = 'Sheet1!A1'

# Load credentials from environment variable
service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

# Global submit count (resets if server restarts)
#

@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        submit_count += 1
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
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            #flash(f'Data saved to Google Sheet! (Total submits: {submit_count})', 'success')
            submit_count=sheet.length()
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        return redirect('/')
    return render_template('tsbridge.html', submit_count=submit_count)

if __name__ == '__main__':
    app.run(debug=True)
