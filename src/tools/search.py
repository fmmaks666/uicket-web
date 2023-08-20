from __future__ import annotations
from pathlib import Path
from os import path, makedirs
from shutil import rmtree
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, OrGroup
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from tools.database import Database
PATH = path.dirname(__file__)


class Search:
	
	
    def __init__(self):
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            name=TEXT(stored=True),
            url=TEXT(stored=True),
        )
        self.index = None
        self.path = path.join(PATH, "data", "index")

    def search(self, query) -> list[tuple[int, str, str], ...] | None:
        if self.index is None:
            return
        with self.index.searcher() as searcher:
            parser = QueryParser("name", self.index.schema, group=OrGroup)
            parsed = parser.parse(query)
            output = searcher.search(parsed)
            results = []
            for i in output:
                results.append(((int(i["id"])), i["name"], i["url"]))

            return results

    def load(self):
        if exists_in(self.path) and self.index is None:
            self.index = open_dir(self.path)

    def create(self, db: Database):
        if Path(self.path).exists():
            rmtree(self.path, ignore_errors=True)

        makedirs(self.path)
        self.index = create_in(self.path, self.schema)
        data = db.get_all(True)
        if data is None:
            return

        with self.index.writer() as writer:
            for release_id, name, url in data:
                writer.add_document(id=str(release_id), name=name, url=url)
