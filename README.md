# TANGENTBOOK v3

Personal macro thesis intelligence system. Swiss brutalist editorial design.

## Prerequisites

- Node 18+
- Python 3.11+
- Git

## Setup

```bash
# Get your free API keys first (all take < 2 minutes)
# FRED:      https://fred.stlouisfed.org/docs/api/api_key.html
# EIA:       https://www.eia.gov/opendata/register.php
# Anthropic: https://console.anthropic.com

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Open .env and add your three API keys

# Start backend (port 8000)
uvicorn main:app --reload --port 8000

# Frontend setup (new terminal)
cd ../frontend
npm install
npm run dev                        # starts on port 3000

# Or start both at once:
make dev
```

Visit http://localhost:3000

## API Keys

### Required (free, instant signup)
- **FRED** — macro economic data
- **EIA** — energy data
- **Anthropic** — AI generation features

### No key needed
- Google Trends (pytrends library)
- SEC EDGAR (data.sec.gov)
- BLS (api.bls.gov)
- USASpending (api.usaspending.gov)
- Congress.gov (api.congress.gov)
- Census Bureau (api.census.gov)
- USPTO Patents (api.patentsview.org)

## Security

Never commit your `.env` file. It is in `.gitignore`.
The `.env.example` file (blank values only) is safe to commit.
