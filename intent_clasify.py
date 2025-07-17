# intent_classify.py

import os
import json
from typing import List, Dict

from groq import Groq
from dotenv import load_dotenv
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
IntentsType = List[str]


def classify_intent_llm(text: str, intents: IntentsType) -> Dict[str, float]:# CẦN THỀM EXAMPLE FEW-SHOT
 
    prompt = (
        "Bạn là bộ phân loại intent. Hãy đánh giá độ liên quan "
        "giữa câu hỏi dưới đây và các intent đã cho.\n\n"
        f"Câu hỏi: \"{text}\"\n"
        f"Danh sách intent: {', '.join(intents)}\n\n"
        "Trả về đúng JSON object mapping mỗi intent với một số thực từ 0 đến 1, "
        "ví dụ:\n"
        '{"Account Types": 0.9, "Card Types": 0.9, "Online Services (Business)": 0.9}\n'
        "Không thêm giải thích hay text khác." \
        "70 /%/ các lần trả về phải có ít nhất 1 intent có độ tin cậy > 0.9!"
    )

    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
   
    content = resp.choices[0].message.content.strip()

    try:
        scores = json.loads(content)
    except json.JSONDecodeError:
        scores = {}
    return scores




intents = [
    "Account Types",
    "Card Types",
    "Online Services (Business)",
]

# text = input("Nhập câu hỏi: ")
# llm_scores = classify_intent_llm(text, intents)

# print("\n=== Kết quả classify_intent_llm (llama-3.1-8b-instant) ===")
# print(llm_scores)


