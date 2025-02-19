import time
import json
import asyncio
import aioredis
import uvicorn
import chromadb
import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Depends
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from sentence_transformers import SentenceTransformer

# ✅ Initialize FastAPI app
app = FastAPI()

# ✅ Async Redis client
redis_client = None

async def connect_redis():
    """ Connects to Redis on startup. """
    global redis_client
    redis_client = await aioredis.from_url("redis://localhost", decode_responses=True)
    await FastAPILimiter.init(redis_client)

@app.on_event("startup")
async def startup_event():
    await connect_redis()

@app.on_event("shutdown")
async def shutdown_event():
    if redis_client:
        await redis_client.close()

# ✅ Rate limiting: 5 requests per second per user
limiter = RateLimiter(times=5, seconds=1)

# ✅ Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="movie_dialogues")

# ✅ Configure Google Gemini AI
genai.configure(api_key="AIzaSyBYlHCEB1HWNHC4EiUqKRoareJHF6_gE7I")
model = genai.GenerativeModel("gemini-pro")

async def generate_gemini_response(prompt: str) -> str:
    """ Wrap Gemini API call in a thread to avoid blocking FastAPI's event loop. """
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(None, model.generate_content, prompt)
    return response.text.strip() if response and hasattr(response, "text") else "I don't know what to say."

@app.post("/chat", dependencies=[Depends(limiter)])
async def chat(movie_character_name: str, user_message: str):
    """ Handles chat requests with caching, ChromaDB search, and Gemini AI. """
    if not movie_character_name or not user_message:
        raise HTTPException(status_code=400, detail="Both 'movie_character_name' and 'user_message' are required")

    start_time = time.time()  # Start timing
    movie_character_name = movie_character_name.strip().lower()
    user_message = user_message.strip()
    cache_key = f"{movie_character_name}:{user_message}"

    # 1️⃣ **Check Redis Cache**
    cached_response = await redis_client.get(cache_key)
    if cached_response:
        response_data = json.loads(cached_response)
        response_data["time_taken"] = round(time.time() - start_time, 4)  # Add time taken
        return response_data

    # 2️⃣ **Query ChromaDB**
    query_embedding = embedding_model.encode(user_message).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=1)

    if results.get("documents") and results["documents"][0]:
        character_response = results["documents"][0][0]
        metadata = results.get("metadatas", [[]])[0][0] if results.get("metadatas") else {}
        retrieved_character = metadata.get("character_name", "").strip().lower()

        if retrieved_character == movie_character_name:
            context_prompt = f"Explain this movie dialogue in one or two sentences: '{character_response}'"
            context = await generate_gemini_response(context_prompt)

            response_data = {
                "character_response": character_response,
                "context": context,
                "source": "database",
                "time_taken": round(time.time() - start_time, 4)  # Add time taken
            }

            await redis_client.setex(cache_key, 3600, json.dumps(response_data))
            return response_data

    # 3️⃣ **No match in database, generate AI response**
    ai_prompt = f"Reply as {movie_character_name} in a movie: {user_message}"
    ai_response = await generate_gemini_response(ai_prompt)

    response_data = {
        "character_response": ai_response,
        "context": "",
        "source": "ai",
        "time_taken": round(time.time() - start_time, 4)  # Add time taken
    }

    await redis_client.setex(cache_key, 3600, json.dumps(response_data))
    return response_data

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
