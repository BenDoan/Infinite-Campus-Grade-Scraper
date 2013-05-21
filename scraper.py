#!/usr/bin/env python

import ConfigParser
import cookielib
import mechanize
import os
import string
import sys

from BeautifulSoup import BeautifulSoup
from datetime import date, timedelta, datetime
from optparse import OptionParser
from xml.dom import minidom

import utils

br = mechanize.Browser()
date = date.today()

APPDIR = os.path.dirname(sys.argv[0])
CONFIG_FILE_NAME = os.path.join(APPDIR, ".", "config.ini")

Config = ConfigParser.ConfigParser()
Config.read(CONFIG_FILE_NAME)

parser = OptionParser(description='Scrapes grades from an infinite campus website')
parser.add_option('-p', '--print', action='store_true', dest='print_results',
        help='prints the grade report to stdout')
parser.add_option('-e', '--email', action='store_true', dest='email',
        help='email the grade report to user')
parser.add_option('-w', '--weekly', action='store_true', dest='weekly',
        help='diffs using the grades from a week ago')
parser.add_option('-n', '--no-log', action='store_true', dest='nolog',
        help='does not log grades in grades database')
parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
        help='outputs more information')
parser.add_option('-d', '--diff', action='store_true', dest='diff',
        help='only returns classes with grades that have changed')

(options, args) = parser.parse_args()

class course:
    """an object for an individual class, contains a grade and class name"""
    def __init__(self, name, grade):
        self.grade = grade
        self.name = name
        self.diff = self.diff_grade(grade, name)

    def get_letter_grade(self):
        """returns the letter equivalent of the class's grade"""
        ap = bool(get_config('Grades')['use_ap_scaling']) and 'AP' in self.name
        meets_cutoff = lambda x: self.grade >= float(get_config('Grades')[x + '_cutoff'])

        if ap and meets_cutoff('a'):
            return 'A+'
        elif (ap and meets_cutoff('b')) or meets_cutoff('a'):
            return 'A'
        elif (ap and meets_cutoff('c')) or meets_cutoff('b'):
            return 'B'
        elif meets_cutoff('c'):
            return 'C'
        elif meets_cutoff('d'):
            return 'D'
        else:
            return 'F'

    def diff_grade_weekly(self):
        return self.diff_grade_custom(self.grade, self.name, date-timedelta(days=7))

    def diff_grade_custom(self, comp_grade, class_name, comp_date):
        """returns the difference between the current class grade and the grade from the provided
        timedelta
        """
        diff = ''
        for entry in reversed(utils.read_csv('data.csv')):
            if entry[0] == class_name and entry[2] == str(comp_date):
                diff = float(entry[1]) - float(comp_grade)
                if diff < 0:
                    return '+' + str(diff)
                else:
                    return diff
        return 0.0

    def diff_grade(self, diff_grade, class_name):
        """returns the difference between the current class grade
        and the last one
        """
        diff = ''
        for name, grade, date in reversed(utils.read_csv('data.csv')):
            if name == class_name:
                return float(grade) - float(diff_grade)
        return 0.0

    def __str__():
        return self.name

def setup():
    """general setup commands"""
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    if options.verbose:
        br.set_debug_http(True)

    # User-Agent
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


def get_base_url():
    """returns the site's base url, taken from the login page url"""
    return get_config('Authentication')['login_url'].split("/campus")[0] + '/campus/'

def get_schedule_page_url():
    """returns the url of the schedule page"""
    school_data = br.open(get_base_url() + 'portal/portalOutlineWrapper.xsl?x=portal.PortalOutline&contentType=text/xml&lang=en')
    dom = minidom.parse(school_data)

    node = dom.getElementsByTagName('Student')[0]
    person_id = node.getAttribute('personID')
    first_name = node.getAttribute('firstName')
    last_name = node.getAttribute('lastName')

    node = dom.getElementsByTagName('Calendar')[0]
    school_id = node.getAttribute('schoolID')

    node = dom.getElementsByTagName('ScheduleStructure')[0]
    calendar_id = node.getAttribute('calendarID')
    structure_id = node.getAttribute('structureID')
    calendar_name = node.getAttribute('calendarName')

    return utils.url_fix(get_base_url() + u"portal/portal.xsl?x=portal.PortalOutline&lang=en&personID={}&studentFirstName={}&lastName={}&firstName={}&schoolID={}&calendarID={}&structureID={}&calendarName={}&mode=schedule&x=portal.PortalSchedule&x=resource.PortalOptions".format(
                                                                    person_id,
                                                                    first_name,
                                                                    last_name,
                                                                    first_name,
                                                                    school_id,
                                                                    calendar_id,
                                                                    structure_id,
                                                                    calendar_name))

