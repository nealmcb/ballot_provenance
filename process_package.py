#!/usr/bin/env python3
"""
Process a Dominion package backup file, extracting images and hashing them

Optionally save extracted png images as we go

Input or command-line argument: project backup as zip file, named after election

log, with timestamps:
  names of input files
  all batches processed  [any time batch name changes in set of tif files processed]
     [don't mark batches done until end of file? or end of batch]

TODO:

  * add any metadata to png image?
  *reproduce timestamp of tiff? or of first AuditMark or adjudication?
     or current timestamp? now or beginning of run?
  * election name?
  * county?
  * signature

Confirm match for count of ballot sheets vs number of hashes for ballot sheets (front side)

Audit ballot image hash data vs cvr data - make sure there is one-for-one correspondence.

"""

import sys
import os
import logging
import io
import zipfile
from PIL import Image, ImageSequence
import hashlib


def extract_pngs(tiffimage):
    """An iterator to return a series of png buffers from a multi-layer Image"""

    for page, image in enumerate(ImageSequence.Iterator(tiffimage)):
        """
        try to extract invariant part of ImageMark - which works sometimes, but sometimes width varies!
        if page == 2:
            width, height = image.size
            image = image.crop((0, height-392, width, height))
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        # image.show()
        buffer.seek(0)
        yield buffer


def main():
    zipf = zipfile.ZipFile(sys.argv[1])

    for zipinfo in zipf.infolist():
        logging.info("Encountering file %s" % zipinfo.filename)
        if zipinfo.filename.endswith(".tif"):
            fn = zipinfo.filename
            ballot_name = os.path.splitext(os.path.basename(fn))[0]
            with zipf.open(fn) as zf:
                raw = zf.read()
            print(f'{ballot_name}: {len(raw)}')
            buffer = io.BytesIO(raw)
            image = Image.open(buffer)

            # with open("/tmp/f.tif", "wb") as tf:
            #    tf.write(raw)

            for tiff_page, image_data in enumerate(extract_pngs(image)):
                process_png(ballot_name, tiff_page, image_data)


def process_png(ballot_name, tiff_page, image_data):
    """Convert a single page of a tiff image to PNG, hash it and save it to disk"""

    pngname = f'{ballot_name}-{tiff_page}.png'
    hash_sha256 = hashlib.sha256(image_data.read())
    print(f'{hash_sha256.hexdigest()}: {pngname}')
    with open(pngname, "wb") as pngfile:
        image_data.seek(0)
        pngfile.write(image_data.read())
    # f"{id}-%d.png


if __name__ == '__main__':
    main()
