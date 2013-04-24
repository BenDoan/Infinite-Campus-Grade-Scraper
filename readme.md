This script scrapes grades from Infinite Campus and stores them in a data file.  It also has the option of emailing grades via smtp.

INSTALL
=======
* Rename "config-sample.ini" to "config.ini" and fill in the required fields
* Install the "mechanize" and "BeautifulSoup" python modules

Caveats
=======
* The script has only been tested on schedules with 5 classes and 4 semesters
* May not work with all versions of Inifinite Campus

USAGE
=====
```
Usage: scraper.py [options]

A script to scrape grades from an infinite campus website

Options:
  -h, --help     show this help message and exit
  -p, --print    prints the grade report to stdout
  -e, --email    email the grade report to user
  -w, --weekly   diffs using the grades from a week ago
  -n, --no-log   does not log grades in grades database
  -v, --verbose  outputs more information
```

LICENSE
=======
```
Infinite Campus Grade Scraper - scrapes your grades from infinite campus and emails them to you.
Copyright (C) 2012 Ben Doan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
```
