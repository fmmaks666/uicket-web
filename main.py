# fmmaks, You should make better structure for Uicket!!!!!!!!!!!!!
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Input, RadioButton, Label, RadioSet, Static, Select
from textual.containers import Horizontal, Vertical, Grid, VerticalScroll
from textual.screen import Screen, ModalScreen
import sqlite3 as sql
from json import load, dump
from translate import Translation
from dataclasses import dataclass
from pathlib import Path
from os import environ, path, makedirs
from platform import platform
from webbrowser import open as web_open
from subprocess import run
from HdRezkaApi import HdRezkaApi, HdRezkaStream
from shutil import rmtree
from whoosh.index import create_in, open_dir, exists_in
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, OrGroup
# # to access ids, . for classes
# > for screen's widget (CSS)

PATH = path.dirname(__file__)

class UserSettings:
	def __init__(self):
		with open(path.join(PATH, "config.json"), encoding="UTF-8") as out:
			data = load(out)
			self.language: str = data["language"]
			self.db: str = data["db"]
			self.favorites: list[int] = data["favorites"]
		
		self.open_link = self._default_open
		if "Linux" in platform():
			if "ANDROID_ROOT" in environ:
				self.open_link = self._termux_open
		
	
	def change_language(self, language="en"): 
	
		self.language = language
	
		values = {
			"language": language,
			"db": self.db,
			"favorites": self.favorites
		}
		
		self.write(values)
			
	
	def update_db(self, db = None): 
		self.db = db
	
		values = {
			"language": self.language,
			"db": db,
			"favorites": self.favorites
		}
		
		self.write(values)
	
	
	def add_favorite(self, release_id: int) -> None:
		self.favorites.append(release_id)
		
		values = {
			"language": self.language,
			"db": self.db,
			"favorites": self.favorites
		}
		
		self.write(values)
	
	
	def remove_favorite(self, release_id: int) -> None:
		self.favorites.remove(release_id)
		
		values = {
			"language": self.language,
			"db": self.db,
			"favorites": self.favorites
		}
		
		self.write(values)
	
	
	def write(self, values: dict):
		with open(path.join(PATH, "config.json"), encoding="UTF-8", mode="w+") as out:
			dump(values, out)
		
		
	def _default_open(self, link: str):
		return web_open(link)
		
		
	def _termux_open(self, link: str):
		return run(["termux-open", link])


class Release(Static):
	
	
	def __init__(self, release_id, release_name, url):
		self.release_id = release_id
		self.release_name = release_name
		self.url = url
		super().__init__()
	
	
	def compose(self) -> ComposeResult:
		yield Label(f"[b]{self.release_name}[/]")
		yield Button(self.app.s("watch"), id="watch")
		
		
	@on(Button.Pressed, "#watch")
	def watch(self):
		self.app.push_screen(ReleasePage(self.release_id, self.release_name, self.url), self.exited_with_error)


	def exited_with_error(self, value):
		if not value:
			button = self.query_one("#watch")
			button.disabled = True
			button.label = self.app.s("not_found")

	
class ReleasesList(Screen):
	
	def __init__(self, releases: list[tuple[int, str, str], ...] = None):
		self.releases = releases
		super().__init__()
		
		
	def compose(self) -> ComposeResult:
		with VerticalScroll():
			if self.releases:
				for i in self.releases:
					release_id, name, url = i
					yield Release(release_id, name, url) 
			else:
				yield Label(self.app.s("no_result"))
		
		yield Button(self.app.s("back"), id="back")


	@on(Button.Pressed, "#back")
	def back(self):
		self.app.pop_screen()
		
		

