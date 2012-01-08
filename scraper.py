import mechanize
import cookielib
import datetime
import re

import config

now = datetime.datetime.now()


# Browser
br = mechanize.Browser()

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



r = br.open('https://www.campus.mpsomaha.org/campus/portal/millard.jsp?status=portalLogoff&lang=en')
br.select_form(nr=0) 

br.form['username'] = config.username 
br.form['password'] = config.password ##these need to be set in the config.py file

br.submit()

r = br.open("https://www.campus.mpsomaha.org/campus/portal/portal.xsl?x=portal.PortalOutline&lang=en&context=187976-1119-1110&personID=187976&studentFirstName=Benjamin&lastName=Doan&firstName=Benjamin&schoolID=45&calendarID=1119&structureID=1110&calendarName=2011-2012%20Millard%20West%20HS&mode=schedule&x=portal.PortalSchedule&x=resource.PortalOptions")

regex_string = '\n'.join(r.readlines())
print regex_string

i = 1;
for x in br.links():
    print x.base_url + x.url
    print i
    i += 1


#r = br.open('https://www.campus.mpsomaha.org/campus/portal/portal.xsl?x=portal.PortalOutline&lang=en&context=187976-1119-1110&mode=classbook&calendarID=1119&structureID=1110&sectionID=514132&personID=187976&trialID=1577&x=portal.PortalClassbook')

# selects the first percetage on the pagee
#regex_string = '\n'.join(r.readlines())
#print regex_string
#match = re.search(r'\d\d\.\d\d', regex_string)
#print match.group()
