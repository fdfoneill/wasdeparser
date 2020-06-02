## set up logging
import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import re, xlrd
import pandas as pd
from datetime import datetime



class Parser:
	"""A class to read and parse WASDE report files
	
	***

	Attributes
	----------
	source_file
	data
	season

	Methods
	-------
	parse -> None
	parsetext -> dict
	parsexl -> dict
	isPageHeader -> bool
		Returns whether a line string
		matches page header syntax
	getHeaderRow_xl -> int
		Returns row id of first row where
		>50% of columns have values
	"""


	def __init__(self):
		self.source_file = None
		self.data = None
		self.date = None
		self.season = None


	def __repr__(self):
		return "<Instance of wasdeparser.parser.Parser>"


	def parse(self,input_file,file_format="TEXT") -> None:
		
		self.source_file = input_file
		try:
			if file_format == "TEXT":
				self.data = self.parsetext(input_file)
			elif file_format == "EXCEL":
				self.data = self.parsexl(input_file)
			else:
				log.error("Argument 'file_format' must be one of: ['TEXT','EXCEL']")
				self.source_file = None
		except:
			log.exception("Failed to parse")
			self.source_file = None
			self.data = None


	def parsetext(self,input_file) -> dict:
		"""Parser for text files, returns parsed dict"""
		log.warning("Parsing for text files not implemented")
		return None

		# read file
		with open(input_file,'r') as rf:
			lines = [l.strip("\n") for l in rf.readlines()]

		# split into pages
		pages = {} # dictionary of lists
		lineIndex = 0
		## skip beginning of file
		try:
			while not self.isPageHeader_txt(lines[lineIndex]):
				lineIndex += 1
		except IndexError:
			log.error(f"No page header matches. Index = {lineIndex}")
		## add pages to dict
		while lineIndex < len(lines):
			pageNumber = [p.strip().split()[0] for p in lines[lineIndex].strip().split("-")][2]
			log.info(pageNumber)
			lineIndex += 1
			pageData = []
			while lineIndex < len(lines):
				if self.isPageHeader_txt(lines[lineIndex]):
					break
				pageData.append(lines[lineIndex])
				lineIndex+= 1
			pages[pageNumber] = pageData

		# parse each page
		return pages


	def parsexl(self,input_file) -> dict:
		"""Parser for excel files, returns parsed dict"""
		try:
			wrkbk = xlrd.open_workbook(input_file)
		except:
			log.error(f"Failed to open {input_file} as excel workbook")
			return None
		out_data = {}

		# PAGE 19 #
		out_data["Wheat"] = self.parsePage_xl(wrkbk,"Page 19","Wheat")

		# PAGE 23 #
		out_data["Corn"] = self.parsePage_xl(wrkbk,"Page 23","Corn")

		return out_data


	def parsePage_xl(self,wrkbk,page_name,page_crop) -> pd.DataFrame:
		sheet = wrkbk.sheet_by_name(page_name)
		header_row = self.getHeaderRow_xl(sheet)
		label_column = self.getStartColumn_xl(sheet)
		date_raw = sheet.cell(0,0).value.strip()
		self.date = datetime.strptime(date_raw,"%B %Y").strftime("%m/%d/%Y")
		self.season = sheet.cell(header_row,label_column).value.strip().split()[0]
		start_column = label_column+2
		rownames = {} # dictionary of rowname:row
		colnames = {} # dictionary of colname:col
		for y in range(header_row+1,sheet.nrows-1):
			contents = sheet.cell(y,label_column).value
			if contents != "" and contents.strip() != "Selected Other":
				rownames[contents.strip()] = y+1
		for x in range(start_column,sheet.ncols):
			contents = sheet.cell(header_row,x).value.strip().replace("\n"," ")
			if contents != "":
				colnames[contents] = x
		## extract data
		page_headers = ["Crop","Category"] + [self.cleanSlashes(region) for region in rownames.keys()]
		page_data = []
		for variable in colnames.keys():
			line = [page_crop,self.cleanSlashes(variable)]
			for region in rownames.keys():
				x = colnames[variable]
				y = rownames[region]
				line.append(sheet.cell(y,x).value)
			page_data.append(line)
		return pd.DataFrame(page_data,columns=page_headers,index=[i for i in range(len(page_data))])


	def isPageHeader_txt(self,line) -> bool:
		"""Tests whether line matches page header syntax
		Returns True if line is of the form 'WASDE-*-#',
		else false.
		"""
		try:
			parts = [p.strip().split()[0] for p in line.strip().split("-")] # get just ["WASDE","<<report no>>","<<page no>>"]
			if parts[0] != "WASDE":
				return False
			if len(parts) != 3:
				return False
			assert int(parts[1])
			assert int(parts[2])
			return True
		except:
			return False


	def getHeaderRow_xl(self,sheet) -> int:
		"""Returns id of first row where >50% of columns have values"""
		for y in range(sheet.nrows):
			full = 0
			for x in range(sheet.ncols):
				if sheet.cell(y,x).value != "":
						 full += 1
				pc = (float(full)/float(sheet.ncols))*100
				if pc >= 50:
					return y
		log.error("Failed to find header row")
		return -1


	def getStartColumn_xl(self,sheet) -> int:
		for x in range(sheet.ncols):
			for y in range(sheet.nrows):
				if sheet.cell(y,x).value.strip().split(" ")[0] == "World":
					return x
		log.error("Failed to find start column")
		return -1


	def cleanSlashes(self,in_string) -> str:
		"""removes weird '1/, 2/ 3/' from the ends of strings"""
		in_string = in_string.strip()
		for i in range(1,10):
			in_string = in_string.strip(f"{i}/").strip()
		return in_string