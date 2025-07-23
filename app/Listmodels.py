from langchain_openai import ChatOpenAI
import os
client = ChatOpenAI(
    api_key = os.getenv('OPENROUTER_API_KEY')
)
models = client.models.list()
for model in models:
    print(model.id)