import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client (Persistent Storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "movie_dialogues"

try:
    collection = chroma_client.get_collection(collection_name)
except Exception:
    collection = chroma_client.create_collection(name=collection_name)

# Initialize the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to SQLite database
conn = sqlite3.connect("movie_dialogues.db")
cursor = conn.cursor()

# Fetch dialogues
cursor.execute("SELECT character_name, user_question, character_response FROM dialogues")
rows = cursor.fetchall()

# Store dialogues in ChromaDB
for character_name, user_question, character_response in rows:
    unique_id = f"{character_name}_{user_question}_{character_response}"

    # Check if entry already exists in ChromaDB
    existing_entry = collection.get(ids=[unique_id])
    if existing_entry and existing_entry["documents"]:
        print(f"🔹 Entry with ID '{unique_id}' already exists, skipping.")
        continue

    embedding = embedding_model.encode(character_response).tolist()

    collection.add(
    documents=[character_response],  # ✅ Ensure character response is stored
    embeddings=[embedding],  # ✅ Store embeddings
    metadatas=[{  
        "character_name": character_name,  
        "user_question": user_question,  
        "character_response": character_response  # ✅ Ensure response is also stored in metadata
    }],
    ids=[unique_id]
)


    print(f"✅ Added: {unique_id}")

# Close database connection
conn.close()

print("🚀 ChromaDB has been successfully populated!")
