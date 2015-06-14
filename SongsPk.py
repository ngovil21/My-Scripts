__author__ = 'Nikhil'

DOWNLOAD_LOCATION = "C:\\Users\\Nikhil\\Downloads\\MP3"
MINIMUM_MATCH = 70

auto = True

import urllib.request

import sys
import argparse
import re
import time
import requests
import os.path
from fuzzywuzzy import fuzz
import uuid
import shutil


def testURL():
    import urllib
    response = urllib.request.urlopen("http://www.hindistop.com/chakravartin-ashoka-samrat-2/")
    if response:
        print(response.readall().decode('utf-8'))

def getBetween(string, t1, t2, start=0):
    startIndex = string.find(t1, start)
    if startIndex == -1:
        return None
    startIndex += len(t1)
    endIndex = string.find(t2, startIndex)
    if endIndex == -1:
        return None
    return string[startIndex:endIndex]


def getPage(url, retries=3, wait=1):
    for i in range(0, retries):
        response = urllib.request.urlopen(url)
        if response:
            return response.readall().decode('utf-8')
        time.sleep(wait)
    return None


def downloadFile(url, filename, attempts=3):
    # NOTE the stream=True parameter
    for i in range(0,attempts):
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=16 * 1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        if os.path.getsize(filename) > 512 * 1024:                  #if file greater than 512kB assume it downloaded correctly, otherwise try again
            return filename
        os.remove(filename)
        print("File too small...Retry?")


def getLastTag(html, position=0, start=0, startTag='<', endTag='>'):
    endIndex = html[:position].rfind(endTag, start)
    if endIndex == -1:
        return None
    startIndex = html[:endIndex].rfind(startTag, start)
    if startIndex == -1:
        return None
    return html[startIndex:endIndex + 1]


def getLinkFromTag(tag):
    startIndex = tag.find('href="')
    if startIndex == -1:
        return None
    startIndex += 6
    return tag[startIndex:tag.find('"', startIndex)]


parser = argparse.ArgumentParser()

parser.add_argument("search", type=str)
parser.add_argument("--album", "-album", "-a", action="store_true", default=False)
parser.add_argument("--manual", "-manual", "-m", action="store_true", default=False)

args = parser.parse_args()

findAlbum = False

if args.search:
    search = args.search
findAlbum = args.album
auto = not args.manual

if findAlbum:
    first_char = search[0]
    if first_char.isdigit():
        url = "http://www.songspk.link/numeric_list.html"
    else:
        url = "http://www.songspk.link/" + first_char.lower() + "_list.html"
    # print(url)
    source = getPage(url)
    if not source:
        print("Cannot load album page!")
        sys.exit(0)
    startIndex = source.find('<ul class="ctlg-holder">')
    startIndex = source.find('<li>', startIndex)
    startIndex = source.find('<li>', startIndex)
    endIndex = source.find('<br>', startIndex)
    endIndex = source[:endIndex].rfind('</li>', startIndex) + 5
    source = source[startIndex:endIndex]
    source = re.sub("\s+", " ", source)
    matches = []
    pos = 0
    while True:
        pos = source.find("<a href", pos)
        if pos == -1:
            break
        album_name = getBetween(source, '>', '<', pos).strip()
        match = fuzz.UWRatio(search, album_name)
        # print("%s %3.1f%%" % (album_name, match))
        if match > MINIMUM_MATCH:
            matches.append((match, album_name, pos))
        pos += 1
    if len(matches) == 0:
        print("Album not found!")
        sys.exit(0)
    matches = sorted(matches, reverse=True)
    if auto:
        album = matches[0]
    else:
        print("   Match  Album")
        if len(matches) > 5:
            max = 5
        else:
            max = len(matches)
        for i in range(0, max):
            key = matches[i]
            print("%d. %3d%%   %s" % (i + 1, key[0], key[1]))
        j = int(input("Please select the album: "))
        album = matches[j-1]
        print("You selected %d. %s" % (j, album[1]))
    pos = album[2]
    if pos != -1:
        tag = getBetween(source, "<", ">", pos)
        page = getLinkFromTag(tag)
        response = getPage("http://www.songspk.link/" + page)
        if not response:
            print("Could not load album page!")
            sys.exit(1)
        source = getBetween(response, "<body", "</body>")                   # get only source between body to avoid scripts
        song_link_match = "http:\/\/link[\d]?\.songspk\.name\/song[\d]?\.php\?songid=[\d]+"
        startpos = 0
        for m in re.finditer(song_link_match, source):
            song_link = m.group(0)
            song_title = re.sub("\s+", " ", getBetween(source, '">', "</a", m.end())).strip()
            if len(song_title) > 50:
                print("Possible error scraping song title...")
                song_title = str(uuid.uuid4())
            print(song_link)
            file_dir = os.path.join(DOWNLOAD_LOCATION, album[1])
            if not os.path.isdir(file_dir):
                os.makedirs(file_dir)
            # urllib.request.urlretrieve(song_link, os.path.join(DOWNLOAD_LOCATION, song_title + ".mp3"))
            downloadFile(song_link, os.path.join(file_dir, song_title + ".mp3"))
