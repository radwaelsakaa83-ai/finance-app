import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random
import plotly.express as px # لإضافة الرسم البياني

# 1. إعدادات الصفحة
st.set_page_config(page_title="AI Finance Master", layout="wide", page_icon="💰")

# 2. الربط بقاعدة البيانات
conn = sqlite3.connect('finance_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS expenses (amount REAL, category TEXT, date TEXT)')
conn.commit()

st.title("💰 AI Finance Master")

# 3. السايد بار (مع خانة المسكن والتاريخ)
st.sidebar.header("📝 إضافة عملية جديدة")
# المسكن هنا هو القيمة الافتراضية اللي بتظهر (value)
income = st.sidebar.number_input("الدخل الشهري الحالي", min_value=1.0, value=15000.0)
amount = st.sidebar.number_input("المبلغ (Amount)", min_value=0.0, value=0.0)
category = st.sidebar.selectbox("الفئة (Category)", ["طعام 🍔", "تسوق 🛍️", "فواتير 📑", "ترفيه 🎮", "أخرى ✨"])
expense_date = st.sidebar.date_input("تاريخ العملية", datetime.now())

if st.sidebar.button("حفظ العملية"):
    if amount > 0:
        c.execute('INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)', 
                  (amount, category, expense_date.strftime("%Y-%m-%d")))
        conn.commit()
        st.sidebar.success("تم حفظ العملية بنجاح! 🎉")
        st.balloons()
        st.rerun()

# 4. معالجة البيانات
df = pd.read_sql_query("SELECT * FROM expenses", conn)
total_spent = df['amount'].sum()
remaining = income - total_spent

# 5. عرض الملخص المالي
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي الدخل", f"{income:,.0f}")
col2.metric("إجمالي المصاريف", f"{total_spent:,.0f}")
col3.metric("المتبقي", f"{remaining:,.0f}")

# 6. الرسم البياني (القرص - Data Analysis)
st.write("---")
if not df.empty:
    st.subheader("📊 تحليل المصاريف حسب الفئة")
    fig = px.pie(df, values='amount', names='category', hole=0.5, 
                 color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("أضف بعض العمليات لعرض الرسم البياني.")

# 7. منطقة ذكاء الـ AI (تعديل شرط ظهور الرسايل الكوميدية)
st.subheader("🔮 نصيحة المساعد الذكي")

messages = [
    "يا بطل، الميزانية بتصوت! 📢 إحنا كدة عدينا نص الدخل.. محتاجين نشد الحزام. 😉",
    "إيه ده! 😱 المصاريف كسبت الدخل 1-0! محتاجين تدخّل سريع. 💸",
    "الميزانية بتقولك 'ارحمني'.. بلاش شوبينج النهاردة وخلينا صحاب. ✨"
]

if total_spent > (income * 0.5): # الرسايل هتظهر لو صرفتي أكتر من نص فلوسك
    st.error(random.choice(messages))
elif remaining > 0:
    st.success("✅ وضعك المالي مستقر حالياً. برافو عليك!")
else:
    st.error("🚨 لقد تجاوزت ميزانيتك بالكامل!")

# 8. عرض السجل
st.write("---")
st.subheader("📜 سجل العمليات")
st.dataframe(df, use_container_width=True)

if st.sidebar.button("🗑️ مسح كل السجل"):
    c.execute("DELETE FROM expenses")
    conn.commit()
    st.rerun()
