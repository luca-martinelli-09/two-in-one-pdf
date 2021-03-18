# Two in One PDF

This tool let you to create a PDF with two pages in one page.

## Usage

### Python

``` bash
python3 two-in-one-pdf.py -i filename [-o outputfile] [-c configfile]
```

### Compiled file (avaiable in releases)

``` bash
two-in-one-pdf -i filename [-o outputfile] [-c configfile]
```

If no output file name given, it will be user input file name with "_merged" appended.

## Configs

You can change [default.ini](default.ini) file. The default configuration is:

``` ini
[GLOBAL]

scale_page = 0.5 # how much pages are scaled
margin_x = 120 # margin on x axis
margin_y = 120 # margin on y axis
margin_inter = 80 # margin on y axis between the pages
border = yes # print a border around pages
```

## Requirements for Python

These packages are required for correct functionality (avaiable also in [requirements.txt](requirements.txt)):

- PyPDF2
- fpdf
- progressbar

You can install all these dependences with

``` bash
pip3 install PyPDF2 fpdf progressbar
```