try:
    import streamlit as st
    from langchain.memory import ConversationBufferMemory
    from RAG_logic.stream_output import get_gpt_response
    from utils.pdf_loader import process_pdf

except Exception as e:
    raise Exception("Error : {}".format(e))

if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")

# Display previous chat history
print(st.session_state.memory.chat_memory.messages)
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

    search_results = process_pdf("data\cong bo thong tin.pdf", input_text)
    for doc in search_results:
        st.session_state.memory.chat_memory.add_message({"role": "system", "content": f"Retrieved Document: {doc}"})


    with st.spinner("Thinking..."):
        response_generator = get_gpt_response(st.session_state.memory.load_memory_variables({}), input_text)
        chat_response = stream_response(response_generator)

    st.session_state.memory.chat_memory.add_message({"role": "assistant", "content": chat_response})
