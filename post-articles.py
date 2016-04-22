#!/usr/bin/env python3

import requests
import configparser
import csv
import sys

counter = 0


def printf(text):
    print(text, end='', flush=True)


def main(args):
    c = configparser.ConfigParser()
    c.read('credentials.ini')
    c = c.defaults()

    hostname = c['host']
    username = c['username']
    password = c['password']
    clientid = c['client_id']
    secret = c['c_secret']
    payload = {'username': username, 'password': password,
               'client_id': clientid, 'client_secret': secret,
               'grant_type': 'password'}

    r = requests.get('{}/oauth/v2/token'.format(hostname), payload)
    token = r.json().get('access_token')

    fp = open(args[1], newline='')
    reader = csv.DictReader(fp)

    global counter
    for row in reader:
        url = row['url']
        isRead = int(row['is_read'])
        isFaved = int(row['is_fav'])
        article = {'url': url, 'archive': isRead,
                   'starred': isFaved, 'access_token': token}
        printf('.')
        r = requests.post('{}/api/entries.json'.format(hostname), article)
        counter += 1


if __name__ == "__main__":
    try:
        main(sys.argv)
        print('\nposted {} articles'.format(counter))
        print('finished')
    except(KeyboardInterrupt):
        print('\nposted {} articles'.format(counter))
        print('aborted')
