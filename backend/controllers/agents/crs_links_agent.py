import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.crs_links import crs_links
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('punkt_tab')

class CRSLinksAgent:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def preprocess_input(self, user_input):
        tokens = word_tokenize(user_input.lower())
        filtered_tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
        return filtered_tokens

    def get_recommendations(self, user_input):
        process_input = self.preprocess_input(user_input)
        recommendation = {}
        for keyword in process_input:
            for item in crs_links['Comprehensive Ranking System (CRS)']:
                if keyword in item['keywords']:
                    recommendation[item['title']] = item['url']        
        return recommendation if recommendation else "No recommendations found"
