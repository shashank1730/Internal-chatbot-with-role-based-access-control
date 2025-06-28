from typing import Dict
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import requests
from app.services.rag_engine import get_rag_response
from fastapi.staticfiles import StaticFiles

        

app = FastAPI()
security = HTTPBasic()
app.mount("/files", StaticFiles(directory="resources/data"), name="files")

# Dummy user database
users_db: Dict[str, Dict[str, str]] = {
    "Tony": {"password": "password123", "role": "engineering"},
    "Bruce": {"password": "securepass", "role": "marketing"},
    "Sam": {"password": "financepass", "role": "finance"},
    "Peter": {"password": "pete123", "role": "engineering"},
    "Sid": {"password": "sidpass123", "role": "marketing"},
    "Natasha": {"password": "hrpass123", "role": "hr"},
    "Shashank":{"password":"password123", "role" : "C-Level Executives"}
}


# Authentication dependency
def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    password = credentials.password
    user = users_db.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"username": username, "role": user["role"]}


# Login endpoint
@app.get("/login")
def login(user=Depends(authenticate)):
    return {"user": user['username'], "role": user["role"]}


# Protected test endpoint
@app.get("/test")
def test(user=Depends(authenticate)):
    return {"message": f"Hello {user['username']}! You can now chat.", "role": user["role"]}




# Payload for chat
class ChatPayload(BaseModel):
    message: str
    role: str

# Chat endpoint
@app.post("/chat")
def chat(payload: ChatPayload, user=Depends(authenticate)):
    print(f"[INFO] Authenticated user: {user['username']} | Role: {payload.role}")
    answer, sources = get_rag_response(payload.message, payload.role)
    return {"response": answer, "sources" : sources}