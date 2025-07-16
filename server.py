import requests
import os
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from llm_answer import *
from dotenv import load_dotenv
import uvicorn
from facebook_action import *
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

app = FastAPI()

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
        data = await request.json()
        print("ĐÃ NHẬN POST FB GỬI TỚT WEBHOOK")
        print("Received event: ", data)

        for entry in data.get("entry", []):
            for message_event in entry.get("messaging", []):
                sender_id = message_event.get("sender", {}).get("id")
                message = message_event.get("message", {}).get("text")
                if sender_id != PAGE_ID and message:
                    print(message)
                    reply_to_message(sender_id, facebook_response(message))

            for change in entry.get("changes", []):
                field = change.get("field")
                value = change.get("value", {})
                item = value.get("item")
                verb = value.get("verb")
                comment_id = value.get("comment_id")
                from_id = value.get("from", {}).get("id")
                comment = value.get("message")
                post_id = value.get("post_id")

                print(field, verb, item)
                if from_id != PAGE_ID and field == "feed" and verb == "add" and item == "comment" and comment_id:
                    print(get_post_info(post_id))
                    reply_to_comment(comment_id, facebook_response(comment))

        return PlainTextResponse("EVENT_RECEIVED", status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
    
# import requests
# import os
# from flask import Flask, request
# from dotenv import load_dotenv
# from facebook_action import *
# load_dotenv()

# VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
# PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
# PAGE_ID = os.getenv("PAGE_ID")

# app = Flask(__name__)

# @app.route('/webhook', methods=['GET', 'POST'])
# def webhook():
#     if request.method == 'GET':
#         # Xác thực với Facebook khi setup webhook
#         if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
#             print("ĐÃ XÁC THỰC WEBHOOK")
#             return request.args.get("hub.challenge"), 200
#         return "Verification token mismatch", 403

#     if request.method == 'POST':
#         data = request.get_json()
#         print("ĐÃ NHẬN POST FB GỬI TỚT WEBHOOK")
#         print("Received event: ", data)
#         # Xử lý dữ liệu comment, message
#         for entry in data.get('entry', []):
#             #process for message
#             for message_event in entry.get('messaging', []):
#                 sender_id = message_event.get('sender',{}).get('id')
#                 message = message_event.get('message',{}).get('text')
#                 if sender_id and message:
#                     reply_to_message(sender_id, "VPBANK XIN CHÀO")
        
#             #process for comment
#             for change in entry.get('changes', []):
#                 field = change.get('field')
#                 value = change.get('value',{})
#                 item = value.get('item')
#                 verb = value.get('verb')
#                 comment_id = value.get('comment_id')
#                 message = value.get('message')
#                 from_id = value.get('from',{}).get('id')
#                 comment = value.get('message')

#                 print(field, verb, item)
#                 if from_id != PAGE_ID and field == 'feed' and verb == 'add' and item == 'comment' and comment_id:
#                     reply_to_comment(comment_id, "VPBANK XIN CHÀO")


#         return "EVENT_RECEIVED", 200

# if __name__ == '__main__':
#     app.run(port=5000, debug=True)
