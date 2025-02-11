import os
import csv

class DecisionAgent:
    def __init__(self):
        self.path = os.path.dirname(os.path.abspath("__file__"))
        self.dataset = ['Visa.csv', 'SP.csv', 'PGWP.csv', 'CRS.csv']
        self.classes = {0:"Visa", 1:"Study Permit", 2:"PGWP", 3:"CRS"}
        self.keywords_data = {}
        #Load keywords from each file and store them in a dictionary
        #for file in self.dataset:
        for index, file in enumerate(self.dataset):
            file = os.path.join(self.path, 'utils', file)
            if os.path.exists(file):
                class_name = self.classes[index]
                self.keywords_data[class_name] = self.load_keywords(file)
            else:
                print(f"File {file} not found.")
                
    def load_keywords(self, file_path):
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            keywords = [row[0] for row in reader]
        return keywords
    
    def count(self, question_tokens, keywords):
        num=0
        for token in question_tokens:
            if token in keywords:
                num += 1
        return num
    
    #Define a function to classify a user question based on keyword matching
    def classify_question(self, question):
        question_words = set(question.lower().split())
        predicted_class_name = "Unknown"
        num=-1
        for class_name, keywords in self.keywords_data.items():
            n_num = self.count(question_words, keywords)
            if n_num > num:
                predicted_class_name = class_name
                num= n_num
        return predicted_class_name
    
    def is_the_query_related_to_study_permit_pgwp_or_visa(self, question):
        question_words = set(question.lower().split())
        predicted_class_name = "Unknown" # Find questions that may get Unknown category
        num=-1
        for class_name, keywords in self.keywords_data.items():
            n_num = self.count(question_words, keywords)
            if n_num > num:
                predicted_class_name = class_name
                num= n_num
        class_idx = (list(self.classes.keys())[list(self.classes.values()).index(predicted_class_name)])
        return predicted_class_name, class_idx<=2



# ## TESTING THE DECISION AGENT ###
# question = "How to apply for it?"   
# da = DecisionAgent()
# answer = da.is_the_query_related_to_study_permit_pgwp_or_visa(question)
# print(f'Is the query related to "study permit", "pgwp" or "visa"? {answer}')