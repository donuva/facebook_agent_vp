import streamlit as st
import sqlite3

conn = sqlite3.connect("vpbank.sqlite")
cur = conn.cursor()
#
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
#
if "is_login" not in st.session_state or not st.session_state.is_login:
    st.warning("CHƯA ĐĂNG NHẬP")
    st.switch_page("Home.py")

#
st.set_page_config(
    page_title="Chatbot",
    page_icon="graphics/icon1.png" 
)
st.logo('graphics/app_logo.png')

options = st.multiselect(
    "Search in which database:",
    ["Mail Database", "Default Database", "Drive Database"],
)

from langchain.memory import ConversationBufferMemory
from logicRAG.stream_output import get_gpt_response, get_llama_response, intergrate_context
from logicRAG.vectorDB.query import query
from logicRAG.vectorDB.indexing import load_index

#if hasn't load index_db yet then load it
# if 'index' not in st.session_state or st.session_state.index == None:
#     try:
#         st.session_state.index = load_index(filename='data/.cache/faiss_index.bin')
#     except Exception as e:
#         print('Error loading index', e)

if "Mail Database" in options: Mail_index = load_index(filename='data/.cache/faiss_Mail_index.bin')
if "Default Database" in options: Default_index = load_index(filename='data/.cache/faiss_Default_index.bin')
if "Drive Database" in options: Drive_index = load_index(filename='data/.cache/faiss_Drive_index.bin')

if 'memory' not in st.session_state or st.session_state.memory == None:
    st.session_state.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

with st.chat_message(avatar=r"graphics\app_logo.png", name="system"):
    st.markdown("© 2024 EDA - VPBank. All rights reserved.")

# Display previous chat history
cur.execute('SELECT user_id, role, message from history WHERE user_id=?', (st.session_state.id))
conn.commit()
exist_chat = cur.fetchall()
for chat in exist_chat:
    role = chat[1]
    message = chat[2]
    if role == "assistant" or role == "user":
        with st.chat_message(role):
            st.markdown(message)

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

def answer_proccess(input_text, indexdb, all_chunks):
    search_results = query(query=input_text, index=indexdb, chunks=all_chunks, top_k=15)    
    #Sử dụng phương pháp Chain of Agents để nâng cái top_k lên -> search toàn diện hơn
    # Chia nhỏ chunk_list , Chain of Agents, Summarize dần dần
    docs = ""
    current_summary = ""
    sum_step = 0
    for doc in search_results:
        docs += doc
        docs += ' '
        if len(docs) > 2000:
            sum_step += 1
            print(sum_step)
            new_summary = intergrate_context([docs, current_summary])
            current_summary = new_summary
            docs = ""
        
    print("TOP_K NEAREST IS : ", docs)
    #print("TEST TEST TEST ", current_summary)
    #KHÔNG NHỚ Retrieved Document NỮA, ĐỂ NẶNG BỘ NHỚ , CHỈ NHỚ QUESTION CỦA USER & ANSWER CỦA ASSISTANT & current retrived docs
    #st.session_state.memory.chat_memory.add_message({"role": "system", "content": f"Retrieved Document: {docs}"})
    current_retrived_summary = {"role": "system", "content": f"Retrieved Document: {current_summary}"}
    response_generator = get_llama_response(st.session_state.memory.load_memory_variables({}), current_retrived_summary, input_text)
    
    response_text = ""
    for chunk in response_generator:
        response_text += chunk 
   
    return response_text
    
    
# When the user inputs a message
if input_text:
    with st.chat_message("user"):
        st.markdown(input_text)
        # cur.execute('CREATE TABLE IF NOT EXISTS history (user_id TEXT, role TEXT, message TEXT)')
        # conn.commit()
    #UPDATE USER MESSAGE
        cur.execute("INSERT INTO history (user_id, role, message) VALUES (?,?,?)", (st.session_state.id[0], "user", input_text) )   
        conn.commit()
    # Append user's message to the chat history in memory
    st.session_state.memory.chat_memory.add_message({"role": "user", "content": input_text})
    with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    all_chunks = content.split('\n|||')
    all_chunks = [chunk for chunk in all_chunks if chunk.strip()]


    #BEGIN WHOLE SEARCH PROCCESS IN 1 SPECIFIC INDEX_DB 
    pre_answer_list = []
    if "Mail Database" in options: 
        pre_answer1 = answer_proccess(input_text, Mail_index, all_chunks)
        pre_answer_list.append(pre_answer1)
    if "Default Database" in options: 
        pre_answer2 = answer_proccess(input_text, Default_index, all_chunks)
        pre_answer_list.append(pre_answer2)
    if "Drive Database" in options: 
        pre_answer3 = answer_proccess(input_text, Drive_index, all_chunks)
        pre_answer_list.append(pre_answer3)

    # for answer in pre_answer_list:
    #     print("PRE ANSWER IS    :   ", answer)  

    final_answer = intergrate_context(pre_answer_list)   
    assistant_message = st.chat_message("ai").empty()
    assistant_message.write(final_answer) 
    # chat_response = stream_response(final_answer)

    # # #UPDATE RESPONSE MESSAGE: ĐANG KHÔNG UPDATE LƯU LỊCH SỬ TRẢ LỜI CỦA BOT VÌ LLaMA-VISION free input không quá 4069 token
    # # cur.execute("INSERT INTO history (user_id, role, message) VALUES (?,?,?)", (st.session_state.id[0], "assistant", chat_response) )   
    # # conn.commit()
    st.session_state.memory.chat_memory.add_message({"role": "assistant", "content": final_answer})