class ReleasePage(Screen[bool]):
	
	def __init__(self, release_id, release_name, url): # These args are temporary
		self.release_id = release_id
		self.release_name = release_name
		self.url = url
		super().__init__()
	
	def compose(self) -> ComposeResult:
		# I should put everything to VerticalScroll()...
		unwatchable = True
		if not self.validate():
			self.dismiss(False)
			
		yield Label(self.release_name)
		self.release = HdRezkaApi(self.url)
		self.type = self.release.getType()
		translations = self.release.getTranslations()
		self.ids = tuple(translations.values())
		with RadioSet(id="selected_translation"):
			for k in translations.keys():
				yield RadioButton(k, value=True)
				
		unwatchable = False
	
		yield Button(self.app.s("watch"), id="watch", disabled=unwatchable)
		yield Button(self.app.s("remove") if self.app.is_favorite(self.release_id) else self.app.s("add"), id="favorites_button")
		yield Button(self.app.s("back"), id="back")


	def validate(self):
		if (self.url.startswith("https://rezka.ag") and self.url.endswith(".html")):
			return True
		else:
			return False
			
	
	@on(Button.Pressed, "#watch")
	def watch(self):
		radio = self.query_one("#selected_translation")
		translation_id = self.ids[radio.pressed_index]
		if self.type == "video.movie":
			streams = self.release.getStream(translation=translation_id)
			self.app.push_screen(QualityPopup(streams))
		else:
			seasons = self.release.getSeasons()
			translation_name = str(radio.pressed_button.label)
			self.app.push_screen(SeasonPopup(seasons[translation_name], self.release))
			
			
	@on(Button.Pressed, "#favorites_button")
	def favorite(self, event: Button.Pressed):
		self.app.toggle_favorite(self.release_id)
		event.button.label = self.app.s("remove") if self.app.is_favorite(self.release_id) else self.app.s("add")
			
	@on(Button.Pressed, "#back")
	def back(self):
		self.app.pop_screen()


class SeasonPopup(ModalScreen):

	def __init__(self, seasons: dict, release: HdRezkaApi):
		self.seasons = seasons
		self.release = release
		self.season_ids = tuple(self.seasons["seasons"].keys())
		super().__init__()

		
	def compose(self) -> ComposeResult:
		with RadioSet(id="season"):
			for k in self.seasons["seasons"].values():
				yield RadioButton(k, value=True)
		
		# Can I get that #season in this part of code?
		episodes = tuple((v, k) for k, v in self.seasons["episodes"][self.season_ids[0]].items())
		yield Select(episodes, id="episode", value=tuple(self.seasons["episodes"][self.season_ids[0]].keys())[0], allow_blank=False)
		yield Button(self.app.s("next"), id="next")
		yield Button(self.app.s("back"), id="back")


	@on(RadioSet.Changed, "#season")
	def update_episodes(self, event: RadioSet.Changed):
		select = self.query_one("#episode")
		episodes = tuple((v, k) for k, v in self.seasons["episodes"][self.season_ids[event.radio_set.pressed_index]].items())
		select.set_options(episodes)


	@on(Button.Pressed, "#next")
	def select_quality(self):
		season = int(self.season_ids[self.query_one("#season").pressed_index])
		episode = int(self.query_one("#episode").value)
		translator_id = self.seasons["translator_id"]
		streams = self.release.getStream(season, episode, translation=translator_id)
		self.app.push_screen(QualityPopup(streams))


	@on(Button.Pressed, "#back")
	def back(self):
		self.app.pop_screen()


class QualityPopup(ModalScreen):
	
	def __init__(self, streams: HdRezkaStream):
		self.streams = streams.videos
		super().__init__()
		
	
	def compose(self) -> ComposeResult:
		with RadioSet(id="quality"):
			for k, v in self.streams.items():
				yield RadioButton(k, value=v)
				
		yield Button(self.app.s("go"), id="open_stream")
		yield Button(self.app.s("back"), id="back")
			
	
	@on(Button.Pressed, "#open_stream")
	def go(self):
			quality = self.query_one("#quality").pressed_index
			stream_link = tuple(self.streams.values())[quality]
			self.app.user_config.open_link(stream_link)

	@on(Button.Pressed, "#back")
	def back(self):
		self.app.pop_screen()


class Database:
	
	def __init__(self):
		self._db = None
		self._cursor = None
		self.get_many_query = """SELECT * FROM releases WHERE id IN({})""" # {} for formaatting. Should be formatted to ?, ?,...
	
	
	def create_connection(self, path: str) -> None:
		self._db = sql.connect(path)
		self._cursor = self._db.cursor()
		self._cursor.execute("CREATE TABLE IF NOT EXISTS releases(id INTEGER PRIMARY KEY, name TEXT, url TEXT)")
	

	def close(self):
		if self._db is not None:
			self._db.close()


	def get_many(self, values: tuple[int] | list[int]) -> tuple[tuple[int, str, str], ...]:
		if self._cursor is None:
			return
		amount = ", ".join(["?"] * len(values))
		return self._cursor.execute(self.get_many_query.format(amount), values).fetchall()
		
	
	def get_all(self, no_fetch=False):
		if self._cursor is None:
			return None

		data = self._cursor.execute("SELECT * FROM releases")

		if not no_fetch:
			data.fetchall()

		return data

