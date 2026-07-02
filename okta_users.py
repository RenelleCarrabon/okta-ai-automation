import requests
import anthropic
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Your credentials
OKTA_DOMAIN = "integrator-7906418.okta.com"
OKTA_TOKEN = "001Imq5McahzQE6Uune56eE-9DNdGSucq0m0D9qJ_P"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Set up headers
headers = {
    "Authorization": f"SSWS {OKTA_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Set up Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --- FUNCTION 1: Get all users ---


def get_users():
    url = f"https://{OKTA_DOMAIN}/api/v1/users?limit=25"
    response = requests.get(url, headers=headers)
    return response.json()

# --- FUNCTION 2: Create a user ---


def create_user(first_name, last_name, email):
    url = f"https://{OKTA_DOMAIN}/api/v1/users?activate=true"
    new_user = {
        "profile": {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "login": email
        }
    }
    response = requests.post(url, headers=headers, json=new_user)
    user = response.json()
    print(
        f"\n✅ Created user: {user['profile']['firstName']} {user['profile']['lastName']}")
    return user['id']

# --- FUNCTION 3: Deactivate a user ---


def deactivate_user(user_id):
    url = f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/deactivate"
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print(f"\n🚫 User {user_id} has been deactivated")

# --- FUNCTION 4: Ask Claude what to do ---


def ask_claude(request):
    users = get_users()
    user_list = "\n".join([
        f"- {u['profile']['firstName']} {u['profile']['lastName']} (ID: {u['id']}, Status: {u['status']})"
        for u in users
    ])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an IT automation assistant. Based on the request below, 
tell me exactly what Okta action to take and on which user.

Current users in Okta:
{user_list}

Request: {request}

Respond in this exact format:
ACTION: (CREATE or DEACTIVATE)
USER: (full name)
ID: (user ID if deactivating, or NEW if creating)
EMAIL: (email if creating, or N/A)
REASON: (one sentence explanation)"""
            }
        ]
    )
    return message.content[0].text


# --- RUN IT ---
print("\n🤖 IT Automation Assistant")
print("=" * 40)

request = input("\nEnter your IT request: ")
response = ask_claude(request)
print("\nClaude's Analysis:")
print(response)

# Parse Claude's response and execute the action
lines = response.strip().split("\n")
action = lines[0].replace("ACTION: ", "").strip()
user_id = lines[2].replace("ID: ", "").strip()

if action == "DEACTIVATE" and user_id not in ["NOT FOUND", "NEW", "N/A"]:
    confirm = input(f"\n⚠️ Confirm deactivation of user {user_id}? (yes/no): ")
    if confirm.lower() == "yes":
        deactivate_user(user_id)
        print("\n✅ Action completed successfully")
    else:
        print("\n❌ Action cancelled")
else:
    print("\n⚠️ No automatic action taken - please review Claude's analysis")
