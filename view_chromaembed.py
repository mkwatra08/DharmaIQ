import chromadb

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection(name="movie_dialogues")

# Fetch all stored dialogues with embeddings
stored_data = collection.get(include=["embeddings", "metadatas", "documents"])

# Check if there's any data
if not stored_data.get("ids"):
    print(" No dialogues found in ChromaDB!")
else:
    print("\n Stored Dialogues and Embeddings in ChromaDB:\n")
    print(f"{'Character':<20} | {'User Question':<50} | {'Character Response':<50} | {'Embedding'}")
    print("-" * 200)

    for i in range(len(stored_data["ids"])):
        metadata = stored_data.get("metadatas", [{}])[i] or {}  # Handle missing metadata
        character = metadata.get("character_name", "Unknown")
        user_question = metadata.get("user_question", "Unknown")
        character_response = stored_data.get("documents", ["Unknown"])[i]

        #  Fix: Properly check if embeddings exist
        embeddings = stored_data.get("embeddings", [None])
        embedding = embeddings[i][:5] if embeddings[i] is not None else " No Embedding"

        print(f"{character:<20} | {user_question:<50} | {character_response:<50} | {embedding}")

    print("\n Successfully retrieved all stored dialogues and embeddings!")
