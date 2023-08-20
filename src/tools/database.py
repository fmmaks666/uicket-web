import sqlite3 as sql


class Database:
	
	
    def __init__(self):
        self._db = None
        self._cursor = None
        self.get_many_query = """SELECT * FROM releases WHERE id IN({})"""  # {} for formatting. Should be formatted to ?, ?,...


    def create_connection(self, path: str) -> None:
        self._db = sql.connect(path)
        self._cursor = self._db.cursor()
        self._cursor.execute(
            "CREATE TABLE IF NOT EXISTS releases(id INTEGER PRIMARY KEY, name TEXT, url TEXT)"
        )


    def close(self):
        if self._db is not None:
            self._db.close()

    def get_one(self, release_id: int) -> tuple[tuple[int, str, str], ...] | None:
        if self._cursor is None:
            return
        return self._cursor.execute(
            "SELECT * FROM releases WHERE id=?", (str(release_id),)
        ).fetchall()


    def get_many(
        self, values: tuple[int] | list[int]
    ) -> tuple[tuple[int, str, str], ...]:
        if self._cursor is None:
            return
        amount = ", ".join(["?"] * len(values))
        return self._cursor.execute(
            self.get_many_query.format(amount), values
        ).fetchall()


    def get_all(self, no_fetch=False):
        if self._cursor is None:
            return None

        data = self._cursor.execute("SELECT * FROM releases")

        if not no_fetch:
            data.fetchall()

        return data

