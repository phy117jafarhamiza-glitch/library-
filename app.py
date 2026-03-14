import streamlit as st
import pandas as pd
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="مكتبة التربية البدنية وعلوم الرياضة", page_icon="🏋️‍♂️", layout="wide")

# 2. إعداد ملفات قاعدة البيانات (CSV)
DB_FILE = "books_data.csv"
CATEGORIES_FILE = "categories_data.csv"
CRED_FILE = "admin_credentials.csv"

# إنشاء ملف الكتب إذا لم يكن موجوداً
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["اسم الكتاب", "المؤلف", "التصنيف", "رابط الكتاب (Google Drive)"])
    df_init.to_csv(DB_FILE, index=False)

# إنشاء ملف الأقسام إذا لم يكن موجوداً
if not os.path.exists(CATEGORIES_FILE):
    cat_init = pd.DataFrame({"التصنيف": ["العلوم الحركية", "العلوم النفسية", "العلوم الصحية", "العلوم البحثية"]})
    cat_init.to_csv(CATEGORIES_FILE, index=False)

# إنشاء ملف بيانات الدخول إذا لم يكن موجوداً (الحساب الافتراضي)
if not os.path.exists(CRED_FILE):
    cred_init = pd.DataFrame({"username": ["admin"], "password": ["12345"]})
    cred_init.to_csv(CRED_FILE, index=False)

# قراءة الأقسام الحالية من الملف وتحويلها لقائمة
categories_df = pd.read_csv(CATEGORIES_FILE)
categories_list = categories_df["التصنيف"].dropna().tolist()

# 3. القائمة الجانبية
st.sidebar.title("القائمة الرئيسية")
page = st.sidebar.radio("الانتقال إلى:", ["الواجهة العامة", "لوحة الإدارة (للمشرفين)"])

