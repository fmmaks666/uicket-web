from json import load as _load
from json.decoder import JSONDecodeError
import logging


class Translation:
	
	def __init__(self) -> None:
		self.language: str = None
		self.strings: dict = None
		

	def load_translation(self, language: str, file_name: str) ->  bool:
		"""
		Loads translation from JSON file
		:param language: (string) Key name of translation in JSON
		:param file_name: (string) File name
		:return: (bool) Returns True on success, False on Failure
		"""
		try:
			with open(file_name) as out:
				output = _load(out)
				self.language = language
				self.strings = output[language]
				logging.debug(f"Language: {self.language}, self.strings: {self.strings}, output was: {output}")
				return True
				
		except FileNotFoundError:
			logging.error("File not found")
			return False
		except JSONDecodeError:
			logging.error("JSON decoding failed")
			return False
		except KeyError:
			logging.error(f"Can't find key '{language}' in {file_name}, make sure that translations stored in JSON object")
			return False

	def get_string(self, string: str) -> str:
		"""
		Get translated string with id
		:param string: (string) ID oc string
		:return: (string) Traslated string. Returns string even if result was not string!
		"""
		logging.info(f"Requested string with id {string}")
		if self.strings is None:
			logging.warning("Translations are not initalized")
			return "not initialized"
		
		try:
			result = self.strings[string]
			logging.info(f"Received string: {result} with string id {string}")
			if not isinstance(result, str):
				logging.warning("Received translation is not string, converting to string")
				return str(result)
			return result
				
		except KeyError:
			logging.warning(f"'{string}' not found")
			return "not found"
			
