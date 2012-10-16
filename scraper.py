#to schedule in windows:
#schtasks /Create /SC DAILY /TN PythonTask /TR "PATH_TO_PYTHON_EXE PATH_TO_PYTHON_SCRIPT"

import mechanize
import cookielib
import smtplib
import re
import csv
import config
import string

from datetime import date, timedelta
from optparse import OptionParser

parser = OptionParser(description="A script to scrape grades from an infinite campus website")
parser.add_option("-p", "--print", action="store_true", dest="print_results",
        help="prints the grade report to stdout")
parser.add_option("-e", "--email", action="store_true", dest="email",
        help="email the grade report to user")
parser.add_option("-w", "--weekly", action="store_true", dest="weekly",
        help="Changes the diff from the current grades and the last grades to the current grades and the grades from one week ago")

#allows for testing
try:
    (options, args) = parser.parse_args()
except SystemExit, e:
    options = None

br = mechanize.Browser()
date = date.today()

def regex_search(regex, regex_string):
    """does a regex search on 'regex_string' and returns the results

    >>> regex_search(r'...a', 'FJSIfdsa')
    'fdsa'
    """
    match = re.search(regex, regex_string)
    if match is not None:
        return match.group()

def does_nothing(text):
    """does nothing"""
    pass

def is_regex_in_string(regex, regex_string):
    """checks if a regex match is in string

    >>> is_regex_in_string(r'333', 'jaskljds3aksdlja33313d')
    True
    >>> is_regex_in_string(r'434', 'sdlkfnhds43asdasd')
    False
    """
    try:
        match = re.search(regex, regex_string)
        does_nothing(match.group())
        return True;
    except Exception :
        return False;

def between(left,right,s):
    """searches for text between left and right

    >>> between('tfs', 'gsa', 'tfsaskdfnsdlkfjkldsfjgsa')
    'askdfnsdlkfjkldsfj'
    """
    before,_,a = s.partition(left)
    a,_,after = a.partition(right)
    return a

def send_email(address, subject, message):
    """sends an email using the gmail account info specifed in config"""
    send_info = "From: %s\nTo: %s\nSubject: %s\nX-Mailer: My-Mail\n\n" % (config.EMAILUSERNAME, address, subject)

    server = smtplib.SMTP(config.EMAILSMTPADDRESS)
    server.starttls()
    server.login(config.EMAILUSERNAME, config.EMAILPASSWORD)
    server.sendmail(config.EMAILUSERNAME, address, send_info + message)
    server.quit()

def find_page_part(page_list, regex, before, after):
    """returns the text in between before and after,
    in the first line containg regex

    >>> find_page_part(('abc','ahd'),r'abc','a','c')
    'b'
    """
    toReturn = ""
    for x in page_list:
        if is_regex_in_string(regex, x):
            toReturn = between(before, after, x)
    return toReturn

def read_csv(file_name):
    """reads a csv file and returns it as a list of lists"""
    final_list = []
    reader = csv.reader(open(file_name, 'rb'), delimiter=',')
    for x in reader:
        final_list.append(x)
    return final_list

def add_to_csv(file_name, single_list):
    """adds a list to the specified csv file"""
    final_list = read_csv(file_name)
    writer = csv.writer(open(file_name, 'wb'), delimiter=',',quoting=csv.QUOTE_MINIMAL)
    final_list.append(single_list)
    for x in final_list:
        writer.writerow(x)

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

def diffGrade(grade_dict, className, date):
    """returns the difference between the current class grade and the last one"""
    diff = ""
    for y in read_csv('data.csv'):
        if y[0] == className and y[2] == str(date):
            diff = float(grade_dict[className]) - float(y[1])
    if diff > 0:
        diff = "+" + str(diff)
    return diff

def getClassLinks():
    """loops through the links in the schedule page
    and adds the grade page links to the link_list array
    """
    r = br.open(config.SCHEDULEURL) #opens schdule page
    link_list = []
    for link in br.links():
        url = link.base_url + link.url
        if is_regex_in_string(r'\.PortalOut', url):
            link_list.append(url)
    return link_list

def get_grade_dict():
    """opens all pages in the link_list array and adds
    the last grade percentage and the corresponding class name
    to the grade_list dict
    """
    grade_dict = {}
    for link in getClassLinks():
        page = br.open(link).readlines()
        grade = find_page_part(page, r'grayText', '<span class="grayText">', '%</span>')
        course_name = find_page_part(page, r'gridTitle', '<div class="gridTitle">', '</div>').rstrip()
        course_name = string.replace(course_name, '&amp;', '&')

        if grade is not None:
            grade_dict[course_name] = grade
        else:
            grade_dict[course_name] = "Error"
    return grade_dict

def login():
    """Logs in to the Infinite Campus at the
    address specified in the config
    """
    br.open(config.LOGINURL)
    br.select_form(nr=0)
    br.form['username'] = config.USERNAME
    br.form['password'] = config.PASSWORD ##these need to be set in the config.py file
    br.submit()


def add_to_grades_database(grade_dict):
    """Adds the class and grade combination to the database under
    the current date.
    """
    for class_name in grade_dict:
        if grade_dict[class_name] != "":
            add_to_csv('data.csv', [class_name,grade_dict[class_name],date])

def get_grade_string(grade_dict):
    """Extracts the grade_string, calculates the diff from
    grade dict and return it
    """
    final_grade_string = ""
    for x in grade_dict:
        if grade_dict[x] != "":
            diff = diffGrade(grade_dict, x, date)
            final_grade_string+= grade_dict[x] + '% - ' + x + " (diff: " + str(diff) + "%)" + '\n';
    return final_grade_string

def get_grade_string(grade_dict):
    """Extracts the grade_string, calculates the diff from
    grade dict and return it
    """
    final_grade_string = ""
    for x in grade_dict:
        if grade_dict[x] != "":
            diff = diffGrade(grade_dict, x, date)
            final_grade_string+= grade_dict[x] + '% - ' + x + " (diff: " + str(diff) + "%)" + '\n';
    return final_grade_string

def get_weekly_report(grade_dict):
    final_grade_string = ""
    for x in grade_dict:
        if grade_dict[x] != "":
            diff = diffGrade(grade_dict, x, date-timedelta(days=7))
            if diff != "":
                final_grade_string += grade_dict[x] + '% - ' + x + " (weekly diff: " + str(diff) + "%)" + '\n';
    if final_grade_string == "":
        final_grade_string = """************************\nNo data from one week ago\n************************"""
    return final_grade_string


def main():
    setup()
    login()
    grade_dict = get_grade_dict()
    add_to_grades_database(grade_dict)

    if options is not None:
        if options.weekly:
            final_grade_string = get_weekly_report(grade_dict)
        else:
            final_grade_string = get_grade_string(grade_dict)

        if options.print_results:
            print final_grade_string
        if options.email:
            send_email(config.RECIEVINGEMAIL, "Grades", final_grade_string)

main()
