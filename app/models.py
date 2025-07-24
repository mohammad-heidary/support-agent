### app/models.py
from pydantic import BaseModel, EmailStr, validator, Field
from typing import List, Optional, TypedDict

class Message(BaseModel):
    role: str  # 'user', 'assistant', 'system', etc.
    content: str

class ChatSession(BaseModel):
    session_id: str
    model_name: Optional[str]
    history: List[Message] = []

class UserMessage(BaseModel):
    session_id: str
    content: str

class ModelAction(BaseModel):
    action: str 
    model_name: str | None = None

# Define a request class for registration
class SignUpRequest(BaseModel):
    email: EmailStr # This line checks the email format
    password: str
   
    @validator('email')
    def validate_email_domain(cls, v):
         """
         Validates that the email domain is example.com.
         Modify the domain list as needed.
         """
         allowed_domains = ["gmail.com", "email.com"]
         domain = v.split('@')[-1].lower()
         if domain not in allowed_domains:
             raise ValueError(f'فقط ایمیل‌های با دامنه‌های {", ".join(allowed_domains)} مجاز هستند.')
         return v

# Define the input model for search tools (required for strict tools)
class SearchInput(BaseModel):
    query: str = Field(description="The search query string")