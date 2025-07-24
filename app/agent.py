# app/agents.py

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langchain_core.tools import StructuredTool
import requests 
import os
from dotenv import load_dotenv

from app.models import SearchInput

# Load environment variables from .env file
load_dotenv("./app/.env")

# Access the variables
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENROUTER_API_BASE")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# --- Alibaba.ir Tools ---

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
    # Checking the output structure and extracting results
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        # Convert the results to a string
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]]) # For example, the first 3
    else:
        # If the structure is different, return a default
        return str(response)

def search_alibaba_help_center_func(query: str) -> str:
    """Search for information specifically in the help center (FAQs, policies, contact)."""
    search_query = f"site:alibaba.ir/help-center {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_magazine_func(query: str) -> str:
    """Search for articles and information in the Alibaba Magazine."""
    search_query = f"site:alibaba.ir/mag {query}"
    response = tavily_tool.invoke({"query": search_query})
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
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_flights_iran_func(query: str) -> str:
    """Search for information about domestic flights (پرواز داخلی) on alibaba.ir."""
    search_query = f"site:alibaba.ir {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_flights_international_func(query: str) -> str:
    """Search for information about international flights (پرواز خارجی) on alibaba.ir/iranout."""
    search_query = f"site:alibaba.ir/iranout {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_trains_func(query: str) -> str:
    """Search for information about train tickets (قطار) on alibaba.ir."""
    search_query = f"site:alibaba.ir/train-ticket {query}"
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
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_tours_func(query: str) -> str:
    """Search for information about tours (تور) on alibaba.ir."""
    search_query = f"site:alibaba.ir/tour {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_hotels_func(query: str) -> str:
    """Search for information about hotels (هتل) on alibaba.ir."""
    search_query = f"site:alibaba.ir/hotel {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_accommodations_func(query: str) -> str:
    """Search for information about villas and accommodations (ویلا و اقمتگاه) on alibaba.ir."""
    search_query = f"site:alibaba.ir/accommodation {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_visa_func(query: str) -> str:
    """Search for information about visas (ویزا) on alibaba.ir."""
    search_query = f"site:alibaba.ir/visa {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

def search_alibaba_insurance_func(query: str) -> str:
    """Search for information about travel insurance (بیمه مسافرتی) on alibaba.ir."""
    search_query = f"site:alibaba.ir/insurance {query}"
    response = tavily_tool.invoke({"query": search_query})
    if isinstance(response, dict) and 'results' in response:
        results = response['results']
        return "\n".join([f"Title: {res['title']}\nURL: {res['url']}\nSnippet: {res['content']}\n---" for res in results[:3]])
    else:
        return str(response)

# --- Define the list of tools available to the agent ---
# تغییر: تعریف ابزارها به صورت StructuredTool
tools = [
    # --- General and Help Center Tools ---
    StructuredTool.from_function(
        name="search_alibaba_general",
        description="Search for general information across all main sections of alibaba.ir. Use this for broad queries.",
        func=search_alibaba_general_func,
        args_schema=SearchInput # مشخص کردن ساختار ورودی
    ),
    StructuredTool.from_function(
        name="search_alibaba_help_center",
        description="Search for information specifically within the help center (FAQs, policies, contact info) on alibaba.ir/help-center.",
        func=search_alibaba_help_center_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_magazine",
        description="Search for articles and travel guides in the Alibaba Magazine (alibaba.ir/mag).",
        func=search_alibaba_magazine_func,
        args_schema=SearchInput
    ),

    # --- Specific Service Category Tools ---
    StructuredTool.from_function(
        name="search_alibaba_profile",
        description="Search for information about profile (پروفایل).",
        func=search_alibaba_profile_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_flights_domestic",
        description="Search for information about domestic flights (پرواز داخلی) on alibaba.ir.",
        func=search_alibaba_flights_iran_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_flights_international",
        description="Search for information about international flights (پرواز خارجی) on alibaba.ir/iranout.",
        func=search_alibaba_flights_international_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_trains",
        description="Search for information about train tickets (قطار) on alibaba.ir/train-ticket.",
        func=search_alibaba_trains_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_buses",
        description="Search for information about bus tickets (اتوبوس) on alibaba.ir/bus-ticket.",
        func=search_alibaba_buses_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_tours",
        description="Search for information about tours (تور) on alibaba.ir/tour.",
        func=search_alibaba_tours_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_hotels",
        description="Search for information about hotels (هتل) on alibaba.ir/hotel.",
        func=search_alibaba_hotels_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_accommodations",
        description="Search for information about villas and accommodations (ویلا و اقمتگاه) on alibaba.ir/accommodation.",
        func=search_alibaba_accommodations_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_visa",
        description="Search for information about visas (ویزا) on alibaba.ir/visa.",
        func=search_alibaba_visa_func,
        args_schema=SearchInput
    ),
    StructuredTool.from_function(
        name="search_alibaba_insurance",
        description="Search for information about travel insurance (بیمه مسافرتی) on alibaba.ir/insurance.",
        func=search_alibaba_insurance_func,
        args_schema=SearchInput
    )
]

def get_agent(model_name: str):
    llm = ChatOpenAI(
        model_name=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        temperature=0.3,  
        max_tokens=4096,  
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1
    )
    llm = llm.with_config(system_message="""
You are a smart and friendly assistant named SupportBot.
You help users find information specifically about services and policies on alibaba.ir.
Always respond in natural Persian (Farsi). Do NOT show code unless asked.

Available tools:
- search_alibaba_general: For general questions about alibaba.ir.
- search_alibaba_help_center: For FAQs, policies, and contact information.
- search_alibaba_magazine: For articles and guides from the Alibaba Magazine.
- search_alibaba_profile: For questions about profile.
- search_alibaba_flights_domestic: For questions about domestic flights.
- search_alibaba_flights_international: For questions about international flights.
- search_alibaba_trains: For questions about train tickets.
- search_alibaba_buses: For questions about bus tickets.
- search_alibaba_tours: For questions about tours.
- search_alibaba_hotels: For questions about hotels.
- search_alibaba_accommodations: For questions about villas and accommodations.
- search_alibaba_visa: For questions about visas.
- search_alibaba_insurance: For questions about travel insurance.
""")
    return create_react_agent(llm, tools=tools)
