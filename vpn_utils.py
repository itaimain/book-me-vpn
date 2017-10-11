#!/usr/bin/python

import sys
import urllib2
from bs4 import BeautifulSoup
import tempfile
import shutil
import os
import pickle
import zipfile

URL = "https://www.vpnbook.com"
URI = URL + '/freevpn'
USGAE = "vpnscript.py init\nvpnscript.py choose [chosen_vpn] [temp_file]"
DICT_FILE_NAME = 'dict.pkl'
LIST_FILE_NAME = 'list.pkl'
ZIP_DIR_NAME = 'zip_dir'
AUTH_FILE = 'auth.txt'

def download_web_page(url):
    return urllib2.urlopen(url).read()

def extract_servers_options(html):
    soup = BeautifulSoup(html, 'html.parser')
    main_links_div = soup.body.find('div', attrs = {'class' : 'one-third column box light featured'})

    all_links = main_links_div.find('ul', attrs = {'class' : 'disc'}).find_all('li')
    all_a = [link.find('a') for link in all_links]

    links_dict = {}
    for a in all_a:
        if None == a:
            continue
        links_dict[a.text] = a['href']

    username = ""
    password = ""
    for li in all_links:
        if li.text.startswith('Username'):
            username = li.find('strong').text
        elif li.text.startswith('Password'):
            password = li.find('strong').text

    return links_dict, username, password

def add_auth_to_ovpn_file(ovpn_file, auth_file_path):
    file_lines = open(ovpn_file, 'r').readlines()
    for index, line in enumerate(file_lines):
        if line.startswith('auth-user-pass'):
            file_lines[index] = 'auth-user-pass %s\n' % auth_file_path

    with open(ovpn_file, 'w') as f:
        f.writelines(file_lines)


def init():
    links_dict, username, password = extract_servers_options(download_web_page(URI))
    links_descs = sorted(links_dict.keys())
    dirpath = tempfile.mkdtemp()

    with open(dirpath + "/" + LIST_FILE_NAME, 'w') as f:
        f.write('\n'.join(links_descs))

    pickle.dump(links_dict, open(dirpath + "/" + DICT_FILE_NAME, 'w'))

    with open(dirpath + "/" + AUTH_FILE, 'w') as f:
        f.write('%s\n%s\n' % (username, password))

    print dirpath + "/" + LIST_FILE_NAME


def choose(chosen_vpn, tempfile):
    tempdir = os.path.dirname(tempfile)
    links_dict = pickle.load(open(tempdir + "/" + DICT_FILE_NAME, 'r'))
    chosen_link = ""

    if chosen_vpn in links_dict.keys():
        chosen_link = URL + links_dict[chosen_vpn]

    zip_file_name = tempdir + "/zip.zip"

    with open(zip_file_name, 'w') as f:
        f.write(urllib2.urlopen(chosen_link).read())
    with zipfile.ZipFile(zip_file_name) as zf:
        zf.extractall(path = tempdir)

    for filename in os.listdir(tempdir):
        if filename.endswith('.ovpn'):
            add_auth_to_ovpn_file('%s/%s' % (tempdir, filename), tempdir + "/" + AUTH_FILE)

    print tempdir

def clean(tempfile):
    tempdir = os.path.dirname(tempfile)
    shutil.rmtree(tempdir)

def main(argv):
    return_value = 0

    if 2 == len(argv) and 'init' == argv[1]:
        init()
    elif 3 == len(argv) and 'clean' == argv[1]:
        clean(argv[2])
    elif 4 == len(argv) and 'choose' == argv[1]:
        choose(argv[2], argv[3])
    else:
        print USGAE
        return_value = 1

    return return_value

if '__main__' == __name__:
    return_value = main(sys.argv)

    exit(return_value)
