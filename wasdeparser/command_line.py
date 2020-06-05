## set up logging
import logging, os
logging.basicConfig(level=os.environ.get("LOGLEVEL","INFO"))
log = logging.getLogger(__name__)

import argparse, glob
from .sheetmaker import Sheetmaker


def main():
	parser = argparse.ArgumentParser(description="Process WASDE data files and output a clean excel workbook")
	parser.add_argument("out_file",
		type=str,
		help="Path to output excel file")
	parser.add_argument('-d',
		"--input_directory",
		type=str,
		help="Directory of WASDE files")

	args = parser.parse_args()

	files = glob.glob(os.path.join(args.input_directory,"*"))
	maker = Sheetmaker()
	for f in files:
		log.debug(f"Reading file: {os.path.basename(f)}")
		try:
			maker.read(f)
		except:
			log.exception(f"Failed to read {f}")
	maker.write(args.out_file)