#!/usr/bin/env python3

import configparser
import csv
import itertools
import requests
import sys

credentialFileName = 'credentials.ini'
maxFailCount = 2


def main(args):
    config = configparser.ConfigParser()
    config.read(credentialFileName)
    hostname, payload = extractCreds(config)
    token = getToken(hostname, payload)

    csvFileName = args[1]

    hasRequiredColumns = checkCsvFile(csvFileName)
    if not hasRequiredColumns:
        sys.exit('csv file does not have the required fields')

    fp = open(csvFileName, newline='')
    reader = csv.DictReader(fp)

    global counter
    counter = 0
    for row in reader:
        failCount = 0
        while failCount < maxFailCount:
            article = extractArticle(row, token)
            printf('.')
            r = requests.post('{}/api/entries.json'.format(hostname), article)
            if not connectionFailed(r):
                counter += 1
                break
            else:
                failCount += 1
                printf('-')
                token = getToken(hostname, payload)
                article['access_token'] = token
        if failCount == 2:
            print('\nConnection failed.\nAborting.')
            break
    fp.close()


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


def checkCsvFile(csvFileName):
    '''
    ensures that the CSV file has the right columns

    returns bool
    '''
    with open(csvFileName, 'r') as f:
        firstLine = f.readline().strip()

    requiredFields = ['url', 'is_read', 'is_fav']
    hasRequiredColumns = False

    for l in itertools.permutations(requiredFields):
        toMatch = '{},{},{}'.format(l[0], l[1], l[2])
        doesMatch = (firstLine == toMatch)
        if doesMatch:
            hasRequiredColumns = True
            break
    return hasRequiredColumns


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
