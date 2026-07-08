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

# Known unsanctioned AI tools to watch for
SHADOW_AI_KEYWORDS = [
    "chatgpt", "openai", "midjourney", "huggingface", "replicate",
    "perplexity", "claude", "gemini", "copilot", "bard", "jasper",
    "runway", "synthesia", "character.ai", "poe", "inflection"
]

# --- FUNCTION 1: Pull Okta system logs ---


def get_okta_logs():
    # Get logs from the last 7 days
    since = (datetime.utcnow() - timedelta(days=7)
             ).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    url = f"https://{OKTA_DOMAIN}/api/v1/logs?since={since}&limit=100"
    response = requests.get(url, headers=headers)
    return response.json()

# --- FUNCTION 2: Extract app sign-on events ---


def extract_app_signons(logs):
    app_signons = []
    for event in logs:
        if event.get('eventType') in ['user.authentication.sso', 'app.oauth2.token.grant']:
            target = event.get('target', [])
            for t in target:
                if t.get('type') == 'AppInstance':
                    app_signons.append({
                        'app': t.get('displayName', 'Unknown'),
                        'user': event.get('actor', {}).get('displayName', 'Unknown'),
                        'time': event.get('published', 'Unknown'),
                        'ip': event.get('client', {}).get('ipAddress', 'Unknown')
                    })
    return app_signons

# --- FUNCTION 3: Check for shadow AI with Claude ---


def analyze_for_shadow_ai(app_signons, logs):
    # Build a summary of all activity for Claude to analyze
    if app_signons:
        activity_summary = "\n".join([
            f"- {s['user']} accessed {s['app']} from {s['ip']} at {s['time']}"
            for s in app_signons
        ])
    else:
        # If no SSO events, summarize recent log activity
        activity_summary = "No SSO app sign-on events found in logs.\n"
        activity_summary += f"Total log events found: {len(logs)}\n"
        if logs:
            event_types = list(
                set([l.get('eventType', 'unknown') for l in logs[:20]]))
            activity_summary += f"Recent event types: {', '.join(event_types)}"

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[
            {
                "role": "user",
                "content": f"""You are an IT security analyst specializing in Shadow AI detection.

Analyze this Okta activity log and identify any potential Shadow AI usage or security concerns.

Known unsanctioned AI tools to watch for: {', '.join(SHADOW_AI_KEYWORDS)}

Recent activity:
{activity_summary}

Even if no direct AI tool sign-ons are found, analyze the activity for:
1. Any suspicious patterns
2. Unusual access times or locations
3. Apps that might be AI-related
4. Security recommendations for Shadow AI prevention

Provide your analysis in this format:

SHADOW AI DETECTED: (YES/NO/INSUFFICIENT DATA)
RISK LEVEL: (LOW/MEDIUM/HIGH)
FINDINGS:
(list your findings)
RECOMMENDATIONS:
(list specific recommendations for preventing Shadow AI in this environment)
SUMMARY:
(2-3 sentence executive summary)"""
            }
        ]
    )
    return message.content[0].text

# --- FUNCTION 4: Generate alert report ---


def run_shadow_ai_detection():
    print("\n🔎 Shadow AI Detection System")
    print("=" * 50)
    print("Scanning Okta logs for unsanctioned AI tool usage...\n")

    # Get logs
    logs = get_okta_logs()
    print(f"📊 Retrieved {len(logs)} log events from the last 7 days")

    # Extract app sign-ons
    app_signons = extract_app_signons(logs)
    print(f"🔍 Found {len(app_signons)} app sign-on events")

    # Analyze with Claude
    print("🤖 Analyzing with Claude AI...\n")
    analysis = analyze_for_shadow_ai(app_signons, logs)

    # Print results
    print("=" * 50)
    print("🚨 SHADOW AI DETECTION REPORT")
    print("=" * 50)
    print(analysis)

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"shadow_ai_report_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write("SHADOW AI DETECTION REPORT\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Logs analyzed: {len(logs)}\n")
        f.write(f"App sign-ons found: {len(app_signons)}\n")
        f.write("=" * 50 + "\n\n")
        if app_signons:
            f.write("APP SIGN-ON ACTIVITY:\n")
            for s in app_signons:
                f.write(f"- {s['user']} accessed {s['app']} at {s['time']}\n")
            f.write("\n")
        f.write("AI ANALYSIS:\n")
        f.write(analysis)

    print(f"\n✅ Report saved to {filename}")


# --- RUN IT ---
run_shadow_ai_detection()
