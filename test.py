#!/usr/bin/env python

from google.oauth2 import service_account
from googleapiclient.discovery import build
from index import WhooshReader, WhooshWriter

# Path to your service account credentials JSON file
SERVICE_ACCOUNT_FILE = 'genealogy-indexer-8eb0ba824c9a.json'

# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

KATINO = '1_OTKGvCBKHvMsHiz2saVZInPXyyWjAgRc_YX5I7Vrzs'


class Sheets:
    def __init__(self, account_file):
        # Authenticate and create the service
        creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)

    def get_document(self, spreadsheet_id):
        return Spreadsheet(self.service, spreadsheet_id)

class Spreadsheet:
    def __init__(self, service, spreadsheet_id: str):
        self.service = service
        self.spreadsheet_id = spreadsheet_id
        self.sheet_metadata = self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    def get_sheet_titles(self) -> [str]:
        sheets = self.sheet_metadata.get('sheets', '')
        return [sheet.get("properties", {}).get("title", "Untitled") for sheet in sheets]

    def get_sheet_content(self, sheet_title: str) -> [[str]]:
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=sheet_title).execute()
        return result.get('values', [])

    def get_title(self) -> str:
        return self.sheet_metadata.get('properties', {}).get('title', '')


def main():
    sheets = Sheets(SERVICE_ACCOUNT_FILE)
    writer = WhooshWriter()

    for spreadsheet_id in [KATINO]:
        document = sheets.get_document(spreadsheet_id)
        locality = document.get_title()
        sheet_titles = document.get_sheet_titles()
        for title in sheet_titles:
            print(f'processing sheet «{title}»')
            rows = document.get_sheet_content(title)
            if len(rows) < 2:
                continue

            try:
                base_column = rows[0].index('Фамилия')
            except ValueError:
                base_column = 5
            name_column = base_column + 7
            year_column = name_column + 3
            print(f'detected: name column {name_column}, year column {year_column}')

            for rowidx, row in enumerate(rows[1:]):
                print('processing row:', row)
                if (len(row) < year_column + 1):
                    print('no data')
                    continue
                name = row[name_column]
                if not name:
                    continue
                year = row[year_column]
                print('adding document:', name, year)
                writer.add_document(sheet=title, row=rowidx+2, content=name, locality=locality, birth_year=year)

    writer.close()

    reader = WhooshReader(writer.index)
    search_results = reader.search("Демид")
    for result in search_results:
        print(result)


if __name__ == '__main__':
    main()
