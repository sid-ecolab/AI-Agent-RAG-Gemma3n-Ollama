import os
import chromadb
from openai import OpenAI, AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

PROFILE = os.environ.get("LLM_PROFILE", "cloud")


def get_embedding_client():
    if PROFILE == "cloud":
        return AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://cds-ds-openai-001-x.openai.azure.com/",
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
        )
    else:
        return OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )


def get_embedding_model():
    if PROFILE == "cloud":
        return "text-embedding-3-small"
    else:
        return "nomic-embed-text"


def get_collection_name():
    if PROFILE == "cloud":
        return "documents"
    else:
        return "documents_local"


client = get_embedding_client()
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(get_collection_name())


def get_embedding(text):
    response = client.embeddings.create(
        model=get_embedding_model(),
        input=text,
    )
    return response.data[0].embedding


def retrieve(query, k=3):
    query_embedding = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
    )
    return results["documents"][0]
