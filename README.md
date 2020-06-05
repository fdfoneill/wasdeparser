# wasdeparser

`wasdeparser` is a Python package that facilitates access to and use of data from the [USDA](https://www.usda.gov/) World Agricultural Supply and Demand Estimates.

# Motivation

The USDA makes their data [freely available online](https://usda.library.cornell.edu/concern/publications/3t945q76s?locale=en&page=13#release-items), but the format in which those data are promulgated does not lend itself to easy between-year analysis or multi-year display. This package is intended to streamline the acquisition and 'cleaning' of multiple years' worth of data, outputting them in a format more suitable for analysis and display. 

# Features

* Download and clean multiple years of WASDE data with a single line of code
* Choose which variables to extract (coming soon!)
* Create analysis-ready Excel files

# Code Example

```
# command line
wasdeparse C:/temp/output_file.xlsx -d C:/input_data_files
```

# How to Use

The main interface with the `wasdeparser` module is through the `wasdeparse` command-line script. This script takes two arguments: a filepath for the output excel file, and the path to a directory of WASDE files (excel or text) downloaded from the [Cornell portal](https://usda.library.cornell.edu/concern/publications/3t945q76s?locale=en&page=13#release-items).

The script reads and parses each file in the input directory, extracting certain variables. By default, those variables are:

* Production
* Domestic Total
* Ending Stocks

for wheat and corn. Wheat statistics are generated for the world, United States, and Russia, while corn statistics are generated for the world and United States. Future releases of `wasdeparser` will allow the user to specify custom crops, variables, and regions to include in the output file.

# License
MIT License

Copyright (c) 2020 F. Dan O'Neill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.