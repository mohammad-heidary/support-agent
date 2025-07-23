### app/database.py
from collections import defaultdict

# In-memory database mockup for now
db = defaultdict(list)

def save_message(session_id: str, role: str, content: str):
    db[session_id].append({"role": role, "content": content})

def get_history(session_id: str):
    return db.get(session_id, [])
