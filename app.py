import streamlit as st
import pandas as pd
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="مكتبة التربية البدنية وعلوم الرياضة", page_icon="🏋️‍♂️", layout="wide")

# 2. إعداد ملف قاعدة البيانات (CSV)
DB_FILE = "books_data.csv"

# إنشاء الملف إذا لم يكن موجوداً
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["اسم الكتاب", "المؤلف", "التصنيف", "رابط الكتاب (Google Drive)"])
    df_init.to_csv(DB_FILE, index=False)

CATEGORIES = ["العلوم الحركية", "العلوم النفسية", "العلوم الصحية", "العلوم البحثية"]

# 3. القائمة الجانبية
st.sidebar.title("القائمة الرئيسية")
page = st.sidebar.radio("الانتقال إلى:", ["الواجهة العامة", "لوحة الإدارة (للمشرفين)"])

# ---------------------------------------------------------
# الصفحة الأولى: الواجهة العامة (للزوار)
# ---------------------------------------------------------
if page == "الواجهة العامة":
    st.title("🏋️‍♂️ مكتبة التربية البدنية وعلوم الرياضة")
    st.write("أهلاً بك في المكتبة! يمكنك تصفح الكتب والضغط على الرابط لقراءتها أو تحميلها.")
    
    # قراءة البيانات
    df = pd.read_csv(DB_FILE)
    
    # فلتر التصنيفات
    selected_category = st.selectbox("اختر نوع الكتاب لعرضه:", ["الكل"] + CATEGORIES)
    st.markdown("---")
    
    if selected_category != "الكل":
        df_filtered = df[df["التصنيف"] == selected_category]
    else:
        df_filtered = df
        
    if df_filtered.empty:
        st.info("لا توجد كتب في هذا التصنيف حالياً.")
    else:
        # عرض الجدول مع جعل الروابط قابلة للضغط
        st.dataframe(
            df_filtered,
            column_config={
                "رابط الكتاب (Google Drive)": st.column_config.LinkColumn(
                    "رابط القراءة/التحميل",
                    display_text="🔗 اضغط هنا لفتح الكتاب"
                )
            },
            hide_index=True,
            use_container_width=True
        )

# ---------------------------------------------------------
# الصفحة الثانية: لوحة الإدارة
# ---------------------------------------------------------
elif page == "لوحة الإدارة (للمشرفين)":
    st.title("🔒 لوحة تحكم الإدارة")
    
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False
        
    if not st.session_state["admin_logged_in"]:
        st.subheader("تسجيل الدخول للإدارة")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول"):
            if username == "admin" and password == "12345": 
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
                
    else:
        st.success("مرحباً بك! يمكنك الآن إضافة بيانات الكتاب ورابطه.")
        if st.button("تسجيل الخروج"):
            st.session_state["admin_logged_in"] = False
            st.rerun()
            
        st.markdown("---")
        st.subheader("📥 إضافة كتاب جديد")
        
        with st.form("add_book_form"):
            book_title = st.text_input("اسم الكتاب *")
            book_author = st.text_input("اسم المؤلف *")
            book_category = st.selectbox("تصنيف الكتاب *", CATEGORIES)
            book_link = st.text_input("رابط الكتاب من Google Drive *", placeholder="https://drive.google.com/...")
            
            submit_button = st.form_submit_button("حفظ بيانات الكتاب")
            
            if submit_button:
                if book_title and book_author and book_link:
                    # حفظ البيانات الجديدة في ملف CSV
                    new_book = pd.DataFrame({
                        "اسم الكتاب": [book_title],
                        "المؤلف": [book_author],
                        "التصنيف": [book_category],
                        "رابط الكتاب (Google Drive)": [book_link]
                    })
                    new_book.to_csv(DB_FILE, mode='a', header=False, index=False)
                    st.success(f"تمت إضافة كتاب '{book_title}' بنجاح!")
                else:
                    st.warning("يرجى تعبئة جميع الحقول المطلوبة.")
