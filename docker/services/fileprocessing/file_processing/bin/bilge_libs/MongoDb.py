

import os
import sys
import io
import re
import json
import pymongo

from configparser import ConfigParser


class mongo_client():

    def __init__(self, config):
        configs = ConfigParser()
        configs.read(config)
        mongo_host = configs.get('mongo', 'mongo_host')
        mongo_port = str(configs.get('mongo', 'mongo_port'))
        mongo_user = configs.get('mongo', 'auth_user')
        mongo_cred = configs.get('mongo', 'auth_cred')
        mongo_db = configs.get('mongo', 'bilge_db')
        #mongo_col = configs.get('mongo', 'test_collection')

        mongo_auth_str = f'default_db?authSource={mongo_db}'
        mongo_url = f'mongodb://{mongo_user}:{mongo_cred}@{mongo_host}:{mongo_port}/{mongo_auth_str}'

        mymongo = pymongo.MongoClient(mongo_url)
        self.bilge_db = mymongo[mongo_db]
        #self.bilge_db.collection.create_index( [("file_words", pymongo.DESCENDING)])
        #self.bilge_db.collection.create_index([("file_words", pymongo.TEXT)])
        # print(f'->{self.bilge_db.list_collection_names()}<-')
        #print(self.bilge_db.authenticate(mongo_user, mongo_cred))
        #print(self.bilge_db.authenticate(mongo_user, mongo_cred))

    def insert_pdf(self, mongo_collection, pdf_detail_dict):
        if not isinstance(pdf_detail_dict, dict):
            raise TypeError('PDF details are not a dict')

        my_collection = self.bilge_db[mongo_collection]
        insert_cmd = my_collection.insert_one(pdf_detail_dict)
        return insert_cmd

    def file_search(self, mongo_collection, file_name):
        my_collection = self.bilge_db[mongo_collection]
        search_dict = {"file_name": file_name}

        file_results = my_collection.count_documents(search_dict)

        if file_results == 0:
            return False
        else:
            return True
