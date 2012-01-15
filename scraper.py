#TODO: Deal with 100%s

#to schedule in windows:
#schtasks /Create /SC DAILY /TN PythonTask /TR "PATH_TO_PYTHON_EXE PATH_TO_PYTHON_SCRIPT"

import mechanize
import cookielib
import datetime
import re
import random
import smtplib

import config

def regex_search(regex, regex_string):
    """does a regex search on 'regex_string' and returns the results"""
    match = re.search(regex, regex_string)
    if match is not None:
        return match.group()

def print_alert(text):
    """prints 'text' surrounded by whitespace"""
    print "\n\n\n\n"
    print text
    print "\n\n\n\n"

def does_nothing(text):
    """does nothing"""
    pass

def is_regex_in_string(regex, regex_string):
    """checks if a regex match is in 'string'"""
    try:
        match = re.search(regex, regex_string)
        does_nothing(match.group())
        return True;
    except Exception, e:
        return False;

def between(left,right,s):
    """searches for text between left and right
    found here:http://stackoverflow.com/questions/3429086/python-regex-to-get-all-text-until-a-and-get-text-inside-brackets
    """
    before,_,a = s.partition(left)
    a,_,after = a.partition(right)
    return before,a,after

def send_email(address, subject, message):
    """sends an email using the gmail account info specifed in config"""
    send_info = "From: %s\nTo: %s\nSubject: %s\nX-Mailer: My-Mail\n\n" % (config.EMAILUSERNAME, address, subject)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(config.EMAILUSERNAME, config.EMAILPASSWORD)
    server.sendmail(config.EMAILUSERNAME, address, send_info + message)
    server.quit()


def setup():
    """general setup commands"""
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # debugging messages
    br.set_debug_http(True)
    br.set_debug_redirects(True)
    br.set_debug_responses(True)

    # User-Agent
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]




# Browser
br = mechanize.Browser()
setup()






r = br.open('https://www.campus.mpsomaha.org/campus/portal/millard.jsp?status=portalLogoff&lang=en')
br.select_form(nr=0)
br.form['username'] = config.USERNAME
br.form['password'] = config.PASSWORD ##these need to be set in the config.py file
br.submit()
r = br.open("https://www.campus.mpsomaha.org/campus/portal/portal.xsl?x=portal.PortalOutline&lang=en&context=187976-1119-1110&personID=187976&studentFirstName=Benjamin&lastName=Doan&firstName=Benjamin&schoolID=45&calendarID=1119&structureID=1110&calendarName=2011-2012%20Millard%20West%20HS&mode=schedule&x=portal.PortalSchedule&x=resource.PortalOptions")

link_list = []
grade_dict= {}

#loops through the links in the schedule page
#and adds the grade page links to the link_list
#array
for x in br.links():
    url = x.base_url + x.url
    if is_regex_in_string(r'\.PortalOut', url):
        link_list.append(x)

#opens all pages in the link_list array and adds
#the first percentage and the corresponding class name
#to the grade_list dict
for x in link_list:
    r = br.open(x.base_url + x.url)
    url_page = r.readlines()

    regex_string = '\n'.join(url_page)
    grade = regex_search(r'\d\d\.\d\d', regex_string) #selects the first percetage on the page

    for x in url_page:
        if is_regex_in_string(r'gridTitle', x):
            cur_class = '\n'.join(between(r'<div class="gridTitle">','</div>', x))
            cur_class = cur_class.rstrip()

    grade_dict[cur_class] = grade


print "\n\n\n\n\n\n"
final_grade_list = "";
for x in grade_dict:
    final_grade_list += x + ':\t\t' + grade_dict[x] + '%\n'
print final_grade_list

#send_email("bendoan5@gmail.com", "Grades", final_grade_list)
