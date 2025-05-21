from flask import Flask, render_template, request, redirect,flash
from google.oauth2 import service_account # type: ignore
from googleapiclient.discovery import build # type: ignore

app = Flask(__name__,static_folder='static', template_folder='templates')

# import secrets
import os
app.secret_key = '210f8bb0cb632dc8e3fe08a1207f7873'  

 # Generate a random secret key for development
#app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-key')

# Replace these values
# SERVICE_ACCOUNT_FILE = 'service_account.json'  # Correct path
SPREADSHEET_ID = '1a4HlzykDhstUvZtR4LPtWEBl-4No2yCAZ_2G1XYWQAU'  # From your sheet URL
RANGE_NAME = 'Sheet1!A1'  # Adjust as needed
# Load credentials
import os
import json


# Load credentials from environment variable
service_account_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# )


# credentials = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE,
#     scopes=['https://www.googleapis.com/auth/spreadsheets']
# )
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()

@app.route('/', methods=['GET', 'POST'])
def index():
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
            sheet.values().append(
                spreadsheetId=SPREADSHEET_ID,
                range=RANGE_NAME,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            flash('Data saved to Google Sheet!', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
        return redirect('/')
    return render_template('tsbridge.html')

if __name__ == '__main__':
    app.run(debug=True)


