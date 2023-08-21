from random import choice
from requests import get
from bs4 import BeautifulSoup
import sqlite3 as sql

PAGE_URL = "https://rezka.ag/page/{}"

AGENTS = ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"]

table = """CREATE TABLE IF NOT EXISTS releases(id INTEGER PRIMARY KEY, name TEXT, url TEXT UNIQUE)"""
insert = """INSERT INTO releases(name, url) VALUES(?, ?)"""

def parse_page(page, cursor, updating=False):
    user_agent = choice(AGENTS)
    headers = {"User-Agent": user_agent}
    page = get(PAGE_URL.format(page), headers=headers).text
    soup = BeautifulSoup(page, "html.parser")
    things = soup.select("#main > div.b-container.b-content.b-wrapper > div.b-content__inline > div > div.b-content__inline_items > div.b-content__inline_item > div.b-content__inline_item-link")
    if updating:
        things = things
    else:
        things = things[::-1]
    for thing in things:
        data = thing.find_all("a")
        for i in data:
            name = i.get_text()
            url = i["href"]
            try:
                cursor.execute(insert, (name, url))
            except sql.IntegrityError:
                if updating:
                    return True
                continue


def main(cursor, db):
    pages = int(input("Enter amount of pages to parse: "))
    updating = bool(input("Are You going to update DB?: "))
    print(f"Mode: {'Updating' if updating else 'Creating'}")
    page = 1 if updating else pages
    current = 1
    if updating:
        while page <= pages:
            result = parse_page(page, cursor, updating)
            if result:
                print("- Updated")
                break
            print(f"\033[K- {page / pages * 100:.2f}%", end="\r")
            page += 1
    else:
        while page >= 1:
            result = parse_page(page, cursor, updating)
            if result:
                print("- Unexpected exit")
                break
            print(f"\033[K- {current / pages * 100:.2f}%", end="\r")
            page -= 1
            current += 1
		
    db.commit()
    db.close()


if __name__ == "__main__":
    try:
        db = sql.connect("final.db")
        cursor = db.cursor()
        cursor.execute(table)
        main(cursor, db)
        print()
    except KeyboardInterrupt:
        db.commit()
        db.close()
        print()
