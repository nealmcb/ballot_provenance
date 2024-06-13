#!/usr/bin/env python3
"""
Process a Dominion package backup file, extracting images and hashing them

Optionally extract into a new filesystem of png images as we go?

input or command-line argument: database named after election

log, with timestamps:
  names of input files
  all batches processed  [any time batch name changes in set of tif files processed]
     [don't mark batches done until end of file? or end of batch]

add any metadata?
  reproduce timestamp of tiff? or of first AuditMark or adjudication?
  or current timestamp? now or beginning of run?
  election name?
  county?
  signature

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
            bn = os.path.splitext(os.path.basename(fn))[0]
            with zipf.open(fn) as zf:
                raw = zf.read()
            print(f'{bn}: {len(raw)}')
            buffer = io.BytesIO(raw)
            image = Image.open(buffer)

            # with open("/tmp/f.tif", "wb") as tf:
            #    tf.write(raw)

            for i, page in enumerate(extract_pngs(image)):
                pngname = f'{bn}-{i}.png'
                hash_sha256 = hashlib.sha256(page.read())
                print(f'{hash_sha256.hexdigest()}: {pngname}')
                with open(pngname, "wb") as pngfile:
                    page.seek(0)
                    pngfile.write(page.read())
                # f"{id}-%d.png


def extract_images_from_tiff(input_file, output_dir):
    """Extracts each image from a TIFF file and saves it as a PNG file.

  Args:
    input_file: The path to the input TIFF file.
    output_dir: The directory where the output PNG files will be saved.
  """

    with Image.open(input_file) as image:
        for i in range(image.n_frames):
            image.seek(i)
            image.save(f"{output_dir}/image_{i}.png")


if __name__ == '__main__':
    main()
