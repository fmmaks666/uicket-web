import sqlite3 as sql
from flask import (
    Blueprint,
    make_response,
    jsonify,
    g,
    request,
    Flask,
)  # I should remove "Flask"
from json import load, dump

# from tools.translate import Translation
from pathlib import Path
from os import environ, path, makedirs
from HdRezkaApi import HdRezkaApi, HdRezkaStream
from shutil import rmtree
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, OrGroup

# # to access ids, . for classes
# > for screen's widget (CSS)

PATH = path.dirname(__file__)


class Database:
    def __init__(self):
        self._db = None
        self._cursor = None
        self.get_many_query = """SELECT * FROM releases WHERE id IN({})"""  # {} for formaatting. Should be formatted to ?, ?,...

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


# class SeasonPopup():

# def __init__(self, seasons: dict, release: HdRezkaApi):
# self.seasons = seasons
# self.release = release
# self.season_ids = tuple(self.seasons["seasons"].keys())
# super().__init__()


# def compose(self):
# with RadioSet(id="season"):
# for k in self.seasons["seasons"].values():
# yield RadioButton(k, value=True)

# # Can I get that #season in this part of code?
# episodes = tuple((v, k) for k, v in self.seasons["episodes"][self.season_ids[0]].items())
# yield Select(episodes, id="episode", value=tuple(self.seasons["episodes"][self.season_ids[0]].keys())[0], allow_blank=False)
# yield Button(self.app.s("next"), id="next")
# yield Button(self.app.s("back"), id="back")


# def update_episodes(self):
# select = self.query_one("#episode")
# episodes = tuple((v, k) for k, v in self.seasons["episodes"][self.season_ids[event.radio_set.pressed_index]].items())
# select.set_options(episodes)


# @on(Button.Pressed, "#next")
# def select_quality(self):
# season = int(self.season_ids[self.query_one("#season").pressed_index])
# episode = int(self.query_one("#episode").value)
# translator_id = self.seasons["translator_id"]
# streams = self.release.getStream(season, episode, translation=translator_id)
# self.app.push_screen(QualityPopup(streams))


# class QualityPopup(ModalScreen):

# def __init__(self, streams: HdRezkaStream):
# self.streams = streams.videos
# super().__init__()


# def compose(self) -> ComposeResult:
# with RadioSet(id="quality"):
# for k, v in self.streams.items():
# yield RadioButton(k, value=v)

# yield Button(self.app.s("go"), id="open_stream")
# yield Button(self.app.s("back"), id="back")


# @on(Button.Pressed, "#open_stream")
# def go(self):
# quality = self.query_one("#quality").pressed_index
# stream_link = tuple(self.streams.values())[quality]
# self.app.user_config.open_link(stream_link)

# @on(Button.Pressed, "#back")
# def back(self):
# self.app.pop_screen()


class Search:
    def __init__(self):
        self.schema = Schema(
            id=ID(stored=True, unique=True),
            name=TEXT(stored=True),
            url=TEXT(stored=True),
        )
        self.index = None
        self.path = path.join(PATH, "index")

    def search(self, query) -> list[tuple[int, str, str], ...]:
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

    # def search(self):
    # query = self.query_one("#query").value
    # results = self.search.search(query)
    # self.push_screen(ReleasesList(results))

    # def dev_search(self):
    # query = self.query_one("#query").value
    # script = f"SELECT * FROM releases WHERE name LIKE '%{query}%'"
    # results = self.db._cursor.execute(script).fetchall()
    # self.push_screen(ReleasesList(results))

    def is_favorite(self, release_id: int) -> bool:
        if release_id in self.user_config.favorites:
            return True

        return False

    def toggle_favorite(self, release_id: int) -> bool:
        """
        Returns True when added to favorites, False whem Removed
        """
        if not release_id in self.user_config.favorites:
            self.user_config.add_favorite(release_id)
            return True
        else:
            self.user_config.remove_favorite(release_id)
            return False


def get_db():
    if "db" not in g:
        db = Database()
        db.create_connection("../data/test.db")
        g.db = db
    return g.db


api = Blueprint("api", __name__)
api = Flask(__name__)
db = Database()
db.create_connection("../data/test.db")


def validate(url):
    if url.startswith("https://rezka.ag") and url.endswith(".html"):
        return True
    else:
        return False


def favorite():
    self.app.toggle_favorite(self.release_id)
    event.button.label = (
        self.app.s("remove")
        if self.app.is_favorite(self.release_id)
        else self.app.s("add")
    )


@api.route("/<int:id>", methods=["GET"])
def get_translations(id):
    result = get_db().get_one(id)
    code = 200
    if not result:
        result = None
        code = 404
        return False

    def toggle_favorite(self, release_id: int) -> bool:
        """
        Returns True when added to favorites, False whem Removed
        """
        if not release_id in self.user_config.favorites:
            self.user_config.add_favorite(release_id)
            return True
        else:
            self.user_config.remove_favorite(release_id)
            return False


def get_db():
    if "db" not in g:
        db = Database()
        db.create_connection("../data/test.db")
        g.db = db
    return g.db


api = Blueprint("api", __name__)
api = Flask(__name__)
db = Database()
db.create_connection("../data/test.db")


def validate(url):
    if url.startswith("https://rezka.ag") and url.endswith(".html"):
        return True
    else:
        return False


def favorite():
    self.app.toggle_favorite(self.release_id)
    event.button.label = (
        self.app.s("remove")
        if self.app.is_favorite(self.release_id)
        else self.app.s("add")
    )


@api.route("/<int:id>", methods=["GET"])
def get_translations(id):
    result = get_db().get_one(id)
    code = 200
    if not result:
        body = {"error": "Not found"}
        code = 404
    else:
        result = result[0]
        release = HdRezkaApi(result[2])
        translations = release.getTranslations()
        body = {
            "id": result[0],
            "name": result[1],
            "link": result[2],
            "translations": translations,
        }
    response = make_response(jsonify(body))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.status_code = code
    return response


@api.route("/episodes/<int:id>")
def get_episodes(id):
    result = get_db().get_one(id)
    if not result:
        body = {"error": "Not found"}
        code = 404
    else:
        result = result[0]
        release = HdRezkaApi(result[2])
        translation = request.args.get("translation", type=str)
        if release.type == "video.movie":
            streams = release.getStream(translation=translation).videos
            body = {"type": "streams", "streams": streams}
        else:
            seasons = release.getSeasons() 
            body = {"type": release.type, "seasons": seasons}
        code = 200
    response = make_response(body)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.status_code = code
    return response


if __name__ == "__main__":
    api.run(debug=True)
