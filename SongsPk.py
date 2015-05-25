__author__ = 'Nikhil'


DOWNLOAD_LOCATION = "C:\\Users\\Nikhil\\Downloads\\MP3"

import urllib.request

import sys
import argparse
import re
import time
import requests
import os.path


def getBetween(string, t1, t2, start=0):
    startIndex = string.find(t1, start)
    if startIndex == -1:
        return None
    startIndex += len(t1)
    endIndex = string.find(t2,startIndex)
    if endIndex == -1:
        return None
    return string[startIndex:endIndex]

def getPage(url, retries=3, wait=1):
    for i in range(0,retries):
        response = urllib.request.urlopen(url)
        if response:
            return response.readall().decode('utf-8')
        time.sleep(wait)
    return None

def downloadFile(url, filename):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=32*1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                f.flush()
    return filename


def getLastTag(html, position=0, start=0, startTag='<', endTag='>'):
    endIndex = html[:position].rfind(endTag ,start)
    if endIndex == -1:
        return None
    startIndex = html[:endIndex].rfind(startTag,start)
    if startIndex == -1:
        return None
    return html[startIndex:endIndex+1]

def getLinkFromTag(tag):
    startIndex = tag.find('href="')
    if startIndex == -1:
        return None
    startIndex += 6
    return tag[startIndex:tag.find('"', startIndex)]


parser = argparse.ArgumentParser()

parser.add_argument("search", type=str)
parser.add_argument("--album", "-album","-a",action="store_true",default=False)

args = parser.parse_args()

findAlbum = False

if args.search:
    search = args.search
findAlbum = args.album


if findAlbum:
    first_char = search[0]
    if first_char.isdigit():
        url = "http://www.songspk.link/numeric_list.html"
    else:
        url = "http://www.songspk.link/" + first_char.lower() + "_list.html"
    #print(url)
    source = getPage(url)

    startIndex = source.find('<ul class="ctlg-holder">')
    startIndex = source.find('<li>', startIndex)
    startIndex = source.find('<li>', startIndex)
    endIndex = source.find('<br>', startIndex)
    endIndex = source[:endIndex].rfind('</li>', startIndex) + 5
    source = source[startIndex:endIndex]
    source = re.sub("\s+", " ", source)
    pos = source.find(search)
    if pos != -1:
        tag = getLastTag(source, pos)
        page = getLinkFromTag(tag)
        response = getPage("http://www.songspk.link/" + page)
        if not response:
            print("Could not load album page!")
            sys.exit(1)
        song_link_match = "http://link.songspk.name/song.php?songid="
        startpos = 0
        while True:
            startpos = response.find(song_link_match, startpos)
            if startpos == -1:
                break
            endpos = response.find('">', startpos)
            song_link = response[startpos:endpos]
            song_title = getBetween(response, '">', "</a", endpos)
            print(song_link)
            #urllib.request.urlretrieve(song_link, os.path.join(DOWNLOAD_LOCATION, song_title + ".mp3"))
            downloadFile(song_link, os.path.join(DOWNLOAD_LOCATION, song_title + ".mp3"))
            startpos = endpos

