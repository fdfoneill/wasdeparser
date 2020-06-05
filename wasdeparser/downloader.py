## set up logging
import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)


import requests

class Downloader:
	"""A class for downloading USDA WASDE data files

	***

	Attributes
	----------

	Methods
	-------

	"""

	def __init__(self):
		pass

	def __repr__(self):
		return "<Instance of wasdeparser.downloader.Downloader>"

	def pull(self,date:str,format="TEXT") -> str:
		"""Downloads a WASDE file

		***

		Parameters
		----------
		date:str
			Release date of desired file,
			formatted as "YYYY-MM-DD"
		format:str
			Desired file format. One of
			TEXT or EXCEL
		"""
		log.warning("Downloading not implemented")
		pass