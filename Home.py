import sqlite3
import uuid
import streamlit as st
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# ----------------------- Khởi tạo cơ sở dữ liệu -----------------------
def init_db():
    connection = sqlite3.connect("vpbank.sqlite")
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id TEXT PRIMARY KEY,
            name TEXT,
            password TEXT,
            chat TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            user_id TEXT,
            role TEXT,
            message TEXT
        )
    ''')
    connection.commit()
    return connection, cursor

# ----------------------- Cấu hình giao diện Streamlit -----------------------
st.set_page_config(page_title="Home", page_icon="graphics/icon1.png")
st.logo('graphics/app_logo.png')

# ----------------------- Xử lý đăng nhập -----------------------
def login(cursor):
    username = st.text_input("Tên đăng nhập")
    password = st.text_input("Mật khẩu", type="password")
    
    if st.button("ĐĂNG NHẬP"):
        cursor.execute('SELECT id FROM user WHERE name=? AND password=?', (username, password))
        user_data = cursor.fetchone()
        
        if not user_data:
            st.error("Tài khoản không tồn tại.")
        else:
            st.session_state.is_login = True
            st.session_state.id = user_data[0]
            st.session_state.name = username
            st.session_state.password = password
            st.switch_page("pages/Chat.py")

# ----------------------- Hiển thị trạng thái đăng nhập -----------------------
def show_logged_in(cursor):
    cursor.execute('SELECT name FROM user WHERE id=?', (st.session_state.id,))
    user_info = cursor.fetchone()
    if user_info:
        st.success(f"Đang đăng nhập dưới tên: {user_info[0]}")
    else:
        st.warning("Không tìm thấy người dùng.")

# ----------------------- Xử lý đăng ký tài khoản mới -----------------------
def register(cursor, connection):
    with st.expander("Đăng ký tài khoản mới"):
        register_user = st.text_input("Tài khoản mới")
        register_password = st.text_input("Mật khẩu mới", type="password")
        
        if st.button("TẠO TÀI KHOẢN"):
            new_user_id = str(uuid.uuid4())
            cursor.execute('''
                INSERT INTO user (id, name, password, chat)
                VALUES (?, ?, ?, ?)
            ''', (new_user_id, register_user, register_password, "chat"))
            connection.commit()
            st.success("Tạo tài khoản thành công!")

# ----------------------- Xử lý đăng xuất -----------------------
def logout():
    if st.button("THOÁT"):
        st.session_state.clear()
        st.switch_page("Home.py")

# ----------------------- Hiển thị chân trang -----------------------
def show_footer():
    st.markdown("""
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
    """, unsafe_allow_html=True)

# ----------------------- Luồng chạy chính của ứng dụng -----------------------
def main():
    connection, cursor = init_db()
    
    if not st.session_state.get("is_login", False):
        login(cursor)
    else:
        show_logged_in(cursor)
    
    register(cursor, connection)
    logout()
    show_footer()

if __name__ == "__main__":
    main()
