#!/usr/bin/env python
import os
import sys
import subprocess
import json
from glob import glob
from time import sleep
from copy import deepcopy
from mimetypes import MimeTypes


# pdftoppm makes several files, input is in wip, output goes to wip
# Convert reads in all of the files and merges them into a single file
# pdftoppm -jpeg -r 300 ../cache/20210318_marie_152104.pdf ../wip/20210318_marie_152104

# Merge convert -append ../wip/20210318_marie_152104-[123].jpg 20210318_marie_152104.jpg

class convertpdf():
    def __init__(self, in_dir, out_dir):
        self.mime = MimeTypes()
        self.cache_dir = in_dir
        self.wip_dir = out_dir
        self.pdf_cmd = '/usr/bin/pdftoppm'
        #self.merge_cmd = '/usr/bin/convert'

    def process_pdf(self, pdf_file):

        jpeg_pdf_details = {}
        cache_pathfile = os.path.join(self.cache_dir, pdf_file)
        file_root = os.path.basename(pdf_file)
        jpeg_out = os.path.join(self.wip_dir, file_root)

        file_hash = self._get_md5(pdf_file)

        if os.path.isfile(jpeg_out):
            os.remove(jpeg_out)

        if not os.path.isfile(cache_pathfile):
            return("Error: Can't find PDF File")

        get_mime = self.mime.guess_type(cache_pathfile)
        if get_mime[0] != 'application/pdf':
            print(self.mime.guess_type(cache_pathfile))
            return('Error: may not be a valid pdf')

        pdfppm = subprocess.run([self.pdf_cmd, '-jpeg', '-r', '300', cache_pathfile, jpeg_out],
                                capture_output=True, check=True)
        print('Waiting for files to write')
        sleep(5)

        # find all of the assocated jpg files
        jpegs = glob(jpeg_out + '*.jpg')
        pages = len(jpegs)
        jpegs.sort()
        jpeg_pdf_details = {'pdf': pdf_file,
                            'pages': pages,
                            'jpegs': jpegs,
                            'md5': file_hash
                            }

        return(jpeg_pdf_details)

    def jpeg_cleanup(self, clean_pdf):
        '''Remove the jpegs we don't need them anymore'''
        file_name = os.path.basename(clean_pdf)
        clean_path = os.path.join(self.wip_dir, file_name)
        clean_path = clean_path.replace('.pdf', '*.jpg')
        cleanup = glob(clean_path)
        for x in cleanup:
            os.remove(x)

    def clean_all(self):
        '''Remove all jpegs'''
        old_jpegs = glob(self.wip_dir + '*.jpg')
        for y in old_jpegs:
            os.remove(y)

    def _get_md5(self, filetohash):
        hash_cmd = subprocess.run(
            ['/usr/bin/md5sum', filetohash], text=True, capture_output=True, check=True)
        hash_data = hash_cmd.stdout
        md5_details = hash_data.split('  ')
        return(md5_details[0])
