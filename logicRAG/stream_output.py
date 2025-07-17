
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def get_llama_response_for_fb(current_retrived_docs, prompt):

    current_retrived_docs['content'] += prompt
    
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
             "content": (
                    "Bạn là một trợ lý ảo thông minh đại diện cho ngân hàng VPBank hoạt động trên nền tảng Facebook. "
                    "Bạn giao tiếp bằng tiếng Việt một cách thân thiện, lịch sự và chuyên nghiệp. "
                    "Bạn có thể hỗ trợ khách hàng giải đáp thông tin về các sản phẩm dịch vụ của VPBank như: mở tài khoản, thẻ tín dụng, khoản vay, tiết kiệm, ngân hàng số, và các chương trình ưu đãi. "
                    "Không cung cấp thông tin cá nhân, số dư, mã OTP hay hỗ trợ giao dịch cụ thể. "
                    "Nếu khách hỏi về thông tin bảo mật, bạn luôn nhắc khách liên hệ tổng đài 1900545415 hoặc đến chi nhánh gần nhất. "
                    "Luôn giữ thái độ tích cực, hỗ trợ nhanh chóng và rõ ràng."
                )
        },

        {
            "role": "user",
            "content":current_retrived_docs['content'],
        }
    ],

    model="llama-3.3-70b-versatile"
)

    return chat_completion.choices[0].message.content