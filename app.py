import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import random

# محاولة استيراد مكتبة الإشعارات
try:
    from plyer import notification
except:
    pass

# 1. إعدادات الصفحة
st.set_page_config(page_title="AI Finance Master", layout="wide", page_icon="💰")

# 2. الربط بقاعدة البيانات
conn = sqlite3.connect('finance_pro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS expenses (amount REAL, category TEXT, date TEXT)')
conn.commit()

# 3. الهيدر وشكل الموقع
st.title("💰 AI Finance Master")
st.markdown("### مساعدك الشخصي الذكي لإدارة ميزانيتك")

# 4. السايد بار (إدخال البيانات مع المسكن والتاريخ)
st.sidebar.header("📝 إضافة عملية جديدة")
income = st.sidebar.number_input("الدخل الشهري الحالي", min_value=1.0, value=15000.0, help="ادخل راتبك الأساسي")
amount = st.sidebar.number_input("المبلغ (Amount)", min_value=0.0, value=0.0, step=10.0)
category = st.sidebar.selectbox("الفئة (Category)", ["طعام 🍔", "تسوق 🛍️", "فواتير 📑", "ترفيه 🎮", "أخرى ✨"])

# خانة التاريخ اللي كانت ناقصة
expense_date = st.sidebar.date_input("تاريخ العملية", datetime.now())

if st.sidebar.button("حفظ العملية"):
    if amount > 0:
        c.execute('INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)', 
                  (amount, category, expense_date.strftime("%Y-%m-%d")))
        conn.commit()
        st.sidebar.success("تم حفظ العملية بنجاح! 🎉")
        st.balloons() # البالونات اللذيذة
        st.rerun()

# 5. معالجة البيانات
df = pd.read_sql_query("SELECT * FROM expenses", conn)
total_spent = df['amount'].sum()
remaining = income - total_spent

# حساب قيمة شريط التقدم بأمان
if income > 0:
    progress_val = max(0.0, min(remaining / income, 1.0))
else:
    progress_val = 0

# 6. عرض الملخص المالي
col1, col2, col3 = st.columns(3)
col1.metric("إجمالي الدخل", f"{income:,.0f} ج.م")
col2.metric("إجمالي المصاريف", f"{total_spent:,.0f} ج.م", delta=f"-{total_spent:,.0f}", delta_color="inverse")
col3.metric("الميزانية المتبقية", f"{remaining:,.0f} ج.م")

st.write("---")

# 7. حالة الإدخار والـ Progress Bar
st.subheader("📊 حالة الميزانية")
st.progress(progress_val)

# 8. منطقة ذكاء الـ AI والرسائل العشوائية (الرسايل اللذيذة هنا)
st.subheader("🔮 نصيحة المساعد الذكي (AI Analysis)")

if remaining <= 0:
    messages = [
        "يا بطل، الميزانية بتصوت في الزاوية! 📢 إحنا كدة عدينا الخط الأحمر.. محتاجين نشد الحزام شوية عشان الشهر يكمل بسلام. 😉",
        "إيه ده! 😱 المصاريف كسبت الدخل 1-0! محتاجين تدخّل سريع قبل ما المحفظة تعلن إفلاسها الرسمي. 💸",
        "شكلك نسيت إننا لسه في نص الشهر؟ 🤔 الميزانية بتقولك 'ارحمني'.. بلاش شوبينج النهاردة وخلينا صحاب. ✨"
    ]
    random_msg = random.choice(messages)
    
    st.error("⚠️ حالة طوارئ مالية!")
    st.warning(random_msg)
    
    # إشعار الويندوز
    try:
        notification.notify(
            title="تنبيه مالي من AI 🤖",
            message=random_msg,
            timeout=7
        )
    except:
        pass

elif remaining < (income * 0.2):
    st.warning("⚠️ تنبيه: ميزانيتك تقترب من النفاد (باقي أقل من 20%).")
else:
    st.success("✅ وضعك المالي مستقر حالياً. برافو عليك، استمر في التوفير!")

# 9. عرض سجل العمليات
st.write("---")
st.subheader("📜 سجل المصاريف الأخيرة")
if not df.empty:
    st.dataframe(df.sort_index(ascending=False), use_container_width=True)
else:
    st.info("لا توجد مصاريف مسجلة حتى الآن.")

# 10. زر مسح البيانات
if st.sidebar.button("🗑️ مسح كل السجل"):
    c.execute("DELETE FROM expenses")
    conn.commit()
    st.sidebar.warning("تم حذف جميع البيانات!")
    st.rerun()

st.sidebar.write("---")
st.sidebar.caption("تم التطوير بواسطة رضوى بالتعاون مع AI 🚀")
