#auth_reouter.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import uuid

from app.users_db import create_user, verify_user
from app.auth_utils import create_access_token, decode_token
from app.agent import get_agent
from app.chat_router import sessions, DEFAULT_MODEL, WELCOME_MESSAGE
from app.database import save_message
from app.models import SignUpRequest

auth_router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@auth_router.post("/signup")
def signup(signup_data: SignUpRequest):
    success = create_user(signup_data.email, signup_data.password)
    if not success:
        raise HTTPException(status_code=400, detail="User already exists")
    return {"msg": "User created"}

@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_user(form_data.username, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": form_data.username})
    
    # Create a default session for this user
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"agent": get_agent(DEFAULT_MODEL)}
    save_message(session_id, "assistant", WELCOME_MESSAGE)

    return {
        "access_token": token,
        "token_type": "bearer",
        "session_id": session_id,
        "welcome": WELCOME_MESSAGE
    }

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = decode_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
