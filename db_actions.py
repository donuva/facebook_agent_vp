# db_actions.py

import sqlite3
import datetime
import pandas as pd

DB_PATH = 'mainboard.db'

# ====== TẠO BẢNG ======
def create_db():
    conn = sqlite3.connect(DB_PATH)
    # Thêm cột is_bot_reply vào bảng nếu chưa có
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mainboard (
            fb_comment_id TEXT PRIMARY KEY,
            date TEXT,
            campaign TEXT,
            user TEXT,
            question TEXT,
            answer TEXT,
            confidence REAL,
            url TEXT,
            admin_reply TEXT,
            handled INTEGER,
            rating INTEGER,
            feedback TEXT,
            admin_note TEXT,
            intent TEXT,
            last_editor TEXT,
            last_edit_time TEXT,
            edit_log TEXT,
            search TEXT,
            is_bot_reply INTEGER DEFAULT 0, 
            response_time REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


# ====== HÀM LƯU CƠ BẢN (nhận tin mới) ======
def insert_message(fb_comment_id, date, user, question, campaign=None, url=None, is_bot_reply=True):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT OR IGNORE INTO mainboard 
        (fb_comment_id, date, user, question, campaign, url, is_bot_reply)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (fb_comment_id, date, user, question, campaign, url, is_bot_reply))
    conn.commit()
    conn.close()

# ====== HÀM UPDATE KẾT QUẢ LLM ======
def update_llm_result(fb_comment_id, answer, confidence, intent, is_bot_reply=True, response_time=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        UPDATE mainboard SET answer=?, confidence=?, intent=?, is_bot_reply=?, response_time=?
        WHERE fb_comment_id=?
    ''', (answer, confidence, intent, is_bot_reply, response_time, fb_comment_id))
    conn.commit()
    conn.close()


# ====== HÀM UPDATE KHI ADMIN CHỈNH SỬA ======
def update_admin_fields(
    fb_comment_id, 
    admin_reply=None, handled=None, rating=None, feedback=None, admin_note=None,
    last_editor=None, is_bot_reply=None
):
    conn = sqlite3.connect(DB_PATH)
    now = datetime.datetime.now().isoformat()
    fields = []
    values = []
    if admin_reply is not None:
        fields.append('admin_reply=?')
        values.append(admin_reply)
    if handled is not None:
        fields.append('handled=?')
        values.append(int(handled))
    if rating is not None:
        fields.append('rating=?')
        values.append(rating)
    if feedback is not None:
        fields.append('feedback=?')
        values.append(feedback)
    if admin_note is not None:
        fields.append('admin_note=?')
        values.append(admin_note)
    if last_editor is not None:
        fields.append('last_editor=?')
        values.append(last_editor)
        fields.append('last_edit_time=?')
        values.append(now)
        # Tự động ghi thêm vào edit_log
        conn.execute(''' 
            UPDATE mainboard SET edit_log = COALESCE(edit_log, '') || ? WHERE fb_comment_id=? 
        ''', (f"\n{now} - {last_editor} edited.", fb_comment_id))
    
    if is_bot_reply is not None:
        fields.append('is_bot_reply=?')
        values.append(is_bot_reply)

    # Cập nhật các trường
    if fields:
        sql = f"UPDATE mainboard SET {', '.join(fields)} WHERE fb_comment_id=?"
        values.append(fb_comment_id)
        conn.execute(sql, tuple(values))
        conn.commit()
    conn.close()


# ====== HÀM UPDATE TRƯỜNG ĐƠN LẺ (VD: chỉ intent, hoặc handled,...) ======
def update_single_field(fb_comment_id, field, value):
    conn = sqlite3.connect(DB_PATH)
    sql = f"UPDATE mainboard SET {field}=? WHERE fb_comment_id=?"
    conn.execute(sql, (value, fb_comment_id))
    conn.commit()
    conn.close()

# ====== HÀM UPDATE SEARCH FIELD ======
def update_search(fb_comment_id, search):
    update_single_field(fb_comment_id, "search", search)

# ====== LOAD TOÀN BỘ DỮ LIỆU (Pandas DataFrame) ======
def load_all():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql('SELECT * FROM mainboard', conn)
    conn.close()
    return df

# ====== LOAD LỌC DỮ LIỆU THEO ĐIỀU KIỆN (VD: handled, date...) ======
def load_filtered(**kwargs):
    # kwargs là các trường filter, ví dụ: handled=1, date="2024-07-15"
    conn = sqlite3.connect(DB_PATH)
    where = []
    vals = []
    for k, v in kwargs.items():
        where.append(f"{k}=?")
        vals.append(v)
    where_sql = " AND ".join(where) if where else "1=1"
    sql = f"SELECT * FROM mainboard WHERE {where_sql}"
    df = pd.read_sql(sql, conn, params=vals)
    conn.close()
    return df

# ====== XÓA 1 DÒNG (nếu cần) ======
def delete_by_id(fb_comment_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM mainboard WHERE fb_comment_id=?', (fb_comment_id,))
    conn.commit()
    conn.close()

# ====== ĐẾM SỐ LƯỢNG (ví dụ: câu chưa xử lý, hoặc câu khó) ======
def count_by_condition(**kwargs):
    conn = sqlite3.connect(DB_PATH)
    where = []
    vals = []
    for k, v in kwargs.items():
        where.append(f"{k}=?")
        vals.append(v)
    where_sql = " AND ".join(where) if where else "1=1"
    sql = f"SELECT COUNT(*) FROM mainboard WHERE {where_sql}"
    cur = conn.execute(sql, vals)
    count = cur.fetchone()[0]
    conn.close()
    return count

# ====== HÀM RESET BẢNG (xóa hết) ======
def clear_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM mainboard')
    conn.commit()
    conn.close()

# ====== ĐẢM BẢO KHỞI TẠO BẢNG KHI IMPORT MODULE ======
create_db()
