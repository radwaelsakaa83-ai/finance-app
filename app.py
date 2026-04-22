import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import plotly.express as px
import hashlib

# 1. إعدادات الصفحة
st.set_page_config(page_title="AI Finance System", layout="wide", page_icon="👥")

# --- إدارة قاعدة البيانات ---
conn = sqlite3.connect('finance_pro.db', check_same_thread=False)
c = conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses (username TEXT, amount REAL, category TEXT, date TEXT)')

try:
    c.execute('ALTER TABLE expenses ADD COLUMN username TEXT')
except:
    pass
conn.commit()

# دالة لتشفير الباسورد
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- واجهة تسجيل الدخول وإنشاء الحساب ---
def auth_page():
    st.title("🔐 نظام إدارة الميزانية الذكي")
    st.markdown("---")

    choice = st.sidebar.selectbox("القائمة | Menu", ["تسجيل الدخول", "إنشاء حساب جديد"])

    if choice == "تسجيل الدخول":
        st.subheader("تسجيل الدخول")
        username = st.text_input("اسم المستخدم (Username)")
        password = st.text_input("كلمة المرور (Password)", type='password')
        if st.button("دخول | Login"):
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_data = c.fetchone()
            if user_data and check_hashes(password, user_data[1]):
                st.session_state['logged_in'] = True
                st.session_state['user'] = username
                st.success(f"مرحباً بك يا {username}")
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة ❌")

    elif choice == "إنشاء حساب جديد":
        st.subheader("عمل حساب جديد")
        new_user = st.text_input("اختر اسم مستخدم")
        new_password = st.text_input("اختر كلمة مرور", type='password')
        if st.button("تسجيل حساب | Register"):
            if new_user and new_password:
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (new_user, make_hashes(new_password)))
                    conn.commit()
                    st.success("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول")
                except:
                    st.warning("اسم المستخدم هذا مسجل بالفعل")

# --- التطبيق الرئيسي ---
def main_app(username):
    st.sidebar.write(f"👤 المستخدم: **{username}**")
    if st.sidebar.button("تسجيل خروج | Logout"):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.rerun()

    lang = st.sidebar.radio("🌐 Language / اللغة", ("العربية", "English"))

    texts = {
        "العربية": {
            "title": f"💰 ميزانية {username}",
            "income_label": "الدخل الشهري",
            "amount_label": "المبلغ المراد تسجيله",
            "cat_label": "الفئة",
            "save_btn": "حفظ العملية",
            "total_income": "إجمالي الدخل",
            "total_spent": "إجمالي المصاريف",
            "remaining": "المتبقي",
            "chart_title": "📊 تحليل مصاريفك الشخصية",
            "ai_title": "🔮 نصيحة المساعد الذكي",
            "history_title": "📜 سجل عملياتك",
            "clear_btn": "🗑️ مسح كل السجل",
            "success_msg": "تم الحفظ! 🎉",
            "cats": ["طعام 🍔", "تسوق 🛍️", "سكن 🏠", "فواتير 📑", "ترفيه 🎮", "أخرى ✨"],
            "ai_msgs": ["يا بطل، الميزانية بتصوت!", "😱 المصاريف كسبت!", "ارحمني من الشوبينج!"]
        },
        "English": {
            "title": f"💰 {username}'s Budget",
            "income_label": "Monthly Income",
            "amount_label": "Amount",
            "cat_label": "Category",
            "save_btn": "Save Transaction",
            "total_income": "Total Income",
            "total_spent": "Total Spent",
            "remaining": "Remaining",
            "chart_title": "📊 Your Expense Analysis",
            "ai_title": "🔮 AI Assistant Advice",
            "history_title": "📜 Transaction History",
            "clear_btn": "🗑️ Clear History",
            "success_msg": "Saved Successfully! 🎉",
            "cats": ["Food 🍔", "Shopping 🛍️", "Bills 📑", "Gaming 🎮", "Others ✨"],
            "ai_msgs": ["Budget is screaming!", "Expenses won 1-0!", "Stop shopping!"]
        }
    }
    t = texts[lang]
    st.title(t["title"])

    income = st.sidebar.number_input(t["income_label"], min_value=1.0, value=10000.0)
    amount = st.sidebar.number_input(t["amount_label"], min_value=0.0)
    category = st.sidebar.selectbox(t["cat_label"], t["cats"])

    if st.sidebar.button(t["save_btn"]):
        if amount > 0:
            c.execute('INSERT INTO expenses VALUES (?,?,?,?)', (username, amount, category, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.sidebar.success(t["success_msg"])
            st.balloons()
            st.rerun()

    df = pd.read_sql_query("SELECT * FROM expenses WHERE username = ?", conn, params=(username,))
    total_spent = df['amount'].sum()
    remaining = income - total_spent

    col1, col2, col3 = st.columns(3)
    col1.metric(t["total_income"], f"{income:,.0f}")
    col2.metric(t["total_spent"], f"{total_spent:,.0f}")
    col3.metric(t["remaining"], f"{remaining:,.0f}")

    if not df.empty:
        st.subheader(t["chart_title"])
        fig = px.pie(df, values='amount', names='category', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
        if total_spent > (income * 0.5):
            st.warning(random.choice(t["ai_msgs"]))

    st.subheader(t["history_title"])
    st.dataframe(df, use_container_width=True)

    if st.sidebar.button(t["clear_btn"]):
        c.execute("DELETE FROM expenses WHERE username = ?", (username,))
        conn.commit()
        st.rerun()

# --- التحكم في الدخول النهائي ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

if not st.session_state['logged_in']:
    auth_page()
else:
    main_app(st.session_state['user'])
