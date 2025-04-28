import os
from llama_index.llms.gemini import Gemini
from llama_index.llms.ollama import Ollama


def get_gemini_model():
    gemini_llm = Gemini(
    model=f"models/gemini-1.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY"),
    )
    return gemini_llm

def get_ollama_model():
    ollama_llm = Ollama(model="deepseek-r1:1.5b", request_timeout=100)  
    return ollama_llm 

class Llm:
    pass