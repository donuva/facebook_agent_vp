import os
import requests
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
url = f'https://graph.facebook.com/v20.0/me?access_token={ACCESS_TOKEN}'

response = requests.get(url)
print(response.json())
