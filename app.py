import streamlit as st
import pandas as pd
import altair as alt
import sqlite3
import io
from datetime import datetime, date

# --- 1. Database Setup ---
conn = sqlite3.connect('finance_master_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS expenses (category TEXT, amount REAL, date DATE)')
conn.commit()

# --- 2. CSS for Professional Look ---
st.set_page_config(page_title="AI Finance Master", layout="wide")
st.markdown("""
    <style>
        .stProgress > div > div > div > div { background-image: linear-gradient(to right, #4caf50, #81c784); }
        .main { background-color: #f9fbfd; }
        .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Language & Sidebar ---
lang = st.sidebar.selectbox("🌐 Choose Language / اختر اللغة", ["العربية", "English"])

if lang == "العربية":
    t = {
        "title": "💸 المساعد المالي الذكي (AI Driver)",
        "income": "الدخل الشهري", "goal": "هدف الادخار", "add": "إضافة عملية جديدة",
        "history": "📜 سجل المصاريف", "ai_box": "🔮 تحليل الذكاء الاصطناعي",
        "cats": ["🍔 طعام", "🚗 مواصلات", "🏠 سكن", "🛍️ تسوق", "✨ أخرى"],
        "download": "📥 تحميل تقرير الإكسيل", "clear": "🗑️ مسح البيانات"
    }
else:
    t = {
        "title": "💸 AI Financial Assistant",
        "income": "Monthly Income", "goal": "Savings Goal", "add": "Add New Transaction",
        "history": "📜 Expense Log", "ai_box": "🔮 AI Insights & Prediction",
        "cats": ["🍔 Food", "🚗 Transport", "🏠 Housing", "🛍️ Shopping", "✨ Other"],
        "download": "📥 Download Excel Report", "clear": "🗑️ Clear All Data"
    }

st.sidebar.header(t["add"])
income = st.sidebar.number_input(t["income"], value=15000)
savings_goal = st.sidebar.number_input(t["goal"], value=2000)

with st.sidebar.form("input_form"):
    amt = st.number_input("المبلغ / Amount", min_value=0.0)
    cat = st.selectbox("الفئة / Category", t["cats"])
    dt = st.date_input("التاريخ / Date", date.today())
    if st.form_submit_button("حفظ / Save"):
        if amt > 0:
            c.execute('INSERT INTO expenses VALUES (?, ?, ?)', (cat, amt, dt))
            conn.commit()
            st.rerun()

# --- 4. Data Processing (Pandas) ---
df = pd.read_sql_query('SELECT * FROM expenses ORDER BY date DESC', conn)
df['date'] = pd.to_datetime(df['date'])

if not df.empty:
    df['Month'] = df['date'].dt.strftime('%B %Y')
    selected_month = st.sidebar.selectbox("📅 Month / الشهر", df['Month'].unique())
    f_df = df[df['Month'] == selected_month].copy()

    total_spent = f_df['amount'].sum()
    remaining = income - total_spent
    progress_val = min(remaining / (income - savings_goal), 1.0) if income > savings_goal else 0

    # --- AI Logic (The Core) ---
    today_day = date.today().day
    daily_avg = total_spent / today_day if today_day > 0 else 0
    est_end_day = income / daily_avg if daily_avg > 0 else 30

    # --- 5. Main UI Display ---
    st.title(t["title"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["income"], f"{income:,} ج.م")
    c2.metric("المصروفات", f"{total_spent:,} ج.م", delta=f"-{total_spent}")
    c3.metric("المتبقي", f"{remaining:,} ج.م")

    st.subheader("🎯 حالة الادخار")
    st.progress(progress_val)
    st.write("---")

    col_main, col_side = st.columns([1.2, 0.8])

    with col_main:
        st.subheader(t["ai_box"])
        # هنا النصيحة والذكاء الاصطناعي (AI Insights)
        if total_spent > 0:
            if est_end_day < 25:
                st.error(f"🚨 **توقيع ذكي:** ميزانيتك قد تنتهي يوم **{int(est_end_day)}** في الشهر.")
                st.warning(
                    "💡 **نصيحة AI:** معدل صرفك اليومي مرتفع ({:.0f} ج.م). حاول تقليل مصاريف 'التسوق' بنسبة 15%.".format(
                        daily_avg))
            else:
                st.success("🌟 **تحليل AI:** وضعك المالي مستقر جداً. معدل صرفك يسمح لك بالادخار.")
                st.info(f"💡 **اقتراح جمعيتي:** يمكنك الالتزام بجمعية بقيمة {remaining * 0.4:.0f} ج.م الشهر القادم.")

        st.subheader(t["history"])
        st.dataframe(f_df[['date', 'category', 'amount']], use_container_width=True)

        # Excel Download Button
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            f_df.to_excel(writer, index=False)
        st.download_button(t["download"], buffer.getvalue(), f"Report_{selected_month}.xlsx")

    with col_side:
        st.subheader("📊 توزيع المصاريف")
        chart = alt.Chart(f_df).mark_arc(innerRadius=60).encode(theta="amount", color="category")
        st.altair_chart(chart, use_container_width=True)

else:
    st.title(t["title"])
    st.info("أهلاً بك! ابدأ بإضافة أول مصروف لتفعيل تحليلات الذكاء الاصطناعي.")

if st.sidebar.button(t["clear"]):
    c.execute('DELETE FROM expenses');
    conn.commit();
    st.rerun()