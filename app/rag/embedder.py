import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

def get_embedder(model_name: str = "text-embedding-3-large") -> OpenAIEmbeddings:
    load_dotenv()  
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not found in environment or .env file.")

    os.environ["OPENAI_API_KEY"] = openai_api_key

    return OpenAIEmbeddings(model=model_name)