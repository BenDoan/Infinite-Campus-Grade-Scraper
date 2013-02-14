#!/usr/bin/env python

#to schedule in windows:
#schtasks /Create /SC DAILY /TN PythonTask /TR "PATH_TO_PYTHON_EXE PATH_TO_PYTHON_SCRIPT"

import cookielib
import csv
import mechanize
import re
import smtplib
import string

from BeautifulSoup import BeautifulSoup
from datetime import date, timedelta
from optparse import OptionParser

import config

parser = OptionParser(description="A script to scrape grades from an infinite campus website")
parser.add_option("-p", "--print", action="store_true", dest="print_results",
        help="prints the grade report to stdout")
parser.add_option("-e", "--email", action="store_true", dest="email",
        help="email the grade report to user")
parser.add_option("-w", "--weekly", action="store_true", dest="weekly",
        help="diffs using the grades from a week ago")

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
    send_info = "From: %s\nTo: %s\nSubject: %s\nX-Mailer: My-Mail\n\n" % (config.EMAIL_USERNAME, address, subject)

    server = smtplib.SMTP(config.EMAIL_SMTP_ADDRESS)
    server.starttls()
    server.login(config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
    server.sendmail(config.EMAIL_USERNAME, address, send_info + message)
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

def diff_grade_weekly(grade_dict, className, date):
    """returns the difference between the current class grade and the last one"""
    diff = ""
    for y in read_csv('data.csv'):
        if y[0] == className and y[2] == str(date):
            diff = float(grade_dict[className]) - float(y[1])
    if diff > 0:
        diff = "+" + str(diff)
    return diff

def diffGrade(grade_dict, className):
    """returns the difference between the current class grade and the last one"""
    diff = ""
    got_first = False
    for y in read_csv('data.csv')[::-1]:
        if y[0] == className:
            if got_first:
                diff = float(y[1]) - float(grade_dict[className])
                if diff > 0:
                    return "+" + str(diff)
                else:
                    return diff
            else:
                got_first = True
    return diff

def get_class_links():
    """loops through the links in the schedule page
    and adds the grade page links to the link_list array
    """
    r = br.open(config.SCHEDULE_URL) #opens schdule page
    soup = BeautifulSoup(r)
    table = soup.find("table", cellpadding=2, bgcolor="#A0A0A0")
    link_list = []
    for row in table.findAll("tr")[1:6]:
        for col in row.findAll('td'):
            link = col.find('a')['href']
            if "mailto" in link:
                link = None
            link_list.append(link)

    return link_list

def get_term(class_links):
    """returns the current term"""
    term = 0
    for class_link in enumerate(class_links[0:3]):
        if class_link[1] is not None:
            term = class_link[0]
    return term

def get_grade_dict():
    """opens all pages in the link_list array and adds
    the last grade percentage and the corresponding class name
    to the grade_list dict
    """
    grade_dict = {}
    class_links = get_class_links()
    term = get_term(class_links)
    base_url = config.LOGIN_URL.split("/campus")[0] + '/campus/'
    for link in enumerate(class_links[term:]):
        if link[0] % 4 == 0:
            if link[1] is not None:
                page = br.open(base_url + link[1]).readlines()
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
    br.open(config.LOGIN_URL)
    br.select_form(nr=0)
    br.form['username'] = config.USERNAME
    br.form['password'] = config.PASSWORD
    br.submit()


def add_to_grades_database(grade_dict):
    """Adds the class and grade combination to the database under
    the current date.
    """
    for class_name in grade_dict:
        if grade_dict[class_name] != "":
            add_to_csv('data.csv', [class_name,grade_dict[class_name],date])

def get_letter_grade(percent):
    """returns the letter equivalent of the percent param"""
    if float(percent) >= config.A_CUTOFF:
        return "A"
    elif float(percent) >= config.B_CUTOFF:
        return "B"
    elif float(percent) >= config.C_CUTOFF:
        return "C"
    elif float(percent) >= config.D_CUTOFF:
        return "D"
    else:
        return "F"

def get_grade_string(grade_dict):
    """Extracts the grade_string, calculates the diff from
    grade dict and return it
    """
    final_grade_string = ""
    for class_name in grade_dict:
        if grade_dict[class_name] != "":
            diff = diffGrade(grade_dict, class_name)
            if config.USE_AP_SCALING and "AP" in class_name:
                letter_grade = get_letter_grade(float(grade_dict[class_name]) + 7.5)
                if grade_dict[class_name] > config.A_CUTOFF + 15:
                    letter_grade = letter_grade += "+"
            else:
                letter_grade = get_letter_grade(grade_dict[class_name])
            final_grade_string += letter_grade + " - " + grade_dict[class_name] + '% - ' + class_name + " (diff: " + str(diff) + "%)" + '\n';
    return final_grade_string

def get_weekly_report(grade_dict):
    """Generates the grade string, using a weekly diff"""
    final_grade_string = ""
    for class_name in grade_dict:
        if grade_dict[class_name] != "":
            diff = diff_grade_weekly(grade_dict, class_name, date-timedelta(days=7))
            if config.USE_AP_SCALING and "AP" in class_name:
                letter_grade = get_letter_grade(float(grade_dict[class_name]) + 7.5)
            else:
                letter_grade = get_letter_grade(grade_dict[class_name])
            if diff != "":
                final_grade_string += letter_grade + " - " + grade_dict[class_name] + '% - ' + class_name + " (weekly diff: " + str(diff) + "%)" + '\n';
    if final_grade_string == "":
        final_grade_string = "************************\nNo data from one week ago\n************************\n"
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
            send_email(config.RECEIVING_EMAIL, "Grades", final_grade_string)

main()
