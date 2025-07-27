# app/agents.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
import os
from dotenv import load_dotenv

# Import input models
from app.models import (
    SearchInput, 
    TrainScheduleSearchInput, 
    FlightScheduleSearchInput, 
    HotelSearchInput, 
    VillaSearchInput,
    FAQSearchInput
)

# Import tools from different modules
from app.playwright import (
    search_alibaba_flight_schedules, 
    search_alibaba_train_schedules,
    search_alibaba_hotel_info, 
    search_alibaba_villa_info,
    search_alibaba_faqs_interactive,
    search_alibaba_tour_info,
    search_alibaba_bus_schedules
)
# Import remaining Tavily tools
from app.tavily import (
    search_alibaba_general_func,
    search_alibaba_faqs,
    search_alibaba_magazine_func,
    search_alibaba_profile_func,
    search_alibaba_flights_iran_func,      # Added: For domestic flights (Tavily)
    search_alibaba_flights_international_func, # Added: For international flights (Tavily)
    search_alibaba_trains_func,            # Added: For train info (Tavily)
    search_alibaba_buses_func,             # Added: For bus info (Tavily)
    search_alibaba_tours_func,             # Added: For tour info (Tavily)
    search_alibaba_hotels_func,            # Added: For hotel info (Tavily)
    search_alibaba_accommodations_func,    # Added: For accommodation info (Tavily)
    search_alibaba_visa_func, 
    search_alibaba_insurance_func
)

# Load environment variables
load_dotenv(".env")

# Access API keys
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENROUTER_API_BASE")

# --- Define the list of tools available to the agent ---
tools = [
    # --- Tavily Search Tools (General & Specific Sections) ---
    StructuredTool.from_function(
        name="search_alibaba_general",
        description="جستجوی عمومی در کل سایت علی‌بابا برای اطلاعات کلی.",
        func=search_alibaba_general_func,
        args_schema=SearchInput
    ),
   StructuredTool.from_function(
        name="search_alibaba_faqs",
        description="جستجو برای پیدا کردن پاسخ سوالات متداول در علی‌بابا. وقتی سوالی درباره قوانین، راهنما، استرداد یا هر چیز دیگه‌ای که ممکنه تو FAQ باشه می‌پرسن، از این ابزار استفاده کن.",
        func=search_alibaba_faqs,
        args_schema=FAQSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_magazine",
        description="جستجو در مجله علی‌بابا برای مقالات و راهنماها.",
        func=search_alibaba_magazine_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_profile",
        description="جستجو در بخش پروفایل کاربری علی‌بابا.",
        func=search_alibaba_profile_func,
        args_schema=SearchInput
    ),
    # --- Tavily Tools for Specific Services (as fallback or for general info) ---
    StructuredTool.from_function(
        name="search_alibaba_flights_domestic",
        description="جستجوی اطلاعات کلی درباره پروازهای داخلی علی‌بابا (با Tavily).",
        func=search_alibaba_flights_iran_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_flights_international",
        description="جستجوی اطلاعات کلی درباره پروازهای خارجی علی‌بابا (با Tavily).",
        func=search_alibaba_flights_international_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_trains",
        description="جستجوی اطلاعات کلی درباره بلیط قطار علی‌بابا (با Tavily).",
        func=search_alibaba_trains_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_buses",
        description="جستجوی اطلاعات کلی درباره بلیط اتوبوس علی‌بابا (با Tavily).",
        func=search_alibaba_buses_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_tours",
        description="جستجوی اطلاعات کلی درباره تورهای علی‌بابا (با Tavily).",
        func=search_alibaba_tours_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_hotels_general",
        description="جستجوی اطلاعات کلی درباره هتل‌های علی‌بابا (با Tavily).",
        func=search_alibaba_hotels_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_accommodations_general",
        description="جستجوی اطلاعات کلی درباره ویلا و اقامتگاه‌های علی‌بابا (با Tavily).",
        func=search_alibaba_accommodations_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_visa",
        description="جستجوی اطلاعات کلی درباره ویزای علی‌بابا.",
        func=search_alibaba_visa_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_insurance",
        description="جستجوی اطلاعات کلی درباره بیمه مسافرتی علی‌بابا.",
        func=search_alibaba_insurance_func,
        args_schema=SearchInput
    ),

    # --- Playwright Interactive Scraping Tools ---
    StructuredTool.from_function(
        name="search_alibaba_flight_schedules",
        description="جستجوی دقیق و تعاملی بلیط هواپیمای داخلی بین دو شهر در تاریخ مشخص در علی‌بابا.",
        func=search_alibaba_flight_schedules,
        args_schema=FlightScheduleSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_train_schedules",
        description="جستجوی دقیق و تعاملی زمانبندی و قیمت قطارها بین دو شهر در تاریخ مشخص در علی‌بابا.",
        func=search_alibaba_train_schedules,
        args_schema=TrainScheduleSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_bus_schedules",
        description="جستجوی دقیق و تعاملی زمانبندی و قیمت اتوبوس‌ها بین دو شهر در تاریخ مشخص در علی‌بابا.",
        func=search_alibaba_bus_schedules,
        args_schema=TrainScheduleSearchInput # Reusing input schema for simplicity, could create a specific one
    ),
    StructuredTool.from_function(
        name="search_alibaba_tour_info",
        description="جستجوی تعاملی اطلاعات تورها در علی‌بابا با مبدا، مقصد و بازه زمانی.",
        func=search_alibaba_tour_info,
        args_schema=HotelSearchInput # Reusing input schema, adjust if a specific tour schema is created
    ),
    StructuredTool.from_function(
        name="search_alibaba_hotel_info",
        description="جستجوی تعاملی اطلاعات هتل در یک شهر و بازه زمانی مشخص در علی‌بابا.",
        func=search_alibaba_hotel_info,
        args_schema=HotelSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_villa_info",
        description="جستجوی تعاملی اطلاعات ویلا/اقامتگاه در یک شهر و بازه زمانی مشخص در علی‌بابا.",
        func=search_alibaba_villa_info,
        args_schema=VillaSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_faqs_interactive",
        description="جستجوی تعاملی و دقیق در بخش پرسش‌های متداول علی‌بابا.",
        func=search_alibaba_faqs_interactive,
        args_schema=FAQSearchInput
    )
]

def get_agent(model_name: str):
    """ساخت و بازگشت یک ایجنت پیکربندی شده.
    Create and return a configured agent.
    """
    llm = ChatOpenAI(
        model_name=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        temperature=0.7,
        max_tokens=4096,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1
    )
    # Configure the system message for the agent
    llm = llm.with_config(system_message="""
You are a smart and friendly assistant named SupportBot.
You help users find information specifically about services and policies on alibaba.ir.
You have access to various tools to provide the most accurate and up-to-date information. Your priority is to use playwright tools.
Always respond in natural Persian (Farsi). Do NOT show code unless asked.

Available tools:
- search_alibaba_general: جستجوی عمومی در کل سایت علی‌بابا.
- search_alibaba_faqs: جستجو برای پیدا کردن پاسخ سوالات متداول (روش Tavily).
- search_alibaba_magazine: جستجو در مجله علی‌بابا.
- search_alibaba_profile: جستجو در بخش پروفایل کاربری.
- search_alibaba_flights_domestic: جستجوی اطلاعات کلی پروازهای داخلی (Tavily).
- search_alibaba_flights_international: جستجوی اطلاعات کلی پروازهای خارجی (Tavily).
- search_alibaba_trains: جستجوی اطلاعات کلی قطارها (Tavily).
- search_alibaba_buses: جستجوی اطلاعات کلی اتوبوس‌ها (Tavily).
- search_alibaba_tours: جستجوی اطلاعات کلی تورها (Tavily).
- search_alibaba_hotels_general: جستجوی اطلاعات کلی هتل‌ها (Tavily).
- search_alibaba_accommodations_general: جستجوی اطلاعات کلی ویلا و اقامتگاه‌ها (Tavily).
- search_alibaba_visa: جستجوی اطلاعات کلی ویزا.
- search_alibaba_insurance: جستجوی اطلاعات کلی بیمه مسافرتی.
- search_alibaba_flight_schedules: جستجوی دقیق بلیط هواپیمای داخلی (Playwright).
- search_alibaba_train_schedules: جستجوی دقیق زمانبندی و قیمت قطارها (Playwright).
- search_alibaba_bus_schedules: جستجوی دقیق زمانبندی و قیمت اتوبوس‌ها (Playwright).
- search_alibaba_tour_info: جستجوی تعاملی اطلاعات تورها (Playwright).
- search_alibaba_hotel_info: جستجوی تعاملی اطلاعات هتل (Playwright).
- search_alibaba_villa_info: جستجوی تعاملی اطلاعات ویلا/اقامتگاه (Playwright).
- search_alibaba_faqs_interactive: جستجوی تعاملی و دقیق در بخش پرسش‌های متداول (Playwright).
""")
    return create_react_agent(llm, tools=tools)
