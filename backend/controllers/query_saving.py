"""
This file contains the functions that are used to save the querries to build FAQs.
Any querries that are not matched with the existing FAQs are saved in the database.
"""
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.history_query import HistoryQuery
from config.mongodb import get_history_query_collection


async def save_query(query: HistoryQuery):
    """
    This function saves the query to the database.
    """
    try:
        history_query_collection = get_history_query_collection()
        query_dict = query.model_dump()
        # Check if the query is already in the database
        existing_query = await history_query_collection.find_one({"query": query_dict['query']})
        if existing_query:
            return existing_query
        new_history_query = await history_query_collection.insert_one(query_dict)
        created_query = await history_query_collection.find_one({"_id": new_history_query.inserted_id})
        return created_query
    
    except Exception as e:
        return {"error": str(e)}
    
    
#### Test the function ####
# if __name__ == "__main__":
#     import asyncio
    
#     query = HistoryQuery(
#         query = "How to apply for a study permit?",
#         timestamp="2022-10-10 10:10:10"
#     )
    
#     result = asyncio.run(save_query(query))
#     print(result)
    