#!/usr/bin/env python3
"""
Process a Dominion package backup file, extracting images and hashing them
"""

import sys
import logging
import zipfile

def main():
    zipf = zipfile.ZipFile(sys.argv[1])

    for zipinfo in zipf.infolist():
        logging.error("Encountering file %s" % zipinfo.filename)
        if zipinfo.filename.endswith(".tif"):
            raw = zipf.open(zipinfo.filename).read()
            print(f'{len(raw)}')

if __name__ == '__main__':
    main()
