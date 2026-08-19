import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "")
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
REPLICATE_MODEL = os.environ.get("REPLICATE_MODEL", "")
TRIGGER_WORD = os.environ.get("TRIGGER_WORD", "")

REQUIRED_VARS = {
    "SLACK_BOT_TOKEN": SLACK_BOT_TOKEN,
    "SLACK_SIGNING_SECRET": SLACK_SIGNING_SECRET,
    "REPLICATE_API_TOKEN": REPLICATE_API_TOKEN,
}


def check_config(require_model=False):
    missing = [k for k, v in REQUIRED_VARS.items() if not v]
    if require_model and not REPLICATE_MODEL:
        missing.append("REPLICATE_MODEL")
    if missing:
        raise RuntimeError(
            f"Missing required .env values: {', '.join(missing)}. "
            f"Copy .env.example to .env and fill these in."
        )
