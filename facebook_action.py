import os
import requests
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

def reply_to_message(sender_id, text):
    url = 'https://graph.facebook.com/v23.0/me/messages'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    payload = {
        'recipient': {'id': sender_id},
        'message':{'text': text}
    }
    r = requests.post(url, params=params, json=payload)
    print(f"ĐẪ TRẢ LỜI MESSAGE là {r.text}")

def reply_to_comment(comment_id, text):
    url = f'https://graph.facebook.com/v23.0/{comment_id}/comments'
    params = {'access_token': PAGE_ACCESS_TOKEN}
    payload = {
        'message':text
    }
    r = requests.post(url, params=params, json=payload)
    print(f"ĐẪ TRẢ LỜI COMMENT là {r.text}")