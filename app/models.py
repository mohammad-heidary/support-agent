### app/models.py
from pydantic import BaseModel, EmailStr, field_validator, Field
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
    email: EmailStr
    password: str
   
    @field_validator('email') 
    @classmethod 
    def validate_email_domain(cls, v): 
        """
        Validates that the email domain is example.com.
        Modify the domain list as needed.
        """
        allowed_domains = ["gmail.com", "email.com"]
        # Change: Error checking if email is empty
        if not v: 
            raise ValueError('Email is required')
        domain = v.split('@')[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f'فقط ایمیل‌های با دامنه‌های {", ".join(allowed_domains)} مجاز هستند.')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    @field_validator('email')
    @classmethod 
    def validate_email_domain(cls, v):
         if not v:
             raise ValueError('Email is required')
         allowed_domains = ["gmail.com", "email.com"]
         domain = v.split('@')[-1].lower()
         if domain not in allowed_domains:
             raise ValueError(f'فقط ایمیل‌های با دامنه‌های {", ".join(allowed_domains)} مجاز هستند.')
         return v
    
# --- Input Models for Agent Tools ---
# These models define the structure of arguments each tool expects.

class SearchInput(BaseModel):
    """Input schema for general search tools."""
    query: str = Field(description="کلمات کلیدی برای جستجو")

class TrainScheduleSearchInput(BaseModel):
    """Input schema for train schedule search."""
    origin: str = Field(description="نام شهر مبدا (مثلاً تهران)")
    destination: str = Field(description="نام شهر مقصد (مثلاً مشهد)")
    date: str = Field(description="تاریخ سفر (مثلاً 1403/05/10)")

class FlightScheduleSearchInput(BaseModel):
    """Input schema for domestic flight search."""
    origin: str = Field(description="نام شهر مبدا (مثلاً تهران)")
    destination: str = Field(description="نام شهر مقصد (مثلاً مشهد)")
    date: str = Field(description="تاریخ سفر (مثلاً 1403/05/10)")

class HotelSearchInput(BaseModel):
    """Input schema for hotel search."""
    city: str = Field(description="نام شهر یا منطقه برای جستجوی هتل")
    checkin_date: str = Field(description="تاریخ ورود (مثلاً 1403/05/10)")
    checkout_date: str = Field(description="تاریخ خروج (مثلاً 1403/05/12)")

class VillaSearchInput(BaseModel):
    """Input schema for villa/accommodation search."""
    city: str = Field(description="نام شهر یا منطقه برای جستجوی اقامتگاه")
    checkin_date: str = Field(description="تاریخ ورود (مثلاً 1403/05/10)")
    checkout_date: str = Field(description="تاریخ خروج (مثلاً 1403/05/12)")

class FAQSearchInput(BaseModel):
    """Input schema for FAQ search."""
    question: str = Field(description="سوالی که کاربر داره")
