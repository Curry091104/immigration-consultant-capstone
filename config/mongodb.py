import dotenv
import os
from pymongo import MongoClient

dotenv.load_dotenv()

def connect():
    MONGO_URI = os.getenv('MONGO_URI')
    client = MongoClient(MONGO_URI)
    db = client['immigration-db']
    return db

def close(db):
    db.client.close()