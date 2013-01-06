This script scrapes grades from Infinite Campus and stores them in a data file.

INSTALL
=======
* Remove the underscores from _config.py and _data.csv
* Fill in the required fields in config.py
* Install the "mechanize" and "BeautifulSoup" python modules

Caveats
=======
* Currently only works for schedules with 4 classes per term
* May not work with all version of Inifinite Campus

Usage: scraper.py [options]

Options:
  -h, --help   show this help message and exit
  -p, --print  prints the grade report to stdout
  -e, --email  email the grade report to user
