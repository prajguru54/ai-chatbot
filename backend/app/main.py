from fastapi import FastAPI
from app.routers import chat
import os
from dotenv import load_dotenv

load_dotenv()
# print(f"GOOGLE_API_KEY: {os.getenv('GOOGLE_API_KEY')}")
# Ensure you have set the GOOGLE_API_KEY environment variable
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

app = FastAPI()

app.include_router(chat.router)
