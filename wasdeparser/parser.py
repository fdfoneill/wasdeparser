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
			log.exception(f"Failed to parse {input_file}")
			self.source_file = None
			self.data = None


	### TEXT ###


	def parsetext(self,input_file) -> dict:
		"""Parser for text files, returns parsed dict"""

		# read file
		with open(input_file,'r') as rf:
			lines = [l.strip("\n") for l in rf.readlines()]

		try:
			junk,month,day,year = os.path.splitext(os.path.basename(input_file))[0].split()[0].split("_")[0].split("-")
			self.date = datetime.strptime(f"{month}-{day}-{year}","%m-%d-%Y").strftime("%m/%d/%Y")
		except: # new ones have it in the file itself
			try:
				date_raw = lines[0].split()[-2] + " " + lines[0].split()[-1]
				self.date = datetime.strptime(date_raw,"%B %Y").strftime("%m/%d/%Y")
			except:
				pass

		# split into pages
		pages = {} # dictionary of lists
		lineIndex = 0
		## skip beginning of file
		try:
			while not self.isPageHeader_txt(lines[lineIndex]):
				lineIndex += 1
		except IndexError:
			log.warning(f"No page header matches in {input_file}. Index = {lineIndex}")
		## add pages to dict
		while lineIndex < len(lines):
			pageNumber = [p.strip().split()[0] for p in lines[lineIndex].strip().split("-")][2]
			lineIndex += 1
			pageData = []
			while lineIndex < len(lines):
				if self.isPageHeader_txt(lines[lineIndex]):
					break
				pageData.append(lines[lineIndex])
				lineIndex+= 1
			pages[pageNumber] = pageData

		out_data = {}
		# find wheat and corn pages by title
		for pageNumber in pages.keys():
			pageTitle = self.getTitleLine_txt(pages[pageNumber])
			if pageTitle == None:
				continue
			if pageTitle.lower() == "world wheat supply and use" and self.hasProj_txt(pages[pageNumber]):
				out_data['Wheat'] = self.parsePage_txt(pages,pageNumber,'Wheat')
			elif pageTitle.lower() == "world corn supply and use" and self.hasProj_txt(pages[pageNumber]):
				out_data['Corn'] = self.parsePage_txt(pages,pageNumber,'Corn')

		# parse each page
		return out_data


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


	def getTitleLine_txt(self,page) -> str:
		"""given list of lines, returns titleline as string"""
		for line in page:
			if len(line.strip()) > 0:
				title_line = line.strip()
				break
		# clean title line of '1/ (cont.)'
		for i in range(len(title_line)):
			try:
				int(title_line[i])
				title_line = title_line[:i]
				return title_line.strip()
			except ValueError:
				continue


	def getDataHeaders_txt(self,page) -> list:
		"""Dummy function for now, just returns expected headers"""
		return ["Beginning stocks","Production","Imports","Domestic Feed","Domestic Total","Exports","Ending Stocks"]


	def parseDataLine_txt(self,line)->list:
		"""Returns list of data values in text file line"""
		if ":" in line:
			parts = line.split(":")[1].split()
		else:
			parts = line.split()
			parts = parts[1:]
		return [p.strip() for p in parts if p.strip() != ":"]


	def parsePage_txt(self,page_data,page_number,page_crop) -> pd.DataFrame:
		"""Turn list of page lines into a pandas dataframe"""
		page = page_data[page_number]
		y = 0
		colnames = self.getDataHeaders_txt(page)
		#colnames = {dataHeaders[i]:i for i in range(len(dataHeaders))}
		#ownames = {}
		rownames = []
		dashRows = 0
		# skip to just below second row of equals signs
		while dashRows < 2:
			if len(page[y].strip()) == 0:
				y += 1
				continue
			elif page[y][0] == '=':
				dashRows += 1
				y += 1
			else:
				y += 1
		# skip to first row name
		while True:
			line = page[y]
			if len(line.strip().strip(":").strip()) == 0:
				y += 1
				continue
			if not self.couldBeData(self.cleanSlashes(line)):
				break
			# if neither of those, probably the season row...
			line = line.strip().strip(":").strip().strip("Proj.").strip("(Projected)").strip()
			self.season = line

			y += 1
		# read data directly from the table (and get the row names as we go!)
		rawData = []
		while y < len(page):
			line = page[y]
			# skip blank lines
			if len(line.strip().strip(":").strip()) == 0:
				y+=1
				continue
			# skip the dreaded "Selected Other"
			if "Selected Other".lower() in line.lower():
				y += 1
				continue
			# break if you've reached the last line (which is all ======'s)
			if line[0] == "=":
				break
			# do stuff if it's a region name
			# if not self.couldBeData(self.cleanSlashes(line)): # it's a normal region name
			# 	if not self.couldBeData(self.cleanSlashes(page[y+2])):
			# 		y += 1
			# 	else:
			# 		y += 2
			# 	rownames.append(self.cleanSlashes(line))
			# 	continue
			# if len(line.split(":")) > 1 and len(line.split(":")[0].split()) > 1: #it's a stupid one-line regionname+data
			# 	rownames.append(self.cleanSlashes(line.split(":")[0][:-4].strip()))
			if self.hasRowName(line):
				rownames.append(self.cleanSlashes(self.cleanRowName(line)))
				if self.cleanSlashes(self.cleanRowName(line)).endswith('4'):
					print(line)
				if self.couldBeData(line): # it's a rowname+data line
					if self.hasRowName(page[y+1]): # check whether the next row has a rowname
						rawData.append(self.parseDataLine_txt(line)) # if it doesn't, add this row's data
					y += 1
				elif self.hasRowName(page[y+2]):
					y += 1
				else:
					y += 2
				continue

			rawData.append(self.parseDataLine_txt(line))
			y += 1
		## housekeeping
		# print(rownames)
		# print(colnames)
		# for row in rawData:
		# 	print(row)
		# reshape data into dataframe-friendliness
		page_headers = ["Crop","Category"] + [self.cleanSlashes(region) for region in rownames]
		page_data = []
		for x in range(len(colnames)):
			variable = self.cleanSlashes(colnames[x])
			line = [page_crop,variable]
			for y in range(len(rownames)):
				region = self.cleanSlashes(rownames[y])
				line.append(rawData[y][x])
			page_data.append(line)
		return pd.DataFrame(page_data,columns=page_headers,index=[i for i in range(len(page_data))])


	def hasProj_txt(self,page)->bool:
		"""returns whether any line contains string 'Proj'"""
		for line in page:
			if "Proj" in line:
				return True
		return False

	### EXCEL ###


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
		date_raw = sheet.cell(*self.getDateCell_xl(sheet)).value.strip()
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


	def getDateCell_xl(self,sheet) -> tuple:
		"""Returns first cell with data, hopefully containing report date"""
		for y in range(sheet.nrows):
			for x in range(sheet.ncols):
				if sheet.cell(y,x).value != "":
					return (y,x)


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


	### GENERAL ###


	def cleanSlashes(self,in_string) -> str:
		"""removes weird '1/, 2/ 3/' from the ends of strings"""
		in_string = in_string.strip().strip(":").strip()
		while in_string.endswith("/"):
			in_string = in_string[:-2].strip()
		return in_string

	def couldBeData(self,in_string) -> bool:
		"""returns whether a string has any numerical digits in it"""
		in_string = self.cleanSlashes(in_string)
		if len(in_string.strip()) == 0:
			return False
		digits= any(char.isdigit() for char in in_string)
		nas = "NA" in in_string
		return (digits or nas)

	def hasRowName(self,in_string) -> bool:
		in_string = self.cleanSlashes(in_string)
		if len(in_string.strip()) == 0:
			return False
		digits= any(char.isdigit() for char in in_string)
		nas = "NA" in in_string
		if digits or nas:
			parts = in_string.split(":")
			if len(parts) < 2:
				return False
			if len(parts[0].split()) < 2:
				return False
			return True
		return True

	def cleanRowName(self,in_string):
		digits= any(char.isdigit() for char in self.cleanSlashes(in_string))
		nas = "NA" in in_string
		if digits or nas:
			return self.cleanSlashes(in_string.split(":")[0][:-4].strip())
		return self.cleanSlashes(in_string.strip()).strip()