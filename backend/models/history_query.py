from typing import List
from pydantic import BaseModel
from datetime import datetime

class HistoryQueries(BaseModel):
    username: str
    message: List[str]
    timestamp: datetime