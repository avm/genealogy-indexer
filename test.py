from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account credentials JSON file
SERVICE_ACCOUNT_FILE = 'genealogy-indexer-8eb0ba824c9a.json'

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Authenticate and create the service
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=creds)

# Example: Read data from a sheet
spreadsheet_id = '1_OTKGvCBKHvMsHiz2saVZInPXyyWjAgRc_YX5I7Vrzs'
range_name = '721!M7:M9'
sheet = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
values = sheet.get('values', [])

if not values:
    print('No data found.')
else:
    for row in values:
        # Print columns A and B, which correspond to indices 0 and 1.
        print(f'{row[0]}')
