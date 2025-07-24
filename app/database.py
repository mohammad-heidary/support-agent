### app/database.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME")

# Initialize MongoDB client and database
try:
    client = MongoClient('localhost',27017, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping') 
    print("✅ Connected to MongoDB successfully!")
    
    db = client[MONGO_DB_NAME]
    chat_sessions_collection = db[MONGO_COLLECTION_NAME]
    
    db_list = client.list_database_names()
    if MONGO_DB_NAME in db_list:
         print(f"✅ Database '{MONGO_DB_NAME}' exists.")
    else:
         print(f"ℹ️  Database '{MONGO_DB_NAME}' will be created on first use.")

    col_list = db.list_collection_names() 
    if MONGO_COLLECTION_NAME in col_list:
         print(f"✅ Collection '{MONGO_COLLECTION_NAME}' exists.")
    else:
         print(f"ℹ️  Collection '{MONGO_COLLECTION_NAME}' will be created on first use.")

except Exception as e:
    print(f"❌ Error connecting to MongoDB: {e}")
    raise e 


def save_message(session_id: str, role: str, content: str):
    """
Storing a message in MongoDB.
Each message is a dictionary with role and content.
All messages for a session_id are stored in a document.
    """
    try:
# Method : One document per session. Messages in an array inside the document.
# $push: Adds the new message to the 'messages' array.
        result = chat_sessions_collection.update_one(
            {"session_id": session_id}, # Filter: Find document with session_id
            {
                "$push": {"messages": {"role": role, "content": content}},
                "$setOnInsert": {"session_id": session_id} # If the document does not exist, create the session_id as well
            },
            upsert=True # If document not found, create one
        )
        #    print(f"💾 Message saved for session {session_id}. Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_id}")
    except Exception as e:
        print(f"❗ Error saving message to MongoDB for session {session_id}: {e}")

def get_history(session_id: str) -> list:
    """
    Get chat history of a session from MongoDB.
    """
    try:
        # Find document by session_id
        document = chat_sessions_collection.find_one({"session_id": session_id})
        if document and "messages" in document:
           # Return the list of messages
            return document["messages"]
        else:
           # If the document or array of messages does not exist, return an empty list
            return []
    except Exception as e:
        print(f"❗ Error retrieving history from MongoDB for session {session_id}: {e}")
        return [] 
