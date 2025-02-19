from locust import HttpUser, task, between
import random

class MovieChatbotUser(HttpUser):
    wait_time = between(1, 3)  # Simulates user wait time between requests

    @task
    def chat_with_bot(self):
        movie_character_name = random.choice(["batman", "joker", "harry potter", "iron man"])
        user_message = random.choice(["Hello!", "What's your favorite quote?", "Tell me something interesting."])

        self.client.post("/chat", json={"movie_character_name": movie_character_name, "user_message": user_message})


