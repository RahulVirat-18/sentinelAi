import chromadb
import sys

# Connect to the database folder
client = chromadb.PersistentClient(path="chroma_db")

def list_all_cases():
    print("\n--- 📂 ALL CASE MEMORIES ---")
    collections = client.list_collections()
    if not collections:
        print("No memories found yet.")
        return

    for col in collections:
        print(f"Found Memory Bank: {col.name}")

def inspect_case(case_id):
    collection_name = f"case_{case_id}"
    try:
        collection = client.get_collection(name=collection_name)
        
        # Fetch ALL data from this collection
        data = collection.get()
        
        print(f"\n--- 🧠 INSIDE MEMORY: {collection_name} ---")
        count = len(data['ids'])
        print(f"Total Facts Stored: {count}")
        print("-" * 40)
        
        for i in range(count):
            print(f"[{i+1}] Source: {data['metadatas'][i]['source']}")
            print(f"    Fact: {data['documents'][i]}")
            print("-" * 40)
            
    except ValueError:
        print(f"❌ Error: Memory for Case {case_id} does not exist.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If user runs: python view_memory.py 1
        inspect_case(sys.argv[1])
    else:
        # If user runs: python view_memory.py
        list_all_cases()
        print("\nTo see details, run: python view_memory.py <case_id>")
        print("Example: python view_memory.py 1")