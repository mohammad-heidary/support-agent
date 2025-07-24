#app/chat_router.py
from fastapi import APIRouter, HTTPException
import traceback

from app.models import UserMessage
from app.database import save_message, get_history
from app.agent import get_agent

chat_router = APIRouter()
sessions = {}

#DEFAULT_MODEL = "mistralai/mistral-7b-instruct"
#DEFAULT_MODEL = "qwen/qwen2.5-72b-instruct"
#DEFAULT_MODEL = "mistralai/mistral-nemo"
DEFAULT_MODEL = "mistralai/mistral-small-3.2-24b-instruct"


WELCOME_MESSAGE = "سلام من علی مدد ام، چطور میتونم کمکتون کنم؟ 😊"

@chat_router.post("/send_message")
def send_message(message: UserMessage):
    session_id = message.session_id
    content = message.content

    
    # If the session does not exist, create it
    if session_id not in sessions:
        sessions[session_id] = {"agent": get_agent(DEFAULT_MODEL)}

    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=403, detail="Invalid or expired session_id.")

    # Save the user's message first
    save_message(session_id, "user", content) # We moved this line here because the model must first have a message from the user in addition to its own message for the history to work properly.

    
    # Get the history AFTER saving the user message
    history = get_history(session_id)

    # Check message count (now including the new user message)
    user_message_count = sum(1 for msg in history if msg["role"] == "user")
    if user_message_count > 20: # تغییر: از >= به > تغییر کرد
        # Optional: Remove the saved user message if limit is exceeded
        # This requires modifying save_message or adding a delete_message function
        # For now, we just return the error
        return {
            "response": "⚠️ You can only send 20 messages in this session. Please start a new session."}

    # Continue the usual process
    agent = session["agent"]

    # Make sure history is not empty and doesn't start with assistant message only
    # This check might be redundant now, but good to be sure.
    # The main fix is moving save_message before get_history.
    
    response = agent.invoke({"messages": history}) # Now history includes the user's latest message
    
    # print (f"⚠️ Raw response: {response}")
    try:
        ai_message = response["messages"][-1]
        output = ai_message.content
        # Save the AI's response
        save_message(session_id, "assistant", output)
    except Exception as e:
        traceback.print_exc()
        output = f"❗ Error processing response: {str(e)}"
        # Even if processing fails, the user message is already saved.
    return {"response": output}

@chat_router.get("/get_history/{session_id}")
def get_chat_history(session_id: str):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return get_history(session_id)
