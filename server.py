import os
from db_actions import insert_message, update_llm_result
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from llm_answer import *           # cần: facebook_response(message) trả về (ans, conf, intent)
from dotenv import load_dotenv
import uvicorn
from facebook_action import *      # reply_to_message, reply_to_comment, get_post_info

load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

app = FastAPI()

CONFIDENCE_THRESHOLD = 0.75

@app.api_route("/webhook", methods=["GET", "POST"])
async def webhook(request: Request):
    if request.method == "GET":
        params = request.query_params
        if (
            params.get("hub.mode") == "subscribe"
            and params.get("hub.verify_token") == VERIFY_TOKEN
        ):
            print("ĐÃ XÁC THỰC WEBHOOK")
            return PlainTextResponse(params.get("hub.challenge"), status_code=200)
        return PlainTextResponse("Verification token mismatch", status_code=403)

    if request.method == "POST":
        import datetime
        data = await request.json()
        print("ĐÃ NHẬN POST FB GỬI TỚI WEBHOOK")
        print("Received event: ", data)

        for entry in data.get("entry", []):
            # Xử lý inbox message
            for message_event in entry.get("messaging", []):
                sender_id = message_event.get("sender", {}).get("id")
                message = message_event.get("message", {}).get("text")
                mid = message_event.get("message", {}).get("mid")     # FB message unique id
                date = datetime.datetime.now().isoformat()
                # ---- XỬ LÝ INBOX ----
                if sender_id != PAGE_ID and message:
                    print(message)
                    # 1. Lưu vào DB
                    insert_message(
                        fb_comment_id=mid,
                        date=date,
                        user=sender_id,
                        question=message,
                        is_bot_reply=False
                    )
                    # 2. Gọi LLM để lấy answer, confidence, intent
                    ans, conf, intent = facebook_response(message)  # Bạn cần chỉnh llm_answer.py trả tuple này
                    # 3. Update vào DB
                    is_bot_reply = (conf >= CONFIDENCE_THRESHOLD)
                    response_time = (datetime.datetime.now() - datetime.datetime.fromisoformat(date)).total_seconds()
                    update_llm_result(mid, ans, conf, intent, is_bot_reply, response_time)
                    # 4. Trả lời lại FB
                    if conf >= CONFIDENCE_THRESHOLD:
                        reply_to_message(sender_id, ans)

            # Xử lý comment feed
            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})
                item = value.get("item")
                verb = value.get("verb")
                comment_id = value.get("comment_id")
                from_id = value.get("from", {}).get("id")
                comment = value.get("message")
                post_id = value.get("post_id")
                date = datetime.datetime.now().isoformat()
                # ---- XỬ LÝ COMMENT ----
                if from_id != PAGE_ID and field == "feed" and verb == "add" and item == "comment" and comment_id:
                    print(post_id)
                    # 1. Lưu vào DB
                    insert_message(
                        fb_comment_id=comment_id,
                        date=date,
                        user=from_id,
                        question=comment,
                        campaign = get_campaign(get_post_content(post_id)),
                        url=f"https://facebook.com/{post_id}",
                        is_bot_reply=False
                    )
                    # 2. Gọi LLM để lấy answer, confidence, intent
                    ans, conf, intent = facebook_response(comment)
                    # 3. Update vào DB
                    is_bot_reply = (conf >= CONFIDENCE_THRESHOLD)
                    response_time = (datetime.datetime.now() - datetime.datetime.fromisoformat(date)).total_seconds()
                    update_llm_result(comment_id, ans, conf, intent, is_bot_reply, response_time)
                    # 4. Trả lời lại FB
                    if conf >= CONFIDENCE_THRESHOLD:
                        reply_to_comment(comment_id, ans)

        return PlainTextResponse("EVENT_RECEIVED", status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
