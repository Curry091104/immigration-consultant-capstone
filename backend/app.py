from fastapi import FastAPI, HTTPException
from config.mongodb import connect, close

app = FastAPI()

mongo_client = None
db = None

@app.on_event("startup")
async def startup_event():
    global mongo_client, db
    mongo_client = connect()
    db = mongo_client
    
@app.on_event("shutdown")
async def shutdown_event():
    close(mongo_client)

@app.get("/")
def health_check():
    if db is not None:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=500, detail="Database connection is not established")