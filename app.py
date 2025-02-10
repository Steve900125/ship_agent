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
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

from agent.agent_main import get_agent_answer
from sqlite.fetch import save_data, get_history

DB_PATH = ROOT / "sqlite" / "conversations.db"

from vision.detect import default_detect, clean_folder

VISION_PATH = ROOT / "vision"
IMAGES_PATH = VISION_PATH / "images"
YOLO_RESULT_PATH = VISION_PATH / "runs"

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


@handler.add(MessageEvent, message= ImageMessageContent)
def handle_image_message(event):
     with ApiClient(configuration) as api_client:

        # 清空 images 資料夾
        clean_folder(IMAGES_PATH)
        # 清空 YOLO_RESULT_PATH 資料夾
        clean_folder(YOLO_RESULT_PATH)

        # 從LINE取得圖片並儲存至本地
        line_bot_blob_api = MessagingApiBlob(api_client)
        message_content = line_bot_blob_api.get_message_content(message_id=event.message.id)
        save_dir = IMAGES_PATH / f"{event.message.id}.jpg"
        with open(save_dir, "wb") as img_file:
            img_file.write(message_content)

        # 執行物件偵測取得物件數量
        detect_result = default_detect()

        # LLM 回復訊息
        # Get the conversation history
        history = get_history(user_id=event.source.user_id, limit=5)

        # Get the user's question and the agent's response
        question = "圖片內出現以下內容"+ str(detect_result) + "系統提示: 請看使用者需要什麼服務並提供相關資訊，請不要隨意執行未經要求之任務"
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