from pages import Data, Chat
import streamlit as st

st.set_page_config(
    page_title="Home",
    page_icon="graphics/icon1.png" 
)

st.logo('graphics/app_logo.png')

footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #333;
    }
    </style>
    <div class="footer">
        <p>© 2024 EDA - VPBank. All rights reserved.</p>
    </div>
    """
st.markdown(footer, unsafe_allow_html=True)
