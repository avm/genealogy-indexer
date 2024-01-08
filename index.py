from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, NUMERIC, STORED
from whoosh.filedb.filestore import RamStorage

from whoosh.qparser import MultifieldParser

class WhooshReader:
    def __init__(self, index):
        self.index = index

    def search(self, query_str):
        with self.index.searcher() as searcher:
            query = MultifieldParser(["content", "birth_year", "locality"],
                                     self.index.schema).parse(query_str)
            results = searcher.search(query)
            return [f'{hit["locality"]}, лист {hit["sheet"]}, строка {hit["row"]}: {hit["content"]} / {hit["birth_year"]}' for hit in results]


class WhooshWriter:
    def __init__(self):
        # Define the schema for the document
        schema = Schema(
            content=TEXT(stored=True),
            locality=TEXT(stored=True),
            birth_year=NUMERIC(stored=True),
            sheet=STORED,
            row=STORED,
        )
        # Create an in-memory index
        self.storage = RamStorage()
        self.index = self.storage.create_index(schema)
        self.writer = self.index.writer()

    def add_document(self, sheet, row, content, locality, birth_year):
        if birth_year.isdigit():
            self.writer.add_document(sheet=sheet, row=row, content=content, locality=locality, birth_year=birth_year)
        else:
            self.writer.add_document(sheet=sheet, row=row, content=content, locality=locality)

    def close(self):
        self.writer.commit()
        self.index.close()

