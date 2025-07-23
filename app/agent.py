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

###  site tools:
tavily_tool = TavilySearchResults(max_results=3)

def search_alibaba(query: str) -> str:
    """Search for information specifically on alibaba.ir."""
    search_query = f"site:alibaba.ir {query}"
    return tavily_tool.invoke({"query": search_query})

def search_alibaba_faq(query: str) -> str:
    """Search for FAQs specifically on alibaba.ir help center."""
    search_query = f"site:alibaba.ir/help-center/categories/faq {query}"
    return tavily_tool.invoke({"query": search_query})

# Convert all to LangChain tool
tools = [
    Tool.from_function(
        name="search_alibaba_flights_or_services", 
        description="Search for flight tickets, travel services, and general information on alibaba.ir. Use this for questions about flights, buses, trains, etc.",
        func=search_alibaba
    ),
    Tool.from_function(
        name="search_alibaba_faq", 
        description="Search for Frequently Asked Questions (FAQs) on alibaba.ir's help center. Use this for specific questions about policies, rules, procedures, etc.",
        func=search_alibaba_faq
    ,tavily_tool)]

def get_agent(model_name: str):
    llm = ChatOpenAI(
        model_name=model_name,
        openai_api_key=openrouter_api_key,
        openai_api_base=openrouter_base_url
    )
    llm = llm.with_config(system_message="""
You are a smart and friendly assistant named SupportBot. 
You help users find information using internal tools such as searching the web, especially alibaba.ir.
Always respond in natural Persian.

Available tools:
- search_alibaba_flights_or_services: Search for flights, buses, trains, and general info on alibaba.ir.
- search_alibaba_faq: Search for FAQs on alibaba.ir's help center.
""")
    return create_react_agent(llm, tools=tools)