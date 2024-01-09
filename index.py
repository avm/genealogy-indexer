from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, NUMERIC, STORED
from whoosh.filedb.filestore import RamStorage
from whoosh.support.charset import charset_table_to_dict
from whoosh.analysis import CharsetFilter, RegexTokenizer

from whoosh.qparser import MultifieldParser

class WhooshReader:
    def __init__(self, index):
        self.index = index

    def search(self, query_str):
        with self.index.searcher() as searcher:
            query = MultifieldParser(["name", "born", "from"],
                                     self.index.schema).parse(query_str)
            results = searcher.search(query, limit=None)
            return [f'{hit["from"]}, лист {hit["sheet"]}, строка {hit["row"]}: '
                    f'{hit["name"]} / {hit.get("born", "?")}' for hit in results]


class WhooshWriter:
    def __init__(self):
        charmap = charset_table_to_dict(
            'А..Я->а..я, '
            'Ё->ь, ё->ь, Е->ь, е->ь, И->ь, и->ь, Ы->ь, ы->ь, '
            'А->ъ, а->ъ, О->ъ, о->ъ, '
            'Ф->п, ф->п')
        analyzer = RegexTokenizer() | CharsetFilter(charmap)
        # Define the schema for the document
        schema = Schema(
            name=TEXT(stored=True, analyzer=analyzer),
            born=NUMERIC(stored=True),
            sheet=STORED,
            row=STORED,
        )
        # Create an in-memory index
        self.storage = RamStorage()
        self.index = self.storage.create_index(schema)
        self.writer = self.index.writer()
        self.writer.add_field('from', TEXT(stored=True))

    def add_document(self, sheet, row, content, locality, birth_year):
        doc = {
            'sheet': sheet,
            'row': row,
            'name': content,
            'from': locality,
        }
        if birth_year.isdigit():
            doc['born'] = birth_year
        self.writer.add_document(**doc)

    def close(self):
        self.writer.commit()
        self.index.close()

