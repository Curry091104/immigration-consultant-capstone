from typing import Optional
from pydantic import BaseModel
from enum import Enum

    
class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    email: str
    phone_number: Optional[str] = None