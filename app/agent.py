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
from app.soup import scrape_main_page_info, scrape_hotel_page_info
from app.playwright import (
    scrape_flight_schedules, 
    scrape_train_schedules,
    scrape_hotel_info, 
    scrape_villa_info
)
from app.tavily import (
    search_alibaba_general_func,
    search_alibaba_faqs,
    search_alibaba_magazine_func,
    search_alibaba_profile_func,
    search_alibaba_flights_iran_func,
    search_alibaba_flights_international_func,
    search_alibaba_trains_func,
    search_alibaba_buses_func, 
    search_alibaba_tours_func, 
    search_alibaba_hotels_func, 
    search_alibaba_accommodations_func,
    search_alibaba_visa_func, 
    search_alibaba_insurance_func
)

# Load environment variables
# Load environment variables
load_dotenv("./app/.env")

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
        description="جستجو برای پیدا کردن پاسخ سوالات متداول در علی‌بابا.",
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
    StructuredTool.from_function(
        name="search_alibaba_flights_domestic",
        description="جستجوی اطلاعات کلی درباره پروازهای داخلی علی‌بابا.",
        func=search_alibaba_flights_iran_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_flights_international",
        description="جستجوی اطلاعات کلی درباره پروازهای خارجی علی‌بابا.",
        func=search_alibaba_flights_international_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_trains",
        description="جستجوی اطلاعات کلی درباره بلیط قطار علی‌بابا.",
        func=search_alibaba_trains_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_buses",
        description="جستجوی اطلاعات کلی درباره بلیط اتوبوس علی‌بابا.",
        func=search_alibaba_buses_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_tours",
        description="جستجوی اطلاعات کلی درباره تورهای علی‌بابا.",
        func=search_alibaba_tours_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_hotels_general",
        description="جستجوی اطلاعات کلی درباره هتل‌های علی‌بابا.",
        func=search_alibaba_hotels_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_accommodations_general",
        description="جستجوی اطلاعات کلی درباره ویلا و اقامتگاه‌های علی‌بابا.",
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

    # --- BeautifulSoup Scraping Tools ---
    StructuredTool.from_function(
        name="scrape_alibaba_main_page",
        description="دریافت اطلاعات کلی از صفحه اصلی علی‌بابا (https://www.alibaba.ir/). شامل خدمات اصلی، لینک‌های پایین صفحه و مزایای سفر.",
        func=scrape_main_page_info,
        args_schema=SearchInput 
    ),
    StructuredTool.from_function(
        name="scrape_alibaba_hotel_page",
        description="دریافت اطلاعات از صفحه رزرو هتل علی‌بابا (https://www.alibaba.ir/hotel).",
        func=scrape_hotel_page_info,
        args_schema=SearchInput 
    ),

    # --- Playwright Interactive Scraping Tools ---
    StructuredTool.from_function(
        name="search_alibaba_flight_schedules",
        description="جستجوی دقیق و تعاملی بلیط هواپیمای داخلی بین دو شهر در تاریخ مشخص در علی‌بابا.",
        func=scrape_flight_schedules,
        args_schema=FlightScheduleSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_train_schedules",
        description="جستجوی دقیق و تعاملی زمانبندی و قیمت قطارها بین دو شهر در تاریخ مشخص در علی‌بابا.",
        func=scrape_train_schedules,
        args_schema=TrainScheduleSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_hotel_info",
        description="جستجوی تعاملی اطلاعات هتل در یک شهر و بازه زمانی مشخص در علی‌بابا.",
        func=scrape_hotel_info,
        args_schema=HotelSearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_villa_info",
        description="جستجوی تعاملی اطلاعات ویلا/اقامتگاه در یک شهر و بازه زمانی مشخص در علی‌بابا.",
        func=scrape_villa_info,
        args_schema=VillaSearchInput
    ),
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
You have access to various tools to provide the most accurate and up-to-date information.
Always respond in natural Persian (Farsi). Do NOT show code unless asked.

Available tools:
- search_alibaba_general: جستجوی عمومی در کل سایت علی‌بابا.
- search_alibaba_faqs: جستجو برای پیدا کردن پاسخ سوالات متداول.
- search_alibaba_magazine: جستجو در مجله علی‌بابا.
- search_alibaba_profile: جستجو در بخش پروفایل کاربری.
- search_alibaba_flights_domestic: جستجوی اطلاعات کلی پروازهای داخلی.
- search_alibaba_flights_international: جستجوی اطلاعات کلی پروازهای خارجی.
- search_alibaba_trains: جستجوی اطلاعات کلی قطارها.
- search_alibaba_buses: جستجوی اطلاعات کلی اتوبوس‌ها.
- search_alibaba_tours: جستجوی اطلاعات کلی تورها.
- search_alibaba_hotels_general: جستجوی اطلاعات کلی هتل‌ها.
- search_alibaba_accommodations_general: جستجوی اطلاعات کلی ویلا و اقامتگاه‌ها.
- search_alibaba_visa: جستجوی اطلاعات کلی ویزا.
- search_alibaba_insurance: جستجوی اطلاعات کلی بیمه مسافرتی.
- scrape_alibaba_main_page: دریافت اطلاعات کلی از صفحه اصلی.
- scrape_alibaba_hotel_page: دریافت اطلاعات از صفحه هتل.
- search_alibaba_flight_schedules: جستجوی دقیق بلیط هواپیمای داخلی.
- search_alibaba_train_schedules: جستجوی دقیق زمانبندی و قیمت قطارها.
- search_alibaba_hotel_info: جستجوی تعاملی اطلاعات هتل.
- search_alibaba_villa_info: جستجوی تعاملی اطلاعات ویلا/اقامتگاه.
""")
    return create_react_agent(llm, tools=tools)
