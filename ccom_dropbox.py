__author__ = 'Nikhil'

import sys
import os

MAX_FILE_SIZE = 10  # Max file size in Megabytes

SOURCE_DIR = "C:\\Users\\Nikhil\\OneDrive\Documents\\CCOM\\Classes"  # Source Directory to make relative paths from
LINK_DIR = "C:\\Users\\Nikhil\\Dropbox\\CCOM\\Classes"  # Link Directory where link is placed

hard = True

target = str(sys.argv[1])
fname = os.path.basename(target)

if __name__ == "__main__":
    if os.path.getsize(target) > MAX_FILE_SIZE * 1024 * 1024:
        print("File is too big for linking!")
        exit()
    if target.startswith(SOURCE_DIR):  # If it's from the source directory, then make a relative path in the link directory
        relpath = os.path.relpath(target, SOURCE_DIR)  # Get the relative path to the target file from the source directory
        linkpath = os.path.join(LINK_DIR, relpath)
    else:
        linkpath = os.path.join(LINK_DIR, fname)

    dirpath = os.path.dirname(linkpath)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath, exist_ok=True)
    if not os.path.exists(linkpath):
        os.link(target, linkpath)
