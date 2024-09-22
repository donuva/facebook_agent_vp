import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_gpt_response(memory_variables, prompt):
    # Extract the history (messages) from the memory variables (dict)
    history = memory_variables.get("chat_history", [])

    # Send the chat history to OpenAI's API and stream the response
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  
        messages=history,
        stream=True
    )

    full_response = ""
    for chunk in response:
        chunk_message = chunk['choices'][0]['delta'].get('content', '')
        full_response += chunk_message
        yield chunk_message
    return history
