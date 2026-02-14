import chromadb
import google.generativeai as genai
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="chroma_db")

def get_embedding(text):
    """Converts text into a list of numbers (vector)"""
    try:
        # Using the newer model to avoid Quota errors
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']
    except Exception as e:
        print(f"--- EMBEDDING ERROR: {e} ---")
        return []

def save_memory(case_id, text, source="report"):
    """
    Saves text into the specific Case Collection.
    """
    try:
        collection_name = f"case_{case_id}"
        collection = chroma_client.get_or_create_collection(name=collection_name)
        
        vector = get_embedding(text)
        
        if not vector:
            print("--- Failed to generate embedding, memory not saved. ---")
            return

        collection.add(
            documents=[text],
            embeddings=[vector],
            metadatas=[{"source": source}], 
            ids=[str(uuid.uuid4())]
        )
        print(f"--- MEMORY: Saved to {collection_name} ---")
    except Exception as e:
        print(f"--- MEMORY ERROR: {e} ---")

def query_memory(case_id, question):
    """
    Finds relevant facts for a question.
    """
    try:
        collection_name = f"case_{case_id}"
        collection = chroma_client.get_collection(name=collection_name)
        
        query_vector = get_embedding(question)
        
        if not query_vector:
            return ""

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3
        )
        
        if results['documents']:
            return "\n".join(results['documents'][0])
        return ""
    except Exception as e:
        # If collection doesn't exist yet, return empty string
        return ""