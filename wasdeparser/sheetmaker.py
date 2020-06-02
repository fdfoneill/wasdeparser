## set up logging
import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

from .parser import Parser

import xlsxwriter



class Sheetmaker:
	"""A class for outputting a well-formatted excel sheet

	***

	Attributes
	----------
	crop_regions
	categories
	data

	Methods
	-------
	read
	write

	"""


	def __init__(self):

		self.crop_regions = {
			"Corn":[
				"World",
				"United States"
			],
			"Wheat":[
				"World",
				"United States",
				"Russia"
			]
		}

		self.categories = [
			"Production",
			"Consumption",
			"Exports",
			"Ending Stocks"
		]

		self.data = {}
		for crop in self.crop_regions.keys():
			self.data[crop] = []


	def __repr__(self):
		return "<Instance of wasdeparser.sheetmaker.Sheetmaker>"


	def read(self,file_path):
		"""Ingest and parse a WASDE data file

		***

		Parameters
		----------
		file_path:str
			FUll path to data file on disk
		"""

		parser = Parser()

		
		name,ext = os.path.splitext(file_path)
		# # get date from filename
		# junk, month, day, year = name.split("-")
		# date = f"{month}/{day}/{year}"

		# case based on filetype
		if ext in ['.xls','.xlsx']:
			parser.parse(file_path,"EXCEL")
		elif ext == ".txt":
			parser.parse(file_path,"TEXT")

		# absorb data
		for crop in parser.data.keys():
			self.data[crop].append({"date":parser.date,"season":parser.season,"data":parser.data[crop]})


	def write(self,out_file,file_format="EXCEL")->str:
		"""Writes stored data to excel file

		***

		Parameters
		----------
		out_file:str
			Path where output will write on disk
		file_format:str
			One of ["EXCEL","CSV"]
		"""
		if file_format == "EXCEL":
			wrkbk = xlsxwriter.Workbook(out_file)
			for crop in self.crop_regions.keys():
				wrkbk.add_worksheet(crop)
				sheet = wrkbk.get_worksheet_by_name(crop)
				# define and write headers
				headers = ["Date","Season","Crop","Category"]+self.crop_regions[crop]
				for i in range(len(headers)):
					sheet.write(0,i,headers[i])
				# write actual data
				row = 0
				for report in self.data[crop]:
					for i in report['data'].index:
						row = row+1
						sheet.write(row,0,report['date'])
						sheet.write(row,1,report['season'])
						sheet.write(row,2,crop)
						sheet.write(row,3,report['data']['Category'][i])
						col = 4
						for region in self.crop_regions[crop]:
							sheet.write(row,col,report['data'][region][i])
							col+= 1
			wrkbk.close()

		elif file_format == "CSV":
			log.warning("CSV output not implemented")

		else:
			log.error(f"'{file_format}' not recognized as valid output file format")

		return out_file