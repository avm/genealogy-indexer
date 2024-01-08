from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.filedb.filestore import RamStorage

from whoosh.qparser import QueryParser

class WhooshReader:
    def __init__(self, index):
        self.index = index

    def search(self, query_str):
        with self.index.searcher() as searcher:
            query = QueryParser("content", self.index.schema).parse(query_str)
            results = searcher.search(query)
            return [hit["content"] for hit in results]


class WhooshWriter:
    def __init__(self):
        # Define the schema for the document
        schema = Schema(content=TEXT(stored=True))
        # Create an in-memory index
        self.storage = RamStorage()
        self.index = self.storage.create_index(schema)

    def add_document(self, content):
        writer = self.index.writer()
        writer.add_document(content=content)
        writer.commit()

    def close(self):
        self.index.close()

