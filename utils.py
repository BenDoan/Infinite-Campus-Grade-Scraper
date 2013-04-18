import csv
import os.path
import re
import smtplib
import urllib
import urlparse


def send_email(smtp_address, smtp_username, smtp_password, address, subject, message):
    """sends an email using the gmail account info specifed in config"""
    send_info = "From: %s\nTo: %s\nSubject: %s\nX-Mailer: My-Mail\n\n" % (smtp_username, address, subject)

    server = smtplib.SMTP(smtp_address)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_address, address, send_info + message)
    server.quit()

def read_csv(file_name):
    """reads a csv file and returns it as a list of lists"""
    final_list = []
    if not os.path.isfile(file_name):
        with open(file_name, 'w+'):
            pass
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

def url_fix(s, charset='utf-8'):
    """fixes spaces and query strings in urls, borrowed from werkzeug"""
    if isinstance(s, unicode):
        s = s.encode(charset, 'ignore')
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

def between(left,right,s):
    """searches for text between left and right

    >>> between('tfs', 'gsa', 'tfsaskdfnsdlkfjkldsfjgsa')
    'askdfnsdlkfjkldsfj'
    """
    before,_,a = s.partition(left)
    a,_,after = a.partition(right)
    return a
