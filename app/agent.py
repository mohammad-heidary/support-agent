# app/agents.py

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.tools import Tool
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("./app/.env")

# Access the variables
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENROUTER_API_BASE")
tavily_api_key = os.getenv("TAVILY_API_KEY")

# --- Alibaba.ir Tools ---

# Initialize the Tavily tool for web searches
tavily_tool = TavilySearchResults(max_results=3, tavily_api_key= tavily_api_key)

# --- General Search Tools for Alibaba.ir Sections ---
# These tools use Tavily to search within specific subdomains or sections of alibaba.ir

def search_alibaba_general(query: str) -> str:
    """Search for information across the main sections of alibaba.ir."""
    search_query = f"site:alibaba.ir {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_help_center(query: str) -> str:
    """Search for information specifically in the help center (FAQs, policies, contact)."""
    search_query = f"site:alibaba.ir/help-center {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_magazine(query: str) -> str:
    """Search for articles and information in the Alibaba Magazine."""
    search_query = f"site:alibaba.ir/mag {query}"
    return tavily_tool.invoke({"query": search_query})

# --- Specific Section Search Tools ---
# These provide more targeted search capabilities for major service categories
def search_alibaba_profile(query: str) -> str:
    """Search for information about profile(پروفایل)"""
    search_query = f"site:alibaba.ir/profile {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_flights_iran(query: str) -> str:
    """Search for information about domestic flights (پرواز داخلی) on alibaba.ir."""
    search_query = f"site:alibaba.ir {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_flights_international(query: str) -> str:
    """Search for information about international flights (پرواز خارجی) on alibaba.ir/iranout."""
    search_query = f"site:alibaba.ir/iranout {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_trains(query: str) -> str:
    """Search for information about train tickets (قطار) on alibaba.ir."""
    search_query = f"site:alibaba.ir/train-ticket {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_buses(query: str) -> str:
    """Search for information about bus tickets (اتوبوس) on alibaba.ir."""
    search_query = f"site:alibaba.ir/bus-ticket {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_tours(query: str) -> str:
    """Search for information about tours (تور) on alibaba.ir."""
    search_query = f"site:alibaba.ir/tour {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_hotels(query: str) -> str:
    """Search for information about hotels (هتل) on alibaba.ir."""
    search_query = f"site:alibaba.ir/hotel {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_accommodations(query: str) -> str:
    """Search for information about villas and accommodations (ویلا و اقمتگاه) on alibaba.ir."""
    search_query = f"site:alibaba.ir/accommodation {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_visa(query: str) -> str:
    """Search for information about visas (ویزا) on alibaba.ir."""
    search_query = f"site:alibaba.ir/visa {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_insurance(query: str) -> str:
    """Search for information about travel insurance (بیمه مسافرتی) on alibaba.ir."""
    search_query = f"site:alibaba.ir/insurance {query}"
    return tavily_tool.invoke({"query": search_query})

# --- Define the list of tools available to the agent ---
tools = [
    # --- General and Help Center Tools ---
    Tool.from_function(
        name="search_alibaba_general",
        description="Search for general information across all main sections of alibaba.ir. Use this for broad queries.",
        func=search_alibaba_general
    ),
    Tool.from_function(
        name="search_alibaba_help_center",
        description="Search for information specifically within the help center (FAQs, policies, contact info) on alibaba.ir/help-center.",
        func=search_alibaba_help_center
    ),
    Tool.from_function(
        name="search_alibaba_magazine",
        description="Search for articles and travel guides in the Alibaba Magazine (alibaba.ir/mag).",
        func=search_alibaba_magazine
    ),

    # --- Specific Service Category Tools ---

    Tool.from_function(
        name="search_alibaba_profile",
        description="Search for information about profile (پروفایل).",
        func=search_alibaba_profile
    ),
   
    Tool.from_function(
        name="search_alibaba_flights_domestic",
        description="Search for information about domestic flights (پرواز داخلی) on alibaba.ir.",
        func=search_alibaba_flights_iran
    ),

    Tool.from_function(
        name="search_alibaba_flights_international",
        description="Search for information about international flights (پرواز خارجی) on alibaba.ir/iranout.",
        func=search_alibaba_flights_international
    ),
    Tool.from_function(
        name="search_alibaba_trains",
        description="Search for information about train tickets (قطار) on alibaba.ir/train-ticket.",
        func=search_alibaba_trains
    ),
    Tool.from_function(
        name="search_alibaba_buses",
        description="Search for information about bus tickets (اتوبوس) on alibaba.ir/bus-ticket.",
        func=search_alibaba_buses
    ),
    Tool.from_function(
        name="search_alibaba_tours",
        description="Search for information about tours (تور) on alibaba.ir/tour.",
        func=search_alibaba_tours
    ),
    Tool.from_function(
        name="search_alibaba_hotels",
        description="Search for information about hotels (هتل) on alibaba.ir/hotel.",
        func=search_alibaba_hotels
    ),
    Tool.from_function(
        name="search_alibaba_accommodations",
        description="Search for information about villas and accommodations (ویلا و اقمتگاه) on alibaba.ir/accommodation.",
        func=search_alibaba_accommodations
    ),
    Tool.from_function(
        name="search_alibaba_visa",
        description="Search for information about visas (ویزا) on alibaba.ir/visa.",
        func=search_alibaba_visa
    ),
    Tool.from_function(
        name="search_alibaba_insurance",
        description="Search for information about travel insurance (بیمه مسافرتی) on alibaba.ir/insurance.",
        func=search_alibaba_insurance
    )
]

def get_agent(model_name: str):
    llm = ChatOpenAI(
        model_name=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url,
        temperature=0.7,  # For example, for more natural responses
        max_tokens=2048,  # For example, for longer answers
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        model_kwargs={"response_format": {"type": "json_object"}} # for JSON response
    )
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
