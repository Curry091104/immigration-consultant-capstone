import sys
import os

sys.path.append(os.path.join(os.getcwd()))

from config.mypinecone import MyPinecone
import json

class FAQAgent:
    def __init__(self):
        self.pinecone = MyPinecone()
    
    def find_answer(self, query, index_name = "faqs", top_k=1, filter = None, include_values=False, include_metadata=True):
        found_doc = self.pinecone.search(index_name, query, top_k, filter, include_values, include_metadata)
        if found_doc.status_code == 200:
            output_search = json.loads(found_doc.body)
            matches = output_search['results']['matches']
            if matches[0]['score'] > 0.8:
                return matches[0].get('metadata')
            return query
        else:
            raise RuntimeError(json.loads(found_doc.body).get('message'))
    