from flask import Flask, request, abort
from dotenv import load_dotenv
import os 
from pathlib import Path

ROOT = Path(__file__).resolve().parents[0]
load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

from agent.agent_main import get_agent_answer
from sqlite.fetch import save_data, get_history

DB_PATH = ROOT / "sqlite" / "conversations.db"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:

        # Get the conversation history
        history = get_history(user_id=event.source.user_id, limit=5)

        # Get the user's question and the agent's response
        question = event.message.text
        response = get_agent_answer(question=question, history=history)

        # Save the conversation to the database
        user_message = {
            'user_message': question,
            'user_id': event.source.user_id,
            'timestamp': event.timestamp
        }
        agent_message = {'agent_message': response}
        save_data(user=user_message, agent=agent_message, db_path=DB_PATH)

        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=response)]
            )
        )

if __name__ == "__main__":
    app.run()