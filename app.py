import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import plotly.express as px

# 1. إعدادات الصفحة
st.set_page_config(page_title="AI Finance Master", layout="wide", page_icon="💰")

# 2. إضافة خاصية اختيار اللغة في السايد بار
lang = st.sidebar.radio("🌐 Choose Language / اختر اللغة", ("العربية", "English"))

# قاموس الترجمة
texts = {
    "العربية": {
        "title": "💰 مساعد الميزانية الذكي (AI)",
        "income_label": "الدخل الشهري الحالي",
        "amount_label": "المبلغ (Amount)",
        "cat_label": "الفئة (Category)",
        "date_label": "تاريخ العملية",
        "save_btn": "حفظ العملية",
        "total_income": "إجمالي الدخل",
        "total_spent": "إجمالي المصاريف",
        "remaining": "المتبقي",
        "chart_title": "📊 تحليل المصاريف حسب الفئة",
        "ai_title": "🔮 نصيحة المساعد الذكي",
        "history_title": "📜 سجل العمليات",
        "clear_btn": "🗑️ مسح كل السجل",
        "success_msg": "تم الحفظ بنجاح! 🎉",
        "cats": ["طعام 🍔", "تسوق 🛍️", "فواتير 📑", "ترفيه 🎮", "أخرى ✨"],
        "ai_msgs": [
            "يا بطل، الميزانية بتصوت! 📢 إحنا كدة عدينا نص الدخل..",
            "إيه ده! 😱 المصاريف كسبت الدخل 1-0! محتاجين تدخّل سريع.",
            "الميزانية بتقولك 'ارحمني'.. بلاش شوبينج النهاردة."
        ]
    },
    "English": {
        "title": "💰 AI Finance Master",
        "income_label": "Current Monthly Income",
        "amount_label": "Amount",
        "cat_label": "Category",
        "date_label": "Transaction Date",
        "save_btn": "Save Transaction",
        "total_income": "Total Income",
        "total_spent": "Total Spent",
        "remaining": "Remaining",
        "chart_title": "📊 Expense Analysis by Category",
        "ai_title": "🔮 AI Assistant Advice",
        "history_title": "📜 Transaction History",
        "clear_btn": "🗑️ Clear All History",
        "success_msg": "Saved Successfully! 🎉",
        "cats": ["Food 🍔", "Shopping 🛍️", "Bills 📑", "Gaming 🎮", "Others ✨"],
        "ai_msgs": [
            "Hey champ, the budget is screaming! 📢 You spent half your income..",
            "Oops! 😱 Expenses beat Income 1-0! Need urgent intervention.",
            "The budget says 'Mercy please'.. stop shopping for today."
        ]
    }
}

t = texts[lang]

# 3. الربط بقاعدة البيانات
conn = sqlite3.connect('finance_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS expenses (amount REAL, category TEXT, date TEXT)')
conn.commit()

st.title(t["title"])

# 4. السايد بار
st.sidebar.header("📝" if lang == "العربية" else "📝 Entry")
income = st.sidebar.number_input(t["income_label"], min_value=1.0, value=15000.0)
amount = st.sidebar.number_input(t["amount_label"], min_value=0.0, value=0.0)
category = st.sidebar.selectbox(t["cat_label"], t["cats"])
expense_date = st.sidebar.date_input(t["date_label"], datetime.now())

if st.sidebar.button(t["save_btn"]):
    if amount > 0:
        c.execute('INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)', 
                  (amount, category, expense_date.strftime("%Y-%m-%d")))
        conn.commit()
        st.sidebar.success(t["success_msg"])
        st.balloons()
        st.rerun()

# 5. معالجة البيانات وعرض الملخص
df = pd.read_sql_query("SELECT * FROM expenses", conn)
total_spent = df['amount'].sum()
remaining = income - total_spent

col1, col2, col3 = st.columns(3)
col1.metric(t["total_income"], f"{income:,.0f}")
col2.metric(t["total_spent"], f"{total_spent:,.0f}")
col3.metric(t["remaining"], f"{remaining:,.0f}")

# 6. الرسم البياني
st.write("---")
if not df.empty:
    st.subheader(t["chart_title"])
    fig = px.pie(df, values='amount', names='category', hole=0.5)
    st.plotly_chart(fig, use_container_width=True)

# 7. ذكاء الـ AI
st.subheader(t["ai_title"])
if total_spent > (income * 0.5):
    st.warning(random.choice(t["ai_msgs"]))
else:
    st.success("✅ Your budget is stable!" if lang == "English" else "✅ ميزانيتك مستقرة!")

# 8. السجل
st.write("---")
st.subheader(t["history_title"])
st.dataframe(df, use_container_width=True)

if st.sidebar.button(t["clear_btn"]):
    c.execute("DELETE FROM expenses")
    conn.commit()
    st.rerun()
