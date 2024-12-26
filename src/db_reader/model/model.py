# import google.generativeai as genai
import os
from llama_index.llms.gemini import Gemini
from llama_index.llms.ollama import Ollama

# Load environment variables
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_model():
    gemini_llm = Gemini(
    model=f"models/gemini-pro",
    api_key=os.getenv("GOOGLE_API_KEY")
    )
    return gemini_llm

def get_ollama_model():
    ollama_llm = Ollama(model="llama3.2:latest", request_timeout=100)  
    return ollama_llm 

# query_str = "show me all customers whose loan amount is greater than 500000"
# query_str = "lap loans between 2019 to 2020"
# response = query_engine.query(query_str)
