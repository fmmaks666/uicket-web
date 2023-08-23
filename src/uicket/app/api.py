import sqlite3 as sql
from flask import (
    Blueprint,
    make_response,
    jsonify,
    g,
    request,
)
from json import load, dump, loads, dumps
from uicket.tools import Search, Database
# from tools.translate import Translation
from pathlib import Path
from os import environ, path, makedirs
from HdRezkaApi import HdRezkaApi, HdRezkaStream
from shutil import rmtree
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, OrGroup

PATH = path.dirname(__file__) # This sucks too
__version__ = "Unstable/Development"
# class Database:
    # def __init__(self):
        # self._db = None
        # self._cursor = None
        # self.get_many_query = """SELECT * FROM releases WHERE id IN({})"""  # {} for formaatting. Should be formatted to ?, ?,...

    # def create_connection(self, path: str) -> None:
        # self._db = sql.connect(path)
        # self._cursor = self._db.cursor()
        # self._cursor.execute(
            # "CREATE TABLE IF NOT EXISTS releases(id INTEGER PRIMARY KEY, name TEXT, url TEXT)"
        # )

    # def close(self):
        # if self._db is not None:
            # self._db.close()

    # def get_one(self, release_id: int) -> tuple[tuple[int, str, str], ...] | None:
        # if self._cursor is None:
            # return
        # return self._cursor.execute(
            # "SELECT * FROM releases WHERE id=?", (str(release_id),)
        # ).fetchall()

    # def get_many(
        # self, values: tuple[int] | list[int]
    # ) -> tuple[tuple[int, str, str], ...]:
        # if self._cursor is None:
            # return
        # amount = ", ".join(["?"] * len(values))
        # return self._cursor.execute(
            # self.get_many_query.format(amount), values
        # ).fetchall()

    # def get_all(self, no_fetch=False):
        # if self._cursor is None:
            # return None

        # data = self._cursor.execute("SELECT * FROM releases")

        # if not no_fetch:
            # data.fetchall()

        # return data


# class Search:
    # def __init__(self):
        # self.schema = Schema(
            # id=ID(stored=True, unique=True),
            # name=TEXT(stored=True),
            # url=TEXT(stored=True),
        # )
        # self.index = None
        # self.path = path.join(PATH, "index")
        # self.path = "/data/data/com.termux/files/home/uicket-web/src/uicket/data/index"  # Hard coding sucks!~

    # def search(self, query) -> list[tuple[int, str, str], ...] | None:
        # if self.index is None:
            # return
        # with self.index.searcher() as searcher:
            # parser = QueryParser("name", self.index.schema, group=OrGroup)
            # parsed = parser.parse(query)
            # output = searcher.search(parsed)
            # results = []
            # for i in output:
                # results.append(((int(i["id"])), i["name"], i["url"]))

            # return results

    # def load(self):
        # if exists_in(self.path) and self.index is None:
            # self.index = open_dir(self.path)

    # def create(self, db: Database):
        # if Path(self.path).exists():
            # rmtree(self.path, ignore_errors=True)

        # makedirs(self.path)
        # self.index = create_in(self.path, self.schema)
        # data = db.get_all(True)
        # if data is None:
            # return

        # with self.index.writer() as writer:
            # for release_id, name, url in data:
                # writer.add_document(id=str(release_id), name=name, url=url)


api = Blueprint("api", __name__)


def get_db():
    if "db" not in g:
        db = Database()
        db.create_connection()
        g.db = db
    return g.db


def get_search():
    if "search" not in g:
        search = Search()
        search.load()
        g.search = search
    return g.search


def generate_response(body, code):
    response = make_response(jsonify(body))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    response.status_code = code
    return response


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
        if None in translations:
            value = translations.pop(None)
            translations[value] = value
        body = {
            "id": result[0],
            "name": result[1],
            "link": result[2],
            "type": release.type,
            "translations": translations,
        }

    return generate_response(body, code)


@api.route("/episodes/<int:id>", methods=["GET"])
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
    return generate_response(body, code)


@api.route("/streams/<int:id>", methods=["GET"])
def get_streams(id):
    result = get_db().get_one(id)
    if not result:
        body = {"error": "Not found"}
        code = 404
        return generate_response(body, code)
    else:
        # I need to use & when using many args, not ,s
        season = request.args.get("season", type=int)
        episode = request.args.get("episode", type=int)
        translation = request.args.get("translation", type=str)
        if not (season is not None and episode is not None):
            return generate_response(
                {
                    "error": "Too few arguments, Required args: season: int, episode: int"
                },
                400,
            )
        result = result[0]
        release = HdRezkaApi(result[2])
        try:
            streams = release.getStream(season, episode, translation=translation)
            body = {"type": "streams", "streams": streams.videos}
        except TypeError:
            return generate_response({"error": "Season/Episode not found"}, 400)
        except ValueError:
            return generate_response(
                {"error": f"Translation with ID {translation} doesn't exists'"}, 400
            )
        return generate_response(body, 200)


@api.route("/search", methods=["GET"])
def search_releases():
    query = request.args.get("q", type=str)
    if query is None:
        return generate_response(
            {"error": "Too few arguments, Required args: q: str"}, 400
        )
    results = get_search().search(query)
    code = 200
    body = {"type": "releases", "results": results}
    if not results:
        code = 204  # 204 == No content
        body = None
    return generate_response(body, code)


@api.route("/favorites", methods=["GET"])
def get_favorites():
    favorites = request.cookies.get("Favorites")
    if favorites is None:
        return generate_response({"error": "Favorites aren't created"}, 404)
    response = generate_response({"favorites": loads(favorites)}, 200)
    return response


@api.route("/favorites/<int:id>", methods=["POST"])
def add_favorite(id):
    favorites = request.cookies.get("Favorites")
    if favorites is None:
        return generate_response({"error": "Favorites aren't created"}, 404)
    favorites = set(loads(favorites))
    favorites.add(id)
    response = generate_response({"success": id in favorites}, 200)
    response.set_cookie("Favorites", dumps(list(favorites)))
    return response


@api.route("/favorites/<int:id>", methods=["DELETE"])
def remove_favorite(id):
    favorites = request.cookies.get("Favorites")
    if favorites is None:
        return generate_response({"error": "Favorites aren't created"}, 404)
    favorites = set(loads(favorites))
    favorites.discard(id)
    response = generate_response({"success": id not in favorites}, 200)
    response.set_cookie("Favorites", dumps(list(favorites)))
    return response


@api.route("/version", methods=["GET"])
def version():
	return generate_response({"version": __version__, "text": "Uicket Web API/Development"}, 200)
