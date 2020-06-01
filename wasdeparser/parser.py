import re, xlrd

class Parser:
	"""A class to read and parse WASDE report files
	
	***

	Attributes
	----------
	data

	Methods
	-------
	parse -> None

	"""

	def __init__(self):
		pass

	def parse(self,input_file,format="TEXT") -> None:
		# loop over lines until you reach "   WSDE-*-19"
		## CODE: line.strip().split()[0].split("-")[2] == "19"
		pass