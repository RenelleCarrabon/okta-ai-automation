import requests
import anthropic
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Credentials
OKTA_DOMAIN = os.getenv("OKTA_DOMAIN")
OKTA_TOKEN = os.getenv("OKTA_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Headers
headers = {
    "Authorization": f"SSWS {OKTA_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Anthropic client
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# --- FUNCTION 1: Get all users and their status ---


def get_all_users():
    url = f"https://{OKTA_DOMAIN}/api/v1/users?limit=25"
    response = requests.get(url, headers=headers)
    return response.json()

# --- FUNCTION 2: Ask Claude to review each user ---


def ai_review_user(user):
    first = user['profile']['firstName']
    last = user['profile']['lastName']
    email = user['profile']['email']
    status = user['status']
    created = user['created']
    last_login = user.get('lastLogin', 'Never')

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an IT security analyst performing an access review.

Review this Okta user and provide a risk assessment:

Name: {first} {last}
Email: {email}
Status: {status}
Account Created: {created}
Last Login: {last_login}

Respond in this exact format:
RISK: (LOW, MEDIUM, or HIGH)
ACTION: (KEEP, REVIEW, or DEACTIVATE)
REASON: (one sentence explanation)"""
            }
        ]
    )
    return message.content[0].text

# --- FUNCTION 3: Generate the report ---


def run_access_review():
    print("\n🔍 Running AI Access Review...")
    print("=" * 50)

    users = get_all_users()
    report = []

    for user in users:
        first = user['profile']['firstName']
        last = user['profile']['lastName']
        status = user['status']

        print(f"\nReviewing: {first} {last} ({status})")
        assessment = ai_review_user(user)
        print(assessment)

        report.append({
            "name": f"{first} {last}",
            "status": status,
            "assessment": assessment
        })

    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"access_review_{timestamp}.txt"

    with open(filename, 'w') as f:
        f.write("OKTA ACCESS REVIEW REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        for entry in report:
            f.write(f"User: {entry['name']}\n")
            f.write(f"Status: {entry['status']}\n")
            f.write(f"{entry['assessment']}\n")
            f.write("-" * 30 + "\n\n")

    print(f"\n✅ Report saved to {filename}")


# --- RUN IT ---
run_access_review()
