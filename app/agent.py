### app/agents.py
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.tools import Tool 

import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access the variables
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
openrouter_base_url = os.getenv("OPENROUTER_API_BASE") 

tavily_key = os.getenv("TAVILY_API_KEY")
didar_key = os.getenv('DIDAR_API_KEY')



###  DIDAR tools:

#  1. Search for cards
def search_cases(query: str) -> str:
    url = f"https://app.didar.me/api/Case/search?apikey={didar_key}"
    payload = {"search": query}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return "❗ Error searching cases."
    data = response.json()
    if not data:
        return "No matching cases found."
    return "\n".join([f"📌 {c['title']} - Status: {c['status']}" for c in data[:3]])

#  2. Search for company contacts
def search_contacts(query: str) -> str:
    url = f"https://app.didar.me/api/contact/companysearch?apikey={didar_key}"
    payload = {"search": query}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return "❗ Error searching contacts."
    contacts = response.json()
    if not contacts:
        return "No contacts found."
    return "\n".join([f"👤 {c['name']} - Company: {c['company']}" for c in contacts[:3]])

#  3. Search for activities
def search_activities(query: str) -> str:
    url = f"https://app.didar.me/api/activity/search?apikey={didar_key}"
    payload = {"search": query}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return "❗ Error searching activities."
    acts = response.json()
    if not acts:
        return "No activities found."
    return "\n".join([f"📅 {a['subject']} - Type: {a['type']}" for a in acts[:3]])

#  4. Search for deals
def search_deals(query: str) -> str:
    url = f"http://localhost:4300/api/deal/search?apikey={didar_key}"
    payload = {"search": query}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        return "❗ Error searching deals."
    deals = response.json()
    if not deals:
        return "No deals found."
    return "\n".join([f"💼 {d['title']} - Status: {d['status']}" for d in deals[:3]])

# Convert all to LangChain tool
tools = [
    Tool.from_function(
        name="search_didar_cases",
        description="Search customer cases using keywords.",
        func=search_cases
    ),
    Tool.from_function(
        name="search_didar_contacts",
        description="Search for company contacts in Didar.",
        func=search_contacts
    ),
    Tool.from_function(
        name="search_didar_activities",
        description="Search for customer activities by subject or type.",
        func=search_activities
    ),
    Tool.from_function(
        name="search_didar_deals",
        description="Search for business deals by title or status.",
        func=search_deals
    ),
    TavilySearchResults(max_results=3)
]


def get_agent(model_name: str):
    llm = ChatOpenAI(
        model_name=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url
    )

    llm = llm.with_config(system_message="""
You are a smart and friendly assistant named SupportBot. 
You help users find information using internal tools such as Didar APIs and Tavily web search.
Always respond in natural English, and do NOT show code unless asked.
""")

    return create_react_agent(llm, tools=tools)
