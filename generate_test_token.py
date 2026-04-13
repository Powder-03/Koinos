"""
Generate a Firebase ID token for API testing.
Usage: python generate_test_token.py

Prerequisites: pip install firebase-admin requests
"""
import json
import firebase_admin
from firebase_admin import credentials, auth
import requests

# --- CONFIG ---
SERVICE_ACCOUNT_PATH = "./serviceAccountKey.json"
TEST_UID = "test-user-123"

# Step 1: Read the project ID from the service account
with open(SERVICE_ACCOUNT_PATH) as f:
    sa = json.load(f)
    PROJECT_ID = sa["project_id"]

# You need your Firebase Web API Key from:
# Firebase Console → Project Settings → General → Web API Key
FIREBASE_WEB_API_KEY = input("Enter your Firebase Web API Key: ").strip()

# Step 2: Initialize Firebase Admin & create a custom token
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

custom_token = auth.create_custom_token(TEST_UID)
print(f"\n✅ Custom token created for UID: {TEST_UID}")

# Step 3: Exchange custom token for an ID token via Firebase Auth REST API
url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={FIREBASE_WEB_API_KEY}"
resp = requests.post(url, json={
    "token": custom_token.decode() if isinstance(custom_token, bytes) else custom_token,
    "returnSecureToken": True
})

if resp.status_code != 200:
    print(f"\n❌ Error exchanging token: {resp.json()}")
    exit(1)

id_token = resp.json()["idToken"]

print(f"\n✅ Firebase ID Token (copy this):\n")
print(id_token)
print(f"\n--- Test commands ---\n")
print(f'# Health check (no auth needed)')
print(f'curl http://localhost:8000/')
print(f'\n# Create expense')
print(f'curl -X POST http://localhost:8000/api/manual/ ^')
print(f'  -H "Authorization: Bearer {id_token[:20]}..." ^')
print(f'  -H "Content-Type: application/json" ^')
print(f'  -d "{{\\"amount\\": 500, \\"category\\": \\"Transport\\", \\"date\\": \\"2026-04-13\\", \\"description\\": \\"Cab ride\\"}}"')
print(f'\n# List expenses')
print(f'curl http://localhost:8000/api/manual/ -H "Authorization: Bearer {id_token[:20]}..."')