# ---------------------------------------------------------
# الصفحة الأولى: الواجهة العامة (للزوار)
# ---------------------------------------------------------
if page == "الواجهة العامة":
    st.title("🏋️‍♂️ مكتبة التربية البدنية وعلوم الرياضة")
    st.write("أهلاً بك في المكتبة! يمكنك البحث عن الكتب أو تصفحها حسب القسم.")
    
    # قراءة بيانات الكتب
    df = pd.read_csv(DB_FILE)
    
    # ترتيب مربع البحث وقائمة الأقسام بجانب بعضهما
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_query = st.text_input("🔍 ابحث عن اسم الكتاب أو المؤلف:")
    with col2:
        selected_category = st.selectbox("اختر القسم لعرض كتبه:", ["الكل"] + categories_list)
        
    st.markdown("---")
    
    # 1. تطبيق فلتر القسم أولاً
    if selected_category != "الكل":
        df_filtered = df[df["التصنيف"] == selected_category]
    else:
        df_filtered = df
        
    # 2. تطبيق فلتر البحث ثانياً (إن وجد)
    if search_query:
        # البحث في عمودي "اسم الكتاب" و "المؤلف" (استخدمنا fillna لتجنب الأخطاء إذا كانت الخلية فارغة)
        search_mask = (
            df_filtered["اسم الكتاب"].fillna("").str.contains(search_query, case=False, regex=False) |
            df_filtered["المؤلف"].fillna("").str.contains(search_query, case=False, regex=False)
        )
        df_filtered = df_filtered[search_mask]
        
    if df_filtered.empty:
        if search_query:
            st.warning(f"لم يتم العثور على نتائج مطابقة لبحثك: '{search_query}'")
        else:
            st.info("لا توجد كتب في هذا التصنيف حالياً.")
    else:
        # عرض الجدول للزوار
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
    
    # قراءة بيانات الدخول الحالية من الملف
    creds_df = pd.read_csv(CRED_FILE)
    real_username = str(creds_df["username"].iloc[0])
    real_password = str(creds_df["password"].iloc[0])
    
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False
        
    if not st.session_state["admin_logged_in"]:
        st.subheader("تسجيل الدخول للإدارة")
        username = st.text_input("اسم المستخدم")
        password = st.text_input("كلمة المرور", type="password")
        
        if st.button("دخول"):
            if username == real_username and password == real_password: 
                st.session_state["admin_logged_in"] = True
                st.rerun()
            else:
                st.error("اسم المستخدم أو كلمة المرور غير صحيحة!")
                
    else:
        st.success("مرحباً بك! يمكنك الآن إدارة المكتبة بالكامل.")
        if st.button("تسجيل الخروج"):
            st.session_state["admin_logged_in"] = False
            st.rerun()
            
        st.markdown("---")

        # --- قسم تغيير كلمة المرور ---
        with st.expander("🔑 تغيير كلمة المرور واسم المستخدم"):
            with st.form("change_password_form", clear_on_submit=True):
                new_username = st.text_input("اسم المستخدم الجديد", value=real_username)
                old_password = st.text_input("كلمة المرور الحالية *", type="password")
                new_password = st.text_input("كلمة المرور الجديدة *", type="password")
                confirm_password = st.text_input("تأكيد كلمة المرور الجديدة *", type="password")
                
                if st.form_submit_button("حفظ بيانات الدخول الجديدة"):
                    if old_password != real_password:
                        st.error("كلمة المرور الحالية غير صحيحة!")
                    elif new_password != confirm_password:
                        st.error("كلمات المرور الجديدة غير متطابقة!")
                    elif len(new_password) < 4:
                        st.warning("يجب أن تتكون كلمة المرور الجديدة من 4 رموز على الأقل.")
                    else:
                        creds_df.at[0, "username"] = new_username
                        creds_df.at[0, "password"] = new_password
                        creds_df.to_csv(CRED_FILE, index=False)
                        st.success("تم تغيير بيانات الدخول بنجاح! سيتم تطبيقها في المرة القادمة.")

        st.markdown("---")
        
        # --- قسم إدارة الأقسام ---
        st.subheader("📂 إدارة أقسام المكتبة (إضافة / تعديل / حذف)")
        st.info("💡 لإضافة قسم جديد: انزل لآخر صف واكتب اسم القسم. للحذف: حدد المربع واضغط سلة المهملات.")
        
        edited_categories = st.data_editor(
            categories_df,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="category_editor"
        )
        
        if st.button("💾 حفظ التعديلات على الأقسام"):
            edited_categories = edited_categories.dropna()
            edited_categories.to_csv(CATEGORIES_FILE, index=False)
            st.success("تم تحديث أقسام المكتبة بنجاح!")
            st.rerun()

        st.markdown("---")

        # --- قسم إضافة كتاب جديد ---
        st.subheader("📥 إضافة كتاب جديد")
        
        with st.form("add_book_form", clear_on_submit=True):
            book_title = st.text_input("اسم الكتاب *")
            book_author = st.text_input("اسم المؤلف *")
            
            if not categories_list:
                st.warning("يرجى إضافة قسم واحد على الأقل من قسم إدارة الأقسام أعلاه.")
                book_category = None
            else:
                book_category = st.selectbox("تصنيف الكتاب *", categories_list)
                
            book_link = st.text_input("رابط الكتاب من Google Drive *", placeholder="https://drive.google.com/...")
            
            submit_button = st.form_submit_button("إضافة الكتاب")
            
            if submit_button:
                if book_title and book_author and book_link and book_category:
                    new_book = pd.DataFrame({
                        "اسم الكتاب": [book_title],
                        "المؤلف": [book_author],
                        "التصنيف": [book_category],
                        "رابط الكتاب (Google Drive)": [book_link]
                    })
                    new_book.to_csv(DB_FILE, mode='a', header=False, index=False)
                    st.success(f"تمت إضافة كتاب '{book_title}' بنجاح!")
                    st.rerun()
                else:
                    st.warning("يرجى تعبئة جميع الحقول المطلوبة.")
                    
        st.markdown("---")
        
        # --- قسم تعديل وحذف الكتب المضافة ---
        st.subheader("✏️ إدارة وتعديل الكتب (تعديل / حذف)")
        st.info("💡 للتعديل: انقر مرتين على أي خلية في الجدول. للحذف: حدد المربع بجانب اسم الكتاب واضغط على أيقونة سلة المهملات أعلى الجدول.")
        
        df_to_edit = pd.read_csv(DB_FILE)
        
        edited_books_df = st.data_editor(
            df_to_edit,
            num_rows="dynamic",
            use_container_width=True,
            hide_index=True,
            key="books_editor"
        )
        
        if st.button("💾 حفظ التعديلات على الكتب"):
            edited_books_df.to_csv(DB_FILE, index=False)
            st.success("تم حفظ جميع التعديلات بنجاح! سيراها الزوار الآن.")
            st.rerun()
