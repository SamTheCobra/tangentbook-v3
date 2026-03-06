import os
import sys
from dotenv import load_dotenv

load_dotenv()

REQUIRED = ["FRED_API_KEY", "EIA_API_KEY", "ANTHROPIC_API_KEY"]
OPTIONAL = ["POLYGON_API_KEY", "CRUNCHBASE_API_KEY", "ALPHA_VANTAGE_API_KEY"]


def validate_env():
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        print(f"\nFATAL: Missing required environment variables:")
        for k in missing:
            print(f"  {k}")
        print(f"\nCopy .env.example to .env and add your keys.")
        print(f"FRED key:      https://fred.stlouisfed.org/docs/api/api_key.html")
        print(f"EIA key:       https://www.eia.gov/opendata/register.php")
        print(f"Anthropic key: https://console.anthropic.com\n")
        sys.exit(1)

    optional_missing = [k for k in OPTIONAL if not os.getenv(k)]
    if optional_missing:
        print(f"INFO: Optional keys not set (features disabled): {', '.join(optional_missing)}")


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tangentbook.db")
FEED_REFRESH_INTERVAL_MINUTES = int(os.getenv("FEED_REFRESH_INTERVAL_MINUTES", "60"))
FRED_API_KEY = os.getenv("FRED_API_KEY", "")
EIA_API_KEY = os.getenv("EIA_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
CRUNCHBASE_API_KEY = os.getenv("CRUNCHBASE_API_KEY", "")
