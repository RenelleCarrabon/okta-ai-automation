import requests
import anthropic
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

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

# --- FUNCTION 1: Get all users ---


def get_all_users():
    url = f"https://{OKTA_DOMAIN}/api/v1/users?limit=25"
    response = requests.get(url, headers=headers)
    return response.json()

# --- FUNCTION 2: Get apps assigned to a user ---


def get_user_apps(user_id):
    url = f"https://{OKTA_DOMAIN}/api/v1/users/{user_id}/appLinks"
    response = requests.get(url, headers=headers)
    return response.json()

# --- FUNCTION 3: Get user's last login events ---


def get_user_logins(user_email):
    since = (datetime.utcnow() - timedelta(days=30)
             ).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    url = f"https://{OKTA_DOMAIN}/api/v1/logs?since={since}&filter=actor.alternateId+eq+\"{user_email}\"&limit=50"
    response = requests.get(url, headers=headers)
    return response.json()

# --- FUNCTION 4: Ask Claude to analyze usage ---


def analyze_license_waste(user_name, user_email, apps, login_count):
    app_list = "\n".join(
        [f"- {app.get('label', 'Unknown App')}" for app in apps]) if apps else "No apps assigned"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""You are an IT cost optimization analyst reviewing SaaS license usage.

Analyze this user's app assignments vs actual login activity:

User: {user_name} ({user_email})
Apps assigned in Okta:
{app_list}

Login events in last 30 days: {login_count}

Provide analysis in this exact format:
RISK: (LOW/MEDIUM/HIGH waste risk)
UNUSED_APPS: (list any apps likely unused based on login activity)
ESTIMATED_WASTE: (low/medium/high)
RECOMMENDATION: (one clear action to take)
REASON: (one sentence explanation)"""
            }
        ]
    )
    return message.content[0].text

# --- FUNCTION 5: Run the full audit ---


def run_saas_audit():
    print("\n💰 SaaS License Auditor")
    print("=" * 50)
    print("Scanning for unused licenses and wasted spend...\n")

    users = get_all_users()
    print(f"📊 Found {len(users)} users to audit\n")

    report = []
    total_waste_flags = 0

    for user in users:
        if user['status'] not in ['ACTIVE', 'PROVISIONED']:
            continue

        first = user['profile']['firstName']
        last = user['profile']['lastName']
        email = user['profile']['email']
        user_id = user['id']
        last_login = user.get('lastLogin', 'Never')

        print(f"🔍 Auditing: {first} {last} ({user['status']})")

        # Get their apps
        apps = get_user_apps(user_id)

        # Get their login activity
        logins = get_user_logins(email)
        login_count = len(logins)

        print(
            f"   Apps assigned: {len(apps)} | Logins (30 days): {login_count}")

        # Ask Claude to analyze
        analysis = analyze_license_waste(
            f"{first} {last}", email, apps, login_count)

        # Check if high risk
        if "RISK: HIGH" in analysis or "RISK: MEDIUM" in analysis:
            total_waste_flags += 1
            print(f"   ⚠️  Waste flagged!")

        report.append({
            "name": f"{first} {last}",
            "email": email,
            "status": user['status'],
            "last_login": last_login,
            "apps_assigned": len(apps),
            "logins_30_days": login_count,
            "analysis": analysis
        })

        print()

    # Generate report
    print("=" * 50)
    print(f"📋 AUDIT COMPLETE")
    print(f"Users audited: {len(report)}")
    print(f"Waste flags: {total_waste_flags}")
    print("=" * 50)

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"saas_audit_{timestamp}.txt"

    with open(filename, 'w') as f:
        f.write("SAAS LICENSE AUDIT REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Users audited: {len(report)}\n")
        f.write(f"Waste flags: {total_waste_flags}\n")
        f.write("=" * 50 + "\n\n")

        for entry in report:
            f.write(f"User: {entry['name']} ({entry['email']})\n")
            f.write(f"Status: {entry['status']}\n")
            f.write(f"Last Login: {entry['last_login']}\n")
            f.write(f"Apps Assigned: {entry['apps_assigned']}\n")
            f.write(f"Logins (30 days): {entry['logins_30_days']}\n")
            f.write(f"\nAI Analysis:\n{entry['analysis']}\n")
            f.write("-" * 30 + "\n\n")

    print(f"\n✅ Report saved to {filename}")


# --- RUN IT ---
run_saas_audit()