def get_class_links():
    """loops through the links in the schedule page
    and adds the grade page links to the link_list array
    """
    r = br.open(get_schedule_page_url())
    soup = BeautifulSoup(r)
    table = soup.find('table', cellpadding=2, bgcolor='#A0A0A0')
    link_list = []
    for row in table.findAll('tr')[1:get_num_blocks()+1]:
        for col in row.findAll('td'):
            link = col.find('a')['href']
            if 'mailto' in link:
                link = None
            link_list.append(link)

    return link_list

def get_term():
    """returns the current term"""
    r = br.open(get_schedule_page_url()) #opens schdule page
    soup = BeautifulSoup(r)
    terms = soup.findAll('th', {'class':'scheduleHeader'}, align='center')
    count = 0
    for term in terms:
        if "(" in term.text:
            count += 1
            date_begin, date_end = utils.between('(', ')', term.text).split('-')
            string_to_date = lambda string: datetime.strptime(string, '%m/%d/%y')
            if string_to_date(date_begin) <= datetime.now() <= string_to_date(date_end):
                return count
    raise StandardError("Couldn't find current term")

def get_num_blocks():
    """returns the number of blocks per day"""
    r = br.open(get_schedule_page_url()) #opens schdule page
    soup = BeautifulSoup(r)
    blocks = soup.findAll('th', {'class':'scheduleHeader'}, align='center')
    count = 0
    for block in blocks:
        if "(" not in block.text:
            count += 1
    return count

def parse_page(url_part):
    """parses the class page at the provided url and returns a course object for it"""
    page = br.open(get_base_url() + url_part)
    soup = BeautifulSoup(page)
    grade = float(soup.findAll(name='a', attrs={'class':'gridPartOfTermGPA'}, limit=1)[0].span.string[:-2])
    course_name = soup.findAll(name='div', attrs={'class':'gridTitle'}, limit=1)[0].string
    course_name = string.replace(course_name, '&amp;', '&')
    return course(course_name, grade)

def get_grades():
    """opens all pages in the link_list array and adds
    the last grade percentage and the corresponding class name
    to the grades list
    """
    grades = []
    class_links = get_class_links()
    term = get_term()
    for num, link in enumerate(class_links):
        if (num+1) % term == 0 and link is not None:
            grades.append(parse_page(link))
    return grades

def login():
    """Logs in to the Infinite Campus at the
    address specified in the config
    """
    br.open(get_config('Authentication')['login_url'])
    br.select_form(nr=0) #select the first form
    br.form['username'] = get_config('Authentication')['username']
    br.form['password'] = get_config('Authentication')['password']
    br.submit()


def add_to_grades_database(grades):
    """Adds the class and grade combination to the database under
    the current date.
    """
    for c in grades:
        utils.add_to_csv('data.csv', [c.name, c.grade, date.today()])

def get_grade_string(grades):
    """Extracts the grade_string, calculates the diff from
    grade dict and return it
    """
    final_grade_string = ''
    for c in grades:
        letter_grade = c.get_letter_grade()
        diff = c.diff
        if diff > 0:
            diff = "+" + str(round(float(diff), 2))
        else:
            diff = round(float(diff), 2)
        if not options.diff or options.diff and diff != 0.0:
            final_grade_string += "{} - {}% - {} (diff: {}%)\n".format(letter_grade,
                                                                c.grade,
                                                                c.name,
                                                                diff)
    return final_grade_string

def get_weekly_report(grades):
    """Generates the grade string, using a weekly diff"""
    final_grade_string = ''
    for c in grades:
        letter_grade = c.get_letter_grade()
        diff = c.diff_grade_weekly()
        if diff > 0:
            diff = "+" + str(round(float(diff), 2))
        else:
            diff = round(float(diff), 2)
        if diff != '':
            if not options.diff or options.diff and diff != 0.0:
                final_grade_string += '{} - {}% - {} (weekly diff: {}%)\n'.format(letter_grade,
                                                                            c.grade,
                                                                            c.name,
                                                                            diff)
    if final_grade_string == '':
        final_grade_string = '*************************\nNo data from one week ago\n*************************\n'
    return final_grade_string

def get_config(section):
    """returns a list of config options in the provided sections
    requires that config is initialized"""
    if not Config:
        return 'Config not found'
    dict1 = {}
    for opt in Config.options(section):
        try:
            dict1[opt] = Config.get(section, opt)
            if dict1[opt] == -1:
                print('skip: %s' % opt)
        except Exception:
            print('exception on %s!' % opt)
            dict1[opt] = None
    return dict1

def main():
    setup()
    login()
    grades = get_grades()

    if not options.nolog:
        add_to_grades_database(grades)

    if options.weekly:
        final_grade_string = get_weekly_report(grades)
    else:
        final_grade_string = get_grade_string(grades)

    if options.print_results:
        print final_grade_string, #comma removes newline
    if options.email:
        utils.send_email(get_config('Email')['smtp_address'],
                get_config('Email')['username'],
                get_config('Email')['password'],
                get_config('Email')['receiving_email'],
                'Grades',
                final_grade_string)

if __name__ == '__main__':
    main()
