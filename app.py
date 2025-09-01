import streamlit as st

# ------------------------
# CẤU HÌNH APP
# ------------------------
st.set_page_config(page_title="Thi đua xanh", layout="wide")

# ------------------------
# DATABASE GIẢ LẬP
# ------------------------
if "users" not in st.session_state:
    st.session_state.users = []  # lưu danh sách tài khoản
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ------------------------
# HÀM ĐĂNG KÝ
# ------------------------
def register():
    st.title("📌 Đăng ký tài khoản")
    with st.form("register_form"):
        name = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        password = st.text_input("Mật khẩu", type="password")
        role = st.selectbox("Chức vụ", ["Học sinh", "Ban cán sự lớp", "Giáo viên chủ nhiệm", "Ban quản lý nhà trường"])
        province = st.text_input("Tỉnh/Thành phố")
        school = st.text_input("Tên trường")
        submit = st.form_submit_button("Đăng ký")

    if submit:
        st.session_state.users.append({
            "name": name,
            "phone": phone,
            "password": password,
            "role": role,
            "province": province,
            "school": school
        })
        st.success("✅ Đăng ký thành công! Hãy đăng nhập.")
        st.session_state.page = "login"

# ------------------------
# HÀM ĐĂNG NHẬP
# ------------------------
def login():
    st.title("🔑 Đăng nhập")
    with st.form("login_form"):
        phone = st.text_input("Số điện thoại")
        password = st.text_input("Mật khẩu", type="password")
        submit = st.form_submit_button("Đăng nhập")

    if submit:
        for user in st.session_state.users:
            if user["phone"] == phone and user["password"] == password:
                st.session_state.current_user = user
                st.success(f"Xin chào {user['name']} ({user['role']}) 👋")
                return
        st.error("❌ Sai thông tin đăng nhập!")

# ------------------------
# TRANG GIAO DIỆN THEO CHỨC VỤ
# ------------------------
def show_dashboard(user):
    role = user["role"]
    st.sidebar.write(f"👤 {user['name']} ({role})")
    st.sidebar.button("Đăng xuất", on_click=lambda: st.session_state.update({"current_user": None, "page": "login"}))

    if role == "Ban quản lý nhà trường":
        st.title("🏫 Trang quản lý thi đua toàn trường")
        st.write("Quản lý tất cả trường, quận, tỉnh.")

    elif role == "Giáo viên chủ nhiệm":
        st.title("👨‍🏫 Trang quản lý của GVCN")
        st.write("Xem và xác nhận điểm thi đua của lớp mình.")

    elif role == "Ban cán sự lớp":
        st.title("🧑‍🎓 Trang Ban cán sự lớp")
        st.write("Cộng/trừ điểm hành vi xanh cho học sinh.")

    elif role == "Học sinh":
st.title("👩‍👩‍👧‍👦 Giao diện Học sinh")
        st.write("Xem điểm cá nhân và điểm lớp.")

# ------------------------
# LOGIC ĐIỀU HƯỚNG
# ------------------------
if "page" not in st.session_state:
    st.session_state.page = "login"

if st.session_state.current_user:
    show_dashboard(st.session_state.current_user)
else:
    if st.session_state.page == "login":
        login()
        st.write("Chưa có tài khoản?")
        if st.button("👉 Đăng ký ngay"):
            st.session_state.page = "register"
    elif st.session_state.page == "register":
        register()

