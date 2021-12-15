
import os
import sys
import io
import re
import json
import configparser

from google.cloud import vision
from configparser import ConfigParser

from google.cloud.storage import blob

common_words = ['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its',
                'before', 'herself', 'had', 'should', 'only', 'under', 'ours', 'has',
                'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor',
                'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing',
                'some', 'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does',
                'above', 'between', 'we', 'who', 'were', 'here', 'hers', 'by',
                'about', 'against', 'own', 'into', 'yourself', 'down', 'your', 'from',
                'her', 'their', 'there', 'been', 'whom', 'too', 'themselves',
                'was', 'until', 'more', 'himself', 'that', 'but', 'with', 'than', 'those',
                'myself', 'these', 'will', 'below', 'can', 'theirs', 'and', 'then',
                'itself', 'have', 'any', 'again', 'when', 'same', 'how', 'other', 'which',
                'you', 'after', 'most', 'such', 'why', 'off', 'yours', 'the', 'having',
                'once', '&', '|', 'and/or', 'e.g']


class GVision():

    def __init__(self, config):
        configs = ConfigParser()
        configs.read(config)
        gauth_json = configs.get('gstorage', 'auth_json')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gauth_json
        self.gclient = vision.ImageAnnotatorClient()

    # def get_text(self, file_path):
    def get_text(self, jpeg_dict):
        out_words = ''
        # pathname = file_path.split('/')
        # filename = pathname[-1]
        pdf_words = ''
        for jpeg in jpeg_dict['jpegs']:
            with io.open(jpeg, 'rb') as image_file:
                content = image_file.read()

            image = vision.Image(content=content)
            response = self.gclient.text_detection(image=image)
            texts = response.text_annotations
            for text in texts:
                out_words += str(f'{text.description} ')
            pdf_words = pdf_words + self._merge_words(out_words)

        # remove the duplicates between files
        return(self._merge_words(pdf_words))

    def _merge_words(self, doc_txt):
        clean_doc = []
        final_words = ''
        doc_txt = doc_txt.replace('\n', ' ').replace(
            ',', '').replace('-', ' ').replace('’', '').lower()
        doc_txt = doc_txt.replace('“', '').replace('”', '').replace('"', '')

        for stopword in common_words:
            if stopword in doc_txt:
                stop_txt = f' {stopword} '  # must be a complete word
                doc_txt = doc_txt.replace(stop_txt, ' ')
        doc_txt = re.sub('\s\s+', ' ', doc_txt)
        doc_list = doc_txt.split(' ')
        doc_set = list(set(doc_list))

        for term in doc_set:
            term = term.rstrip()

            if term:
                if '(s)' in term:  # reason(s)
                    term = term.replace('(s)', '')
                # Run this twice to ensure we don't have strings like '.;' etc
                # Ends with
                special_char_trk = 3
                while special_char_trk != 0:
                    term = re.sub('[\', :, \., \;, \>, \), !, \?]$', '', term)
                    term = re.sub('^[\', \<, \(, \‘]', '', term)
                    special_char_trk -= 1

                if len(term) <= 2:
                    continue
                clean_doc.append(term)

        cleanwords = list(set(clean_doc))
        for hipword in cleanwords:
            final_words += f'{hipword} '

        return(final_words)
