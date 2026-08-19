"""
Down Memory Lane -- Slack bot that generates "childhood you" photos using a
Flux LoRA model trained on Replicate.

Flow:
  User posts a message in a channel the bot is in, e.g.
    "my 5-year-old self on a beach"
        |
        v
  Slack Events API -> POST /slack/events (via ngrok tunnel)
        |
        v
  handle_message() -- ignores the bot's own messages, posts an immediate
  "Generating..." ack in the same thread, then calls Replicate with the
  trained LoRA model + trigger word baked into the prompt
        |
        v
  Replicate returns a public image URL
        |
        v
  Bot posts the image back in the SAME thread via chat_postMessage with an
  image block (fast path: no download/re-upload round trip needed)

Run with: python app.py
Needs SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET, REPLICATE_API_TOKEN,
REPLICATE_MODEL, TRIGGER_WORD all set in .env first.
"""

from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
import replicate

import config

config.check_config()

bolt_app = App(
    token=config.SLACK_BOT_TOKEN,
    signing_secret=config.SLACK_SIGNING_SECRET,
)

flask_app = Flask(__name__)
handler = SlackRequestHandler(bolt_app)


@bolt_app.event("message")
def handle_message(event, say, client, logger):
    # Ignore anything that isn't a plain human message -- otherwise the bot
    # can end up replying to its own messages (or edits/deletes) in a loop.
    if event.get("bot_id") or event.get("subtype"):
        return

    description = (event.get("text") or "").strip()
    if not description:
        return

    channel = event["channel"]
    thread_ts = event.get("thread_ts", event["ts"])

    # Immediate ack so the thread doesn't look dead while Replicate runs
    # (image generation typically takes 10-30 seconds).
    say(text=f"Generating: _{description}_ ...", thread_ts=thread_ts)

    try:
        prompt = f"{config.TRIGGER_WORD}, {description}"
        if not config.REPLICATE_MODEL:
            raise RuntimeError(
                "REPLICATE_MODEL is not set in .env -- fill it in with your "
                "trained model's 'owner/name:version' once training finishes."
            )

        output = replicate.run(
            config.REPLICATE_MODEL,
            input={"prompt": prompt},
        )
        # Flux models on Replicate commonly return either a single item or a
        # list of output URLs/FileOutput objects depending on the model
        # version -- handle both.
        image = output[0] if isinstance(output, list) else output
        image_url = str(image)

        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"Here's {description}:",
            blocks=[
                {
                    "type": "image",
                    "image_url": image_url,
                    "alt_text": description,
                }
            ],
        )
    except Exception as e:
        logger.exception("Image generation failed")
        say(text=f"Sorry, something went wrong generating that image: `{e}`", thread_ts=thread_ts)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


@flask_app.route("/", methods=["GET"])
def index():
    return "Down Memory Lane bot is running. Slack should POST to /slack/events."


if __name__ == "__main__":
    # Port 5000 is often taken on macOS by the AirPlay Receiver service.
    flask_app.run(host="0.0.0.0", port=5002, debug=True)
