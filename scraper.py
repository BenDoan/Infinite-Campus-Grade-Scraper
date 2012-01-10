#TODO: Deal with 100%s


import mechanize
import cookielib
import datetime
import re
import random

import config

def regex_search(regex, regex_string):
    match = re.search(regex, regex_string)
    return match.group()

def print_alert(text):
    print "\n\n\n\n"
    print text
    print "\n\n\n\n"

def does_nothing(text):
    pass

def setup():
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
br.form['username'] = config.username
br.form['password'] = config.password ##these need to be set in the config.py file
br.submit()


r = br.open("https://www.campus.mpsomaha.org/campus/portal/portal.xsl?x=portal.PortalOutline&lang=en&context=187976-1119-1110&personID=187976&studentFirstName=Benjamin&lastName=Doan&firstName=Benjamin&schoolID=45&calendarID=1119&structureID=1110&calendarName=2011-2012%20Millard%20West%20HS&mode=schedule&x=portal.PortalSchedule&x=resource.PortalOptions")

link_list = []
grade_dict= {}
for x in br.links():
    url = x.base_url + x.url
    try:
        match = re.search(r'\.PortalOut', url)
        does_nothing(match.group)
        link_list.append(x)
    except Exception, e:
        pass

for x in link_list:
    r = br.open(x.base_url + x.url)
    regex_string = '\n'.join(r.readlines())
    grade = regex_search(r'\d\d\.\d\d', regex_string) #selects the first percetage on the page
    cur_class = 'math' + str(random.randrange(1000))
    print_alert(regex_string)

    grade_dict[cur_class] = grade



print "\n\n\n\n\n\n"
for x in grade_dict:
    print x + ': ' + grade_dict[x]
