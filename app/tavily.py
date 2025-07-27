# app.tavily.py
from langchain_tavily import TavilySearch
import os
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(".env")

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    logger.error("TAVILY_API_KEY environment variable is not set.")
    # Consider raising an exception or handling the error gracefully

# Initialize the Tavily tool for web searches

tavily_tool = TavilySearch(max_results=3, tavily_api_key=tavily_api_key, topic="general")

# --- General Search Tools for Alibaba.ir Sections ---
# These tools use Tavily to search within specific subdomains or sections of alibaba.ir

# Change: We define functions separately (for use in StructuredTool)
def search_alibaba_general_func(query: str) -> str:
    """Search for information across the main sections of alibaba.ir."""
    search_query = f"site:alibaba.ir {query}"
    # Change: How to call tavily_tool
    response = tavily_tool.invoke({"query": search_query})

    logger.info(f"🔍 [Tavily] search_alibaba_general_func invoked with query='{query}'")

    # Checking the output structure and extracting results
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        # Convert the results to a string
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]]) # For example, the first 3
    else:
        # If the structure is different, return a default
        return str(response)

def search_alibaba_faqs(query: str, category: str = "") -> str:
    """
    جستجوی سوالات متداول (FAQs) در علی‌بابا با استفاده از Tavily.
    Search for FAQs on alibaba.ir/help-center/categories/faq using Tavily.
    
    Args:
        query: سوال کاربر.
        category: دسته‌ی مورد نظر (مثلاً "train", "hotel", "flight-domestic"). 
                  اگه خالی باشه، جستجو تو کل FAQ انجام می‌شه.
    """
    # ساخت search_query بر اساس دسته
    if category:
        # اگه دسته مشخص شده، جستجو فقط تو اون زیرمجموعه
        search_query = f"site:alibaba.ir/help-center/categories/faq/{category} {query}"
    else:
        # اگه دسته خالی هست، جستجو تو کل بخش FAQ
        search_query = f"site:alibaba.ir/help-center/categories/faq {query}"
    
    try:
        response = tavily_tool.invoke({"query": search_query})
        logger.info(f"🔍 [Tavily] search_alibaba_faqs invoked with query='{query}', category='{category}'")
        
        # فرمت‌بندی نتایج
        if isinstance(response, dict) and 'results' in response:
            results = response['results']
            if not results:
                 # پیام مناسب‌تری بر اساس دسته
                 category_msg = f" در دسته '{category}'" if category else ""
                 return f"سوالی مشابه '{query}'{category_msg} در بخش سوالات متداول پیدا نکردم."
            
            info_lines = [f"❓ نتایج جستجو در سوالات متداول علی‌بابا برای '{query}':"]
            for res in results[:3]: # فقط 3 تا اولی
                title = res.get('title', 'بدون عنوان')
                url = res.get('url', '#')
                snippet = res.get('content', 'بدون خلاصه')
                info_lines.append(f"- [{title}]({url})\n  {snippet}\n")
            return "\n".join(info_lines)
        else:
            return f"خطا در دریافت نتایج جستجو برای سوال '{query}'."
    except Exception as e:
        logger.error(f"Error in search_alibaba_faqs: {e}")
        return f"❌ خطایی در جستجوی سوالات متداول رخ داد: {str(e)}"

def search_alibaba_magazine_func(query: str) -> str:
    """Search for articles and information in the Alibaba Magazine."""
    search_query = f"site:alibaba.ir/mag {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_magazine_func invoked with query='{query}'")
    
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

# --- Specific Section Search Tools ---
def search_alibaba_profile_func(query: str) -> str:
    """Search for information about profile(پروفایل)"""
    search_query = f"site:alibaba.ir/profile {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_profile_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_flights_iran_func(query: str) -> str:
    """Search for information about domestic flights (پرواز داخلی) on alibaba.ir."""
    search_query = f"site:alibaba.ir {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_flights_iran_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_flights_international_func(query: str) -> str:
    """Search for information about international flights (پرواز خارجی) on alibaba.ir/iranout."""
    search_query = f"site:alibaba.ir/iranout {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_flights_international_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_trains_func(query: str) -> str:
    """Search for information about train tickets (قطار) on alibaba.ir."""
    search_query = f"site:alibaba.ir/train-ticket {query}"
    logger.info(f"🔍 [Tavily] search_alibaba_trains_func invoked with query='{query}'")
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_buses_func(query: str) -> str:
    """Search for information about bus tickets (اتوبوس) on alibaba.ir."""
    search_query = f"site:alibaba.ir/bus-ticket {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_buses_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_tours_func(query: str) -> str:
    """Search for information about tours (تور) on alibaba.ir."""
    search_query = f"site:alibaba.ir/tour {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_tours_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_hotels_func(query: str) -> str:
    """Search for information about hotels (هتل) on alibaba.ir."""
    search_query = f"site:alibaba.ir/hotel {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_hotels_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_accommodations_func(query: str) -> str:
    """Search for information about villas and accommodations (ویلا و اقمتگاه) on alibaba.ir."""
    search_query = f"site:alibaba.ir/accommodation {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_accommodations_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_visa_func(query: str) -> str:
    """Search for information about visas (ویزا) on alibaba.ir."""
    search_query = f"site:alibaba.ir/visa {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_visa_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_insurance_func(query: str) -> str:
    """Search for information about travel insurance (بیمه مسافرتی) on alibaba.ir."""
    search_query = f"site:alibaba.ir/insurance {query}"
    response = tavily_tool.invoke({"query": search_query})
    logger.info(f"🔍 [Tavily] search_alibaba_insurance_func invoked with query='{query}'")
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)
    
