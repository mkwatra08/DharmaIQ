import requests
import time

API_URL = "http://127.0.0.1:5000/chat"  # Change if needed
HEADERS = {"Content-Type": "application/json"}
DATA = {
    "movie_character_name": "Harry potter",
    "user_message": "What is Hogwarts?"
}

def send_requests(n):
    for i in range(n):
        response = requests.post(API_URL, json=DATA, headers=HEADERS)
        print(f"Request {i+1}: Status Code - {response.status_code}, Response - {response.json()}")
        time.sleep(0.1)  # Short delay to simulate quick consecutive requests

if __name__ == "__main__":
    print("Sending 6 requests to test rate limiting...")
    send_requests(6)  # Send 6 requests rapidly
