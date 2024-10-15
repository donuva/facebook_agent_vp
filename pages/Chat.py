import streamlit as st
st.set_page_config(
    page_title="Chatbot",
    page_icon="graphics/icon1.png" 
)
st.logo('graphics/app_logo.png')

from langchain.memory import ConversationBufferMemory
from logicRAG.stream_output import get_gpt_response
from logicRAG.vectorDB.query import query
from logicRAG.vectorDB.indexing import load_index

if 'index' not in st.session_state:
    try:
        st.session_state.index = load_index(filename='data/.cache/faiss_index.bin')
    except Exception as e:
        print('Error loading index', e)

if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

with st.chat_message(avatar=r"graphics\app_logo.png", name="system"):
    st.markdown("© 2024 EDA - VPBank. All rights reserved.")

# Display previous chat history
for message in st.session_state.memory.chat_memory.messages:
    if message["role"] == "assistant" or message["role"] == "user":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

input_text = st.chat_input("Chat with your bot here")


# Stream the response and update the UI
def stream_response(response_generator):
    assistant_message = st.chat_message("ai").empty()  
    streamed_text = "" 

    # Stream each token and update the placeholder
    for chunk in response_generator:   
        streamed_text += chunk 
        assistant_message.write(streamed_text)  # Update the message in real-time
    
    return streamed_text

# When the user inputs a message
if input_text:
    with st.chat_message("user"):
        st.markdown(input_text)

    # Append user's message to the chat history in memory
    st.session_state.memory.chat_memory.add_message({"role": "user", "content": input_text})
    with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    all_chunks = content.split('\n|||')
    all_chunks = [chunk for chunk in all_chunks if chunk.strip()]
    search_results = query(query=input_text, index=st.session_state.index, chunks=all_chunks, top_k=5)
    docs = ''
    for doc in search_results:
        docs += doc
        docs += ' '
    st.session_state.memory.chat_memory.add_message({"role": "system", "content": f"Retrieved Document: {docs}"})
    response_generator = get_gpt_response(st.session_state.memory.load_memory_variables({}), input_text)
    chat_response = stream_response(response_generator)

    st.session_state.memory.chat_memory.add_message({"role": "assistant", "content": chat_response})
