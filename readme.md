This script scrapes grades from Infinite Campus and stores them in a data file.

INSTALL
=======
* Remove the underscore from "_config.py" and fill in the required data
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