class Search:

	def __init__(self):
		self.schema = Schema(id=ID(stored=True, unique=True), name=TEXT(stored=True), url=TEXT(stored=True))
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


class LanguageSwitcher(ModalScreen):
	
	def compose(self) -> ComposeResult:
			yield Select((("English", "en"), ("Українська", "ua")), allow_blank=False, prompt=self.app.s("change"))
			yield Button(self.app.s("close"),id="close")


	@on(Select.Changed)
	def switch(self, event: Select.Changed):
		self.app.user_config.change_language(language=str(event.value))
		
	
	@on(Button.Pressed, "#close")
	def destroy(self):
		self.app.pop_screen()
	
	
class Config(ModalScreen):
	
	
	def compose(self) -> ComposeResult:
		with Horizontal(id = "config"):
			yield Input(placeholder=self.app.s("db_path"), id="path")
			yield Button(self.app.s("apply"), id="apply")
			yield Button(self.app.s("cancel"), id="cancel")
	
	
	@on(Button.Pressed, "#apply")		
	def apply(self):
		path = self.query_one("#path").value
		if Path(path).exists():
			self.app.db.create_connection(path)
			self.app.user_config.update_db(path)
			self.app.search.create(self.app.db)
			self.app.pop_screen()
	
	
	@on(Button.Pressed, "#cancel")		
	def cancel(self):
		self.app.pop_screen()
	
	
			
class Uicket(App):
	
	CSS_PATH = "uicket.css"

	def __init__(self, database: Database, translation: Translation, settings: UserSettings, search: Search):
		self.db = database
		self.t = translation
		self.s = self.t.get_string
		self.user_config = settings
		self.search = search
		if self.user_config.db is not None:
			if Path(self.user_config.db).exists():
				self.db.create_connection(self.user_config.db)
				self.search.load()
		self.translated = True
		if not self.t.load_translation(self.user_config.language, path.join(PATH, "translation.json")):
			self.translated = False
		super().__init__()


	BINDINGS = [("ctrl+c", "exit", "Quit Uicket"), ("d", "toggle_dark", "Switch Theme"), ("s", "setup", "Configure DB"), ("l", "settings", "Change Language")]



	def compose(self) -> ComposeResult:
		"""Creating UI"""
		yield Header()
		with Horizontal():
			yield Input(placeholder=self.s("enter_something"), id="query")
			yield Button(self.s("search"), id="search")
		yield Button(self.s("favorites"), id="favorites")
		yield Label("Created by fmmaks\nLicensed under GNU GPLv3", id="about")
		yield Footer()
		
	def on_mount(self):
		if not self.translated:
			self.panic("[blink]Uicket -- Fatal Error[/]\n Sorry we can't run Uicket~~\n Error: Can't load Uicket translations")
	
	def action_exit(self) -> None:
		self.db.close()
		self.exit()
		
	def action_toggle_dark(self) -> None:
		self.dark = not self.dark
		
	def action_settings(self) -> None:
		self.push_screen(LanguageSwitcher())
		
	def action_setup(self) -> None:
		self.push_screen(Config())
	
	
	@on(Button.Pressed, "#search")
	def search(self):
		query = self.query_one("#query").value
		results = self.search.search(query)
		self.push_screen(ReleasesList(results))
	
	
	# def dev_search(self):
		# query = self.query_one("#query").value
		# script = f"SELECT * FROM releases WHERE name LIKE '%{query}%'"
		# results = self.db._cursor.execute(script).fetchall()
		# self.push_screen(ReleasesList(results))

	
	
	@on(Button.Pressed, "#favorites")
	def open_favorites(self):
		favorites_data = self.db.get_many(self.user_config.favorites)
		self.push_screen(ReleasesList(favorites_data))
		
		
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
	
	
if __name__ == "__main__":
	if not Path(PATH, "config.json").exists():
		config = {
			"language": "en",
			"db": None,
			"favorites": []

		}
		with open(path.join(PATH, "config.json"), "w+", encoding="UTF-8") as out:
			dump(config, out)
			
	app = Uicket(Database(), Translation(), UserSettings(), Search())
	app.run()
