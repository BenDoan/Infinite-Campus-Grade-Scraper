#!/usr/bin/env python

import ConfigParser
import cookielib
import mechanize
import string

from BeautifulSoup import BeautifulSoup
from datetime import date, timedelta, datetime
from optparse import OptionParser
from xml.dom import minidom

import utils

br = mechanize.Browser()
date = date.today()
Config = ConfigParser.ConfigParser()
Config.read('config.ini')

parser = OptionParser(description='A script to scrape grades from an infinite campus website')
parser.add_option('-p', '--print', action='store_true', dest='print_results',
        help='prints the grade report to stdout')
parser.add_option('-e', '--email', action='store_true', dest='email',
        help='email the grade report to user')
parser.add_option('-w', '--weekly', action='store_true', dest='weekly',
        help='diffs using the grades from a week ago')

(options, args) = parser.parse_args()

class course:
    """an object for an individual class, contains a grade and class name"""
    grade = 0
    name = ''
    def __init__(self, name, grade):
        self.grade = grade
        self.name = name

    def get_letter_grade(self):
        """returns the letter equivalent of the class's grade"""
        ap = bool(get_config('Grades')['use_ap_scaling']) and 'AP' in self.name
        float_grade = float(self.grade)
        if ap and bool(get_config('Grades')['use_ap_scaling']) and float_grade >= float(get_config('Grades')['a_cutoff']):
            return 'A+'
        elif (ap and float_grade >= float(get_config('Grades')['b_cutoff'])) or float_grade >= float(get_config('Grades')['a_cutoff']):
            return 'A'
        elif (ap and float_grade >= float(get_config('Grades')['c_cutoff'])) or float_grade >= float(get_config('Grades')['b_cutoff']):
            return 'B'
        elif float_grade >= float(get_config('Grades')['c_cutoff']):
            return 'C'
        elif float_grade >= float(get_config('Grades')['d_cutoff']):
            return 'D'
        else:
            return 'F'
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

    # User-Agent
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

def diff_grade_custom(grade, class_name, date):
    """returns the difference between the current class grade and the grade from the provided date"""
    diff = ''
    for line in utils.read_csv('data.csv')[::-1]:
        if line[0] == class_name and line[2] == str(date):
            diff = float(line[1]) - float(grade)
            if diff > 0:
                return '+' + str(diff)
            else:
                return diff
    return diff

def diff_grade(grade, class_name):
    """returns the difference between the current class grade
    and the last one
    """
    diff = ''
    got_first = False #we need to skip the grade we just added to the database
    for line in utils.read_csv('data.csv')[::-1]:
        if line[0] == class_name:
            if got_first:
                diff = float(line[1]) - float(grade)
                if diff > 0:
                    return "+" + str(diff)
                else:
                    return diff
            else:
                got_first = True
    return 0.0

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

#def string_to_date(string):
    #return datetime.strptime(string, '%m/%d/%y')

def get_term():
    """returns the current term"""
    r = br.open(get_schedule_page_url()) #opens schdule page
    soup = BeautifulSoup(r)
    terms = soup.findAll('th', {'class':'scheduleHeader'}, align='center')
    dates = []
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
        if c.name != '':
            utils.add_to_csv('data.csv', [c.name, c.grade, date])

def get_grade_string(grades):
    """Extracts the grade_string, calculates the diff from
    grade dict and return it
    """
    final_grade_string = ''
    for c in grades:
        letter_grade = c.get_letter_grade()
        diff = diff_grade(c.grade, c.name)
        final_grade_string += "{} - {}% - {} (diff: {}%)\n".format(letter_grade,
                                                                c.grade,
                                                                c.name,
                                                                round(float(diff), 2))
    return final_grade_string

def get_weekly_report(grades):
    """Generates the grade string, using a weekly diff"""
    final_grade_string = ''
    for c in grades:
        if c.grade != '':
            letter_grade = c.get_letter_grade()
            diff = diff_grade_custom(c.grade, c.name, date-timedelta(days=7))
            if diff != '':
                final_grade_string += '%s - %s%% - %s (weekly diff: %r)\n' % (letter_grade,
                                                                                c.grade,
                                                                                c.name,
                                                                                round(float(diff), 2))
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
    add_to_grades_database(grades)

    if options is not None:
        if options.weekly:
            final_grade_string = get_weekly_report(grades)
        else:
            final_grade_string = get_grade_string(grades)

        if options.print_results:
            print final_grade_string
        if options.email:
            utils.send_email(get_config('Email')['smtp_address'],
                    get_config('Email')['username'],
                    get_config('Email')['password'],
                    get_config('Email')['receiving_email'],
                    'Grades', final_grade_string)

if __name__ == '__main__':
    main()
