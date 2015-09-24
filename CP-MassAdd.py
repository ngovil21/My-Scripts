CSV_FILE = ''
CP_URL = 'http://127.0.0.1:5050'
CP_API = ''

CP_PROFILE_ID = ''
CP_CATEGORY_ID = ''
CP_FORCE_READD = 'true'

import sys
import json

import csv

if sys.version < '3':
    import urllib, urllib2
else:
    from urllib import request, parse


def search_imdb_id(title):
    search_url = CP_URL + '/api/' + CP_API + '/search/'
    try:
        if sys.version < '3':
            encode = urllib.urlencode({'q': title})
            search_response = urllib2.urlopen(search_url, encode)
        else:
            encode = parse.urlencode({'q': title}).encode('utf-8')
            search_response = request.urlopen(search_url, encode)
        if search_response:
            parsed_response = json.loads(search_response.read().decode('utf-8'))
            if 'movies' in parsed_response:
                return parsed_response['movies'][0]['imdb']
    except:
        pass
    return ''


def main(file):
    with open(file, 'r') as csv_file:
        data = csv.reader(csv_file)
        for row in data:
            movie_title = row[0]
            if len(row) > 1:
                imdb_id = row[1]
            else:
                imdb_id = search_imdb_id(movie_title)

            data_headers = {
                'profile_id': CP_PROFILE_ID,
                'category_id': CP_CATEGORY_ID,
                'force_readd': CP_FORCE_READD,
                'identifier': imdb_id
            }

            url = CP_URL + '/api/' + CP_API + '/movie.add/'
            if sys.version < '3':
                data_encoded = urllib.urlencode(data_headers)
                response = urllib2.urlopen(url, data_encoded)
            else:
                data_encoded = parse.urlencode(data_headers).encode('utf-8')
                response = request.urlopen(url, data_encoded)
            if response:
                parsed_response = json.loads(response.read().decode('utf-8'))
                if parsed_response['success']:
                    print("Successfully added: " + movie_title + "  Imdb Id: " + imdb_id)
                else:
                    print("Failed to add : " + movie_title + "  Imdb Id: " + imdb_id)

# Run the main function
main(CSV_FILE)
