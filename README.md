# Down Memory Lane -- Slack Bot (Flux LoRA on Replicate)

Generates "you as a kid" photos on request in Slack, using a Flux LoRA model
fine-tuned on your own photos, and replies with the image in the same thread.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env`:
- `SLACK_BOT_TOKEN` -- from api.slack.com/apps -> OAuth & Permissions
- `SLACK_SIGNING_SECRET` -- from api.slack.com/apps -> Basic Information
- `REPLICATE_API_TOKEN` -- from replicate.com/account/api-tokens
- `REPLICATE_MODEL` -- your trained model as `owner/name:version` (from the training detail page once it completes)
- `TRIGGER_WORD` -- must match what you set during training (e.g. `IRISFACE`)

## Run

```bash
python app.py          # runs on port 5002
ngrok http 5002         # in a second terminal
```

Take the ngrok HTTPS URL, append `/slack/events`, and set that as the
Request URL under Slack app -> Event Subscriptions. Subscribe to the
`message.channels` bot event, save, then invite the bot into a channel
(`/invite @Down Memory Lane Bot`).

## Test

Post a message in that channel, e.g.:
- "Your 2-year-old self in your house's backyard"
- "Your 5-year-old self on a beach"
- "Your 10-year-old self in a classroom"

The bot replies in-thread with a "Generating..." message, then the image.
