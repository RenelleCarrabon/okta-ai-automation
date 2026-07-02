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

# --- FUNCTION 1: Get or create department group ---


def get_or_create_group(department):
    # Check if group exists
    url = f"https://{OKTA_DOMAIN}/api/v1/groups?q={department}"
    response = requests.get(url, headers=headers)
    groups = response.json()

    if groups:
        print(f"✅ Found existing group: {department}")
        return groups[0]['id']

    # Create group if it doesn't exist
    url = f"https://{OKTA_DOMAIN}/api/v1/groups"
    new_group = {
        "profile": {
            "name": department,
            "description": f"{department} department group"
        }
    }
    response = requests.post(url, headers=headers, json=new_group)
    group = response.json()
    print(f"✅ Created new group: {department}")
    return group['id']

# --- FUNCTION 2: Add user to group ---


def add_user_to_group(user_id, group_id):
    url = f"https://{OKTA_DOMAIN}/api/v1/groups/{group_id}/users/{user_id}"
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        print(f"✅ User added to department group")
    else:
        print(f"❌ Error adding to group: {response.json()}")

# --- FUNCTION 3: Generate welcome email with Claude ---


def generate_welcome_email(first, last, title, department):
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Generate a warm, professional welcome email for a new employee joining our company.

New hire details:
Name: {first} {last}
Title: {title}
Department: {department}
Start Date: {datetime.now().strftime("%B %d, %Y")}

The email should:
- Be warm and welcoming
- Mention their role and department
- Let them know their Okta account is ready
- Be signed by 'The IT Team'
- Be concise, 3-4 short paragraphs"""
            }
        ]
    )
    return message.content[0].text

# --- FUNCTION 4: Run onboarding for existing user ---


def onboard_existing_user():
    print("\n🚀 AI-Powered Employee Onboarding System")
    print("=" * 50)

    # Existing user details — replace user_id with James Harrison's actual Okta ID
    first = "James"
    last = "Harrison"
    email = "james.harrison@company.com"
    title = "Software Engineer"
    department = "Engineering"
    user_id = "00u14sxeu06xL6YwB698"

    print(f"\n⚙️  Processing onboarding for {first} {last}...\n")

    # Step 1: Get or create department group
    group_id = get_or_create_group(department)

    # Step 2: Add user to group
    add_user_to_group(user_id, group_id)

    # Step 3: Generate welcome email
    print("🤖 Generating welcome email with AI...")
    welcome_email = generate_welcome_email(first, last, title, department)

    # Step 4: Print summary
    print("\n" + "=" * 50)
    print("📋 ONBOARDING SUMMARY")
    print("=" * 50)
    print(f"Name: {first} {last}")
    print(f"Title: {title}")
    print(f"Department: {department}")
    print(f"Email: {email}")
    print(f"Okta ID: {user_id}")
    print("\n📧 WELCOME EMAIL PREVIEW:")
    print("-" * 30)
    print(welcome_email)

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"onboarding_{first}_{last}_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"ONBOARDING REPORT - {first} {last}\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Title: {title}\n")
        f.write(f"Department: {department}\n")
        f.write(f"Email: {email}\n")
        f.write(f"Okta ID: {user_id}\n\n")
        f.write("WELCOME EMAIL:\n")
        f.write(welcome_email)

    print(
        f"\n✅ Onboarding report saved to onboarding_{first}_{last}_{timestamp}.txt")


# --- RUN IT ---
onboard_existing_user()
