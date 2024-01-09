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
        self.sheet_metadata = self.service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()

    def get_sheet_titles(self) -> [str]:
        sheets = self.sheet_metadata.get('sheets', '')
        return [sheet.get("properties", {}).get("title", "Untitled") for sheet in sheets]

    def get_sheet_content(self, sheet_title: str) -> [[str]]:
        result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=sheet_title).execute()
        return result.get('values', [])

    def get_title(self) -> str:
        return self.sheet_metadata.get('properties', {}).get('title', '')


class Indexer:
    def __init__(self, service_account_file):
        self.sheets = Sheets(service_account_file)
        self.writer = WhooshWriter()

    def process_spreadsheet(self, spreadsheet_id: str) -> None:
        document = self.sheets.get_document(spreadsheet_id)
        sheet_titles = document.get_sheet_titles()
        for title in sheet_titles:
            self.process_sheet(document, title)

    def process_sheet(self, document, title):
        print(f'processing sheet «{title}»')
        rows = document.get_sheet_content(title)
        if len(rows) < 2:
            return

        try:
            base_column = rows[0].index('Фамилия')
        except ValueError:
            base_column = 5
        name_column = base_column + 7
        year_column = name_column + 3
        print(f'detected: name column {name_column}, year column {year_column}')

        locality = document.get_title()
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
            self.writer.add_document(sheet=title, row=rowidx+2, content=name,
                                     locality=locality, birth_year=year)

    def done(self):
        self.writer.close()


class Server:
    def __init__(self, service_account_file):
        idx = Indexer(SERVICE_ACCOUNT_FILE)

        for spreadsheet_id in [KATINO]:
            idx.process_spreadsheet(spreadsheet_id)

        idx.done()

        self.reader = WhooshReader(idx.writer.index)

    def search(self, query: str):
        return self.reader.search(query)


def main():
    server = Server(SERVICE_ACCOUNT_FILE)
    search_results = server.search("Демид")
    for result in search_results:
        print(result)


if __name__ == '__main__':
    main()
