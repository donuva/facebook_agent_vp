import openai
import os
import copy
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Khởi tạo client của HuggingFace với token
client = InferenceClient(api_key="")
# (Lưu ý: Token này nên được đặt trong .env thay vì hard-code)

# -------------------------- HÀM: Trả lời bằng GPT (OpenAI) --------------------------
def get_gpt_response(memory_variables, prompt):
    """
    Gửi toàn bộ lịch sử hội thoại đến GPT và stream câu trả lời.
    - memory_variables: dict chứa lịch sử chat
    - prompt: không sử dụng ở đây vì lịch sử đã đầy đủ
    """
    history = memory_variables.get("chat_history", [])

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # Model OpenAI sử dụng
        messages=history,
        stream=True
    )

    full_response = ""
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta'].get('content', '')
        full_response += chunk_message
        yield chunk_message  # Trả từng phần câu trả lời theo luồng

    return history

# -------------------------- HÀM: Tổng hợp các đoạn nội dung --------------------------
def intergrate_context(intergrate_list):
    """
    Nhận danh sách các đoạn văn cần hợp nhất, dùng LLaMA để sinh ra 1 bản tóm tắt bao quát.
    - intergrate_list: danh sách các văn bản string cần tích hợp
    """
    all_content = ""
    for content in intergrate_list:
        all_content += f"One Source is: {content}. "

    prompt = [
        {
            "role": "user",
            "content": all_content + (
                "You need to read current source text and summary of previous source text, "
                "and generate a summary to include them both, covering all important information."
            ),
        }
    ]

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct",
        messages=prompt,
        max_tokens=500,
        stream=False
    )

    return response['choices'][0]['message']['content']

# -------------------------- HÀM: Trả lời bằng LLaMA (có context) --------------------------
def get_llama_response(memory_variables, current_retrived_docs, prompt):
    """
    Gửi lịch sử hội thoại + tài liệu truy xuất mới nhất vào LLaMA để trả lời.
    - memory_variables: dict chứa lịch sử chat
    - current_retrived_docs: nội dung truy xuất từ vectorDB (role="system")
    - prompt: prompt cuối cùng của user (không dùng trực tiếp vì đã nằm trong memory)
    """
    history = memory_variables.get("chat_history", [])
    temp_history = copy.deepcopy(history)
    temp_history.append(current_retrived_docs)  # Thêm context mới vào cuối history

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.2-11B-Vision-Instruct",
        messages=temp_history,
        max_tokens=500,
        stream=True
    )

    full_response = ""
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta'].get('content', '')
        full_response += chunk_message
        yield chunk_message  # Trả từng phần của câu trả lời

    return history
