# Okta AI Automation Tool

An AI-powered IT automation tool that uses natural language to manage user lifecycle in Okta.

## What it does
- Lists all users in an Okta org
- Creates new users via the Okta API
- Deactivates users using plain English requests
- Uses Claude AI to interpret requests and identify the correct user and action
- Requires human confirmation before executing any action

## Tech Stack
- Python
- Okta API
- Anthropic Claude API
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