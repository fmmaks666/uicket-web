import sqlite3 as sql
from pathlib import Path
from os import makedirs
from shutil import rmtree
from whoosh.index import create_in, exists_in
from whoosh.fields import Schema, TEXT, ID
from main import UserSettings

table = """CREATE TABLE IF NOT EXISTS releases(id INTEGER PRIMARY KEY, name TEXT, url TEXT)"""

db_path = input("Enter path to DB: ")
db = sql.connect(db_path)
cursor = db.cursor()
cursor.execute(table)
highest = cursor.execute("SELECT COUNT(*) FROM releases").fetchall()[0][0]
data = cursor.execute("SELECT * FROM releases")

schema = Schema(id=ID(stored=True, unique=True), name=TEXT(stored=True), url=TEXT(stored=True))
path = input("Path to index?: ")
if not path:
    path = "index"
config = UserSettings()
config.update_db(db_path)

def create(data, highest):
    if Path(path).exists():
        rmtree(path, ignore_errors=True)
	
    makedirs(path)
    index = create_in(path, schema)
    if not data:
        exit()
	

    with index.writer() as writer:
        for release_id, name, url in data:
            writer.add_document(id=str(release_id), name=name, url=url)
            print(f"\033[K- {release_id / highest * 100:.2f}%", end="\r")
		
create(data, highest)
print()
