from chromadb import PersistentClient

# Connect to ChromaDB
client = PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("movie_dialogues")

# Fetch all stored dialogues
stored_dialogues = collection.get(include=["documents", "metadatas"])

print("\n📌 Stored Dialogues in ChromaDB:")
for doc, meta in zip(stored_dialogues["documents"], stored_dialogues["metadatas"]):
    print(f"🔹 Dialogue: {doc} | 🎭 Character: {meta.get('character', 'Unknown')}")
