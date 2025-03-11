import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.getcwd(), 'immigration-consultant-capstone'))


from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from models.user import User
from config.mongodb import user_collection
from auth.user_authentication import hash_password, decode_access_token
from auth.admin_api_validation import validate_admin_api_key
import dotenv
dotenv.load_dotenv()

router = APIRouter(prefix="/auth")

@router.post("/signup")
async def signup(user: User, request: Request, x_api_key: str = Depends(validate_admin_api_key)):
    if not x_api_key:
        return JSONResponse({'error': 'Invalid API Key'}, status_code=401)
    
    token = request.cookies.get('access_token')
    print(token)
    if not token:
        return JSONResponse({'error': 'Invalid Token'}, status_code=401)
    
    payload = decode_access_token(token)
    if not payload:
        return JSONResponse({'error': 'Invalid Token'}, status_code=401)
    
    if not payload["is_super_admin"]:
        return JSONResponse({'error': 'Unauthorized'}, status_code=401)
    
    try:
        user_dict = user.model_dump()
        if await user_collection.find_one({"username": user_dict["username"]}):
            return {"error": "User already exists"}
        if await user_collection.find_one({"email": user_dict["email"]}):
            return {"error": "Email already exists"}
        if await user_collection.find_one({"phone_number": user_dict["phone_number"]}):
            return {"error": "Phone number already exists"}
        
        hashed_password = hash_password(user_dict["password"])
        user_dict["hashed_password"] = hashed_password
        del user_dict["password"]
        
        await user_collection.insert_one(user_dict)
        return {"message": "User created successfully"}
    
    except Exception as e:
        return {"error": str(e)}