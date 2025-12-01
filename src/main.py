import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Make sure .env file exists")

client = OpenAI(api_key=OPENAI_API_KEY)

print("OpenAI client configured correctly!")

