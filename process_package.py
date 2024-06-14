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

* Parse Batches Loaded Report.xml and update database, tracking newly finalized ballots
* Only generate hashes for the new ones

* Add any metadata to png image?
  * reproduce timestamp of tiff? or of first AuditMark or adjudication?
   or current timestamp? now or beginning of run?
  * election name?
  * county?
  * signature

* Confirm match for count of ballot sheets vs number of hashes for ballot sheets (front side)

* Audit ballot image hash data vs cvr data - make sure there is one-for-one correspondence.

"""

import sys
import os
import logging
import argparse
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
    parser = argparse.ArgumentParser(
        description='Process a Dominion package backup file, extracting images and hashing them.')
    parser.add_argument('zipfile', type=str, help='The zip file to process.')
    parser.add_argument('-d', '--debug', type=int, default=0, help='Set the debug level.')
    args = parser.parse_args()

    logging.basicConfig(level=args.debug)

    logging.info(f"Starting processing of zip file {args.zipfile}")
    try:
        zipf = zipfile.ZipFile(args.zipfile)
    except (FileNotFoundError, zipfile.BadZipFile) as e:
        logging.error(f"Failed to open zip file {args.zipfile}: {e}")
        sys.exit(1)

    skipcount = 0
    for zipinfo in zipf.infolist():
        if zipinfo.is_dir():
            continue

        # Count files that are not in the "Results" directory
        if "/Results/" not in zipinfo.filename:
            skipcount += 1
            continue

        logging.info("Encountering file %s" % zipinfo.filename)
        if zipinfo.filename.endswith(".tif"):
            fn = zipinfo.filename
            ballot_name = os.path.splitext(os.path.basename(fn))[0]
            try:
                with zipf.open(fn) as zf:
                    raw = zf.read()
            except Exception as e:
                logging.error(f"Failed to read file {fn} from zip: {e}")
                continue
            logging.info(f"Read {fn}, {len(raw)} B")
            buffer = io.BytesIO(raw)
            try:
                image = Image.open(buffer)
            except Exception as e:
                logging.error(f"Failed to open image from file {fn}: {e}")
                continue

            for tiff_page, image_data in enumerate(extract_pngs(image)):
                process_png(ballot_name, tiff_page, image_data)
                logging.info(f"Successfully processed image {tiff_page} from file {fn}")
        else:
            logging.info(f"Skipping file {zipinfo.filename}")

    logging.info(f"Skipped {skipcount} files not in Results directory")
    logging.info(f"Finished processing of zip file {args.zipfile}")


def process_png(ballot_name, tiff_page, image_data):
    """Convert a single page of a tiff image to PNG, hash it and save it to disk"""

    pngname = f'{ballot_name}-{tiff_page}.png'
    image_data_content = image_data.read()
    hash_sha256 = hashlib.sha256(image_data_content)
    print(f'{hash_sha256.hexdigest()}: {pngname}')
    with open(pngname, "wb") as pngfile:
        pngfile.write(image_data_content)


if __name__ == '__main__':
    main()
