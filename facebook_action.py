import os
import requests
from dotenv import load_dotenv
load_dotenv()
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

# print(PAGE_ACCESS_TOKEN)
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

def get_post_info(post_id):
    url = f"https://graph.facebook.com/v23.0/{post_id}"
    fields = "message, story, created_time, permalink_url, attachments"
    params = {
        "fields": fields,
        "access_token": PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"LỖI KHI LẤY BÀI VIẾT: {e}")
        return {}
    
def get_campaign(text): #lấy tên hastash làm tên campaign
    campaign_list = []

    for word in text.split(" "):
        if "#" in word:
            campaign_list.append(word.split("#")[1])

    return campaign_list

def confidence_score(question, answer):#few_shot + random sampling
    pass


print(get_post_info(200090973179526_122233803668150598))

