#!/usr/bin/env python
import os
import sys
import json
import concurrent.futures

from glob import glob
from bilge_libs.GStorage import GStorage
from bilge_libs.GVision import GVision  # enable GCP Api
from bilge_libs.ConvertPdf import convertpdf
from bilge_libs.MongoDb import mongo_client
from configparser import ConfigParser
from threading import Thread


# Convert
bilge_root = '/file_processing'
bilge_config = os.path.join(bilge_root, 'conf', 'access.conf')
pdf_json = os.path.join(bilge_root, 'conf', 'pdf_folders.json')
bilge_wip = os.path.join(bilge_root, 'wip')

# GCP Storage
gbuckets = GStorage(bilge_config)
# Gcp Vision
gvision = GVision(bilge_config)
# Mongo
mymongo = mongo_client(bilge_config)


def process_pdf(pdf, upload_bucket, bilge_folder):

    converter = convertpdf(bilge_folder, bilge_wip)
    pdf_path_chain = pdf.split('/')
    pdf_filename = pdf_path_chain[-1]

    # Skip that file its been processed already
    if mymongo.file_search(upload_bucket, pdf_filename):
        print(f'Skipping file {pdf}')
        return None

    print(f'working on {pdf}')

    pdf_details = {
        'bucket': upload_bucket,
        'file_name': pdf_filename,
        'local_path': str(pdf),
        'gcp_path': f'{upload_bucket}/{pdf_filename}',
        'file_timestamp': int(os.path.getmtime(pdf))
    }

    # Returns list [jpg_file, pages, md5]
    converted_jpg = converter.process_pdf(pdf)

    # Send to vision to get words
    pdf_details['file_words'] = gvision.get_text(converted_jpg)
    pdf_details['md5'] = converted_jpg['md5']
    pdf_details['pages'] = converted_jpg['pages']

    # Send pdf to bucket
    #gbuckets.gs_upload(upload_bucket, pdf)

    converter.jpeg_cleanup(pdf)
    #print(json.dumps(pdf_details, indent=2, sort_keys=True))

    # Insert into Mongo
    mymongo.insert_pdf(upload_bucket, pdf_details)
    converter.clean_all()


def process_folder(bilge_folder):
    bucket_prefix = 'bilge_'

    fullpathlist = bilge_folder.split('/')
    folder_name = fullpathlist[-1]

    # Gather all the pdf's
    pdfs = glob(bilge_folder + '/*.pdf')
    upload_bucket = bucket_prefix + folder_name

    # Make sure bucket exists
    if gbuckets.gs_checkbucket(upload_bucket) == False:
        print('Creating bucket: ' + upload_bucket)
        gbuckets.gs_createbucket(upload_bucket)

    with concurrent.futures.ThreadPoolExecutor() as pdf_ex:
        for pdf in pdfs:
            pdf_ex.submit(process_pdf(pdf, upload_bucket, bilge_folder))


def main(pdf_folders):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(process_folder, pdf_folders)


if __name__ == '__main__':
    f = open(pdf_json)
    pdf_vaults = json.load(f)
    main(pdf_vaults['pdf_folders'])
