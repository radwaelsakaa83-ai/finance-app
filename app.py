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

# إنشاء الجداول لو مش موجودة
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS expenses (username TEXT, amount REAL, category TEXT, date TEXT)')
conn.commit()

# دالة لتشفير الباسورد (عشان الأمان)
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- واجهة تسجيل الدخول وإنشاء الحساب ---
def auth_page():
    st.title("🔐 نظام إدارة الميزانية الذكي")
    choice = st.sidebar.selectbox("القائمة | Menu", ["تسجيل الدخول", "إنشاء حساب جديد"])

    if choice == "تسجيل الدخول":
        st.subheader("تسجيل الدخول")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type='password')
        if st.button("دخول"):
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user_data = c.fetchone()
            if user_data and check_hashes(password, user_data[1]):
                st.session_state['logged_in'] = True
                st.session_state['user'] = username
                st.success(f"مرحباً بك يا {username}")
                st.rerun()
            else:
                st.error("خطأ في الاسم أو الباسورد")

    elif choice == "إنشاء حساب جديد":
        st.subheader("عمل حساب جديد")
        new_user = st.text_input("اختر اسم مستخدم")
        new_password = st.text_input("اختر كلمة مرور", type='password')
        if st.button("تسجيل"):
            if new_user and new_password:
                try:
                    c.execute('INSERT INTO users VALUES (?,?)', (new_user, make_hashes(new_password)))
                    conn.commit()
                    st.success("تم إنشاء الحساب بنجاح! اذهب لتسجيل الدخول")
                except:
                    st.warning("الاسم ده موجود قبل كدة، اختار اسم تاني")

# --- التطبيق الرئيسي ---
def main_app(username):
    st.sidebar.write(f"👤 المستخدم الحالي: **{username}**")
    if st.sidebar.button("تسجيل خروج"):
        st.session_state['logged_in'] = False
        st.rerun()

    lang = st.sidebar.radio("🌐 Language", ("العربية", "English"))
    
    # نصوص اللغات (نفس اللي عملناها)
    texts = {
        "العربية": {
            "title": f"💰 ميزانية {username}",
            "income_label": "دخل الشخصي",
            "amount_label": "المبلغ",
            "cat_label": "الفئة",
            "save_btn": "حفظ",
            "chart_title": "📊 تحليلاتك الشخصية",
            "ai_msgs": ["عديت النص! 😱", "ميزانيتك بتصوت 📢"]
        },
        "English": {
            "title": f"💰 {username}'s Budget",
            "income_label": "Monthly Income",
            "amount_label": "Amount",
            "cat_label": "Category",
            "save_btn": "Save",
            "chart_title": "📊 Your Analysis",
            "ai_msgs": ["Half gone! 😱", "Budget is screaming! 📢"]
        }
    }
    t = texts[lang]
    st.title(t["title"])

    # مدخلات البيانات (بتربط باليوزر نيم)
    income = st.sidebar.number_input(t["income_label"], min_value=1.0, value=10000.0)
    amount = st.sidebar.number_input(t["amount_label"], min_value=0.0)
    category = st.sidebar.selectbox(t["cat_label"], ["طعام 🍔", "تسوق 🛍️", "فواتير 📑", "ترفيه 🎮", "أخرى ✨"])
    
    if st.sidebar.button(t["save_btn"]):
        if amount > 0:
            c.execute('INSERT INTO expenses VALUES (?,?,?,?)', (username, amount, category, datetime.now().strftime("%Y-%m-%d")))
            conn.commit()
            st.balloons()
            st.rerun()

    # استعراض بيانات "هذا المستخدم فقط"
    df = pd.read_sql_query("SELECT * FROM expenses WHERE username = ?", conn, params=(username,))
    
    total_spent = df['amount'].sum()
    col1, col2 = st.columns(2)
    col1.metric("صرفت كام", f"{total_spent:,.0f}")
    col2.metric("باقي كام", f"{income - total_spent:,.0f}")

    if not df.empty:
        st.subheader(t["chart_title"])
        fig = px.pie(df, values='amount', names='category', hole=0.4)
        st.plotly_chart(fig)
        
        if total_spent > (income * 0.5):
            st.warning(random.choice(t["ai_msgs"]))

# --- التحكم في الدخول ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth_page()
else:
    main_app(st.session_state['user'])
