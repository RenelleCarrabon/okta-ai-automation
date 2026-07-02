# Okta AI Automation Suite

An AI-powered IT automation toolkit that handles the full employee lifecycle — 
onboarding, access review, and offboarding — using Okta API.


## What it does

### 🚀 Onboarding (onboarding.py)
- Creates a new employee's Okta account with title and department
- Automatically assigns them to the correct department group
- Generates a personalized AI welcome email via Claude
- Saves a timestamped onboarding report

### 🔍 Access Review (access_review.py)
- Pulls all users from Okta
- Uses Claude AI to assess each account for security risk
- Flags dormant, suspicious, or unactivated accounts
- Generates a compliance report with recommended actions

### 🚫 Offboarding (okta_users.py)
- Takes a plain English request like "offboard John Doe"
- Connects to Okta and pulls live user data
- Uses Claude AI to identify the correct user and action
- Requires human confirmation before executing
- Automatically deactivates the user in Okta

## Tech Stack
- Python
- Okta API
- Anthropic Claude API (claude-sonnet-4-6)
- python-dotenv

## Setup
1. Clone the repo
2. Create a virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install dependencies: `pip3 install requests anthropic python-dotenv`
5. Create a `.env` file with your credentials:

OKTA_DOMAIN=your-okta-domain
OKTA_TOKEN=your-okta-api-token
ANTHROPIC_API_KEY=your-anthropic-api-key


## Why I built this
These tools replace repetitive UI-based tasks with automated, AI-assisted workflows.

## Author
Renelle Carrabon — IT Automation & AI Operations
[LinkedIn](https://linkedin.com/in/renellecarrabon) | 
[GitHub](https://github.com/RenelleCarrabon)
