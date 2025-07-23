### app/main.py
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.chat_router import chat_router
from app.auth_router import auth_router

app = FastAPI(title="Smart Support Chatbot")

@app.get("/")
def root():
    return RedirectResponse("/docs") # or return a simple message

@app.get("/favicon.ico")
def favicon():
    return {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://687f7594951ddf00081c0b47--supportchatbotai.netlify.app"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

#  Defining a security schema for Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Smart Support Chatbot",
        version="0.1.0",
        description="Chatbot with Authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if method in ["post", "get"]:
                openapi_schema["paths"][path][method]["security"] = [{"OAuth2PasswordBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

#app.openapi = custom_openapi

#  Register routers
app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/chat")
