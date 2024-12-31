import sqlite3
import uuid

conn = sqlite3.connect("vpbank.sqlite")
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS user (id TEXT, name VARCHAR, password VARCHAR, chat TEXT)')
conn.commit()
cur.execute('CREATE TABLE IF NOT EXISTS history (user_id TEXT, role TEXT, message TEXT)')
conn.commit()
#conn.close()

#-----------------------------------------
import streamlit as st
st.set_page_config(
    page_title="Home",
    page_icon="graphics/icon1.png" 
)

st.logo('graphics/app_logo.png')

if "is_login" not in st.session_state or not st.session_state.is_login:
    user = st.text_input("user")
    password = st.text_input("password")
    if st.button("LOGIN"):
        cur.execute('SELECT id from user WHERE name=? AND password=?', (user, password))
        conn.commit()
        id_data = cur.fetchall()
        if not id_data:
            st.title("tài khoản không tồn tại")
        else:
            st.session_state.is_login = True
            st.session_state.id = id_data[0]
            st.session_state.name = user
            st.session_state.password = password
            st.switch_page("pages/Chat.py") 
else:
    cur.execute('SELECT name from user WHERE id=?', (st.session_state.id))
    conn.commit()
    name = cur.fetchall()
    print(name[0][0])
    st.title("BẠN ĐANG ĐĂNG NHẬP!")

#REGISTER
with st.expander("REGISTER"):
    re_user = st.text_input("register user")
    re_password = st.text_input("register password")
    #st.button("SEND!")
    if st.button("SEND!"):
        user_id = str(uuid.uuid4())
        print(user_id)
        cur.execute('INSERT INTO user (id, name, password, chat) VALUES (?,?,?,?)',(user_id, re_user, re_password,"chat"))
        conn.commit()

if st.button("QUIT"):
    st.session_state.is_login = False
    st.session_state.name = None
    # st.session_state.id = None
    st.session_state.password = None
    st.session_state.memory = None
    st.session_state.index = None
    st.switch_page("Home.py")
    print("quit")

#st.button("LOGOUT",type="primary")

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
