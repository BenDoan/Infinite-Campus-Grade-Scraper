This script scrapes grades from Infinite Campus and stores them in a data file.  It also has the option of emailing grades via smtp.

INSTALL
=======
* Rename "config-sample.ini" to "config.ini" and fill in the required fields
* Install the "mechanize" and "BeautifulSoup" python modules

Caveats
=======
* The script has only been tested on schedules with 5 classes and 4 semesters
* May not work with all versions of Inifinite Campus

Usage: scraper.py [options]

```
Options:
  -h, --help   show this help message and exit
  -p, --print  prints the grade report to stdout
  -e, --email  email the grade report to user
```
