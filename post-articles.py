#!/usr/bin/env python3

import requests
import configparser
import csv
import sys

counter = 0


def main(args):
    config = configparser.ConfigParser()
    config.read('credentials.ini')
    hostname, payload = extractCreds(config)
    token = getToken(hostname, payload)

    fp = open(args[1], newline='')
    reader = csv.DictReader(fp)

    global counter
    for row in reader:
        failCount = 0
        while failCount < 2:
            article = extractArticle(row, token)
            printf('.')
            r = requests.post('{}/api/entries.json'.format(hostname), article)
            if not connectionFailed(r):
                counter += 1
                break
            else:
                failCount += 1
                token = getToken(hostname, payload)
                article['access_token'] = token
        if failCount == 2:
            print('\nConnection failed.\nAborting.')
            break


def extractCreds(config):
    '''
    reads the config file and
    returns a tuple of the hostname (str)
    and the API request payload (dict)
    '''
    config = config.defaults()
    hostname = config['host']
    username = config['username']
    password = config['password']
    clientid = config['client_id']
    secret = config['c_secret']
    payload = {'username': username, 'password': password,
               'client_id': clientid, 'client_secret': secret,
               'grant_type': 'password'}
    return (hostname, payload)


def getToken(hostname, payload):
    '''
    acquires an API token

    returns str
    '''
    r = requests.get('{}/oauth/v2/token'.format(hostname), payload)
    token = r.json().get('access_token')
    refresh = r.json().get('refresh_token')
    payload['grant_type'] = 'refresh_token'
    payload['refresh_token'] = refresh
    return token


def extractArticle(row, token):
    '''
    interprets a line of the CSV file

    returns dict
    '''
    url = row['url']
    isRead = int(row['is_read'])
    isFaved = int(row['is_fav'])
    article = {'url': url, 'archive': isRead,
               'starred': isFaved, 'access_token': token}
    return article


def connectionFailed(response):
    '''
    checks if there was an error when connecting to the API

    returns bool
    '''
    return 'error' in response.json().keys()


def printf(text):
    '''
    prints text without newline at the end

    returns void
    '''
    print(text, end='', flush=True)

if __name__ == "__main__":
    try:
        main(sys.argv)
        print('\nposted {} articles\nfinished successfully.'.format(counter))
    except(KeyboardInterrupt):
        print('\nposted {} articles\naborted.'.format(counter))
