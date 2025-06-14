import json
import os

AUTH_FILE = "user_auth.json"

def load_auth_data():
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            return json.load(f)
    return {}

def save_auth_data(data):
    with open(AUTH_FILE, "w") as f:
        json.dump(data, f, indent=2)    
