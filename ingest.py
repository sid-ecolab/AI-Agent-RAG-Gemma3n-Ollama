import os
from pypdf import PdfReader
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
collection = chroma_client.get_or_create_collection(name=get_collection_name())


def read_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        content = page.extract_text()
        if content:
            text += content
    return text


def split_into_chunks(text: str, chunk_size: int = 700, overlap: int = 100):
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():
            chunks.append(chunk)
    return chunks


def get_embedding(text: str):
    response = client.embeddings.create(
        model=get_embedding_model(),
        input=text,
    )
    return response.data[0].embedding


def ingest_documents(data_folder: str = "data"):
    print(f"Starting ingestion (profile: {PROFILE})...")
    print(f"Embedding model: {get_embedding_model()}")
    print(f"Collection: {get_collection_name()}\n")

    for filename in os.listdir(data_folder):
        if not filename.endswith(".pdf"):
            continue

        file_path = os.path.join(data_folder, filename)
        print(f"Reading: {filename}")

        text = read_pdf(file_path)
        chunks = split_into_chunks(text)

        print(f"  -> Created {len(chunks)} chunks")

        for idx, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            collection.add(
                documents=[chunk],
                embeddings=[embedding],
                ids=[f"{filename}_{idx}"],
            )

    print("\nIngestion completed successfully!")


if __name__ == "__main__":
    ingest_documents()
