from chromadb import PersistentClient

# Connect to ChromaDB
client = PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("movie_dialogues")

# Delete all entries
all_data = collection.get()
if "ids" in all_data and all_data["ids"]:
    collection.delete(ids=all_data["ids"])
    print("✅ ChromaDB collection cleared successfully!")
else:
    print("⚠️ No data found in ChromaDB.")

