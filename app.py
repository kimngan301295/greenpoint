import streamlit as st

# Khởi tạo session state để lưu người dùng
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "role" not in st.session_state:
    st.session_state.role = None

# -------------------------
# Trang đăng ký / đăng nhập
# -------------------------
def login_page():
    st.title("🔑 Đăng nhập / Đăng ký")

    with st.form("login_form"):
        fullname = st.text_input("Họ và tên")
        phone = st.text_input("Số điện thoại")
        password = st.text_input("Mật khẩu", type="password")
        role = st.selectbox("Chức vụ", ["Học sinh", "Giáo viên thường", "Giáo viên quản lý"])
        area = st.text_input("Khu vực")
        school = st.text_input("Tên trường")

        submitted = st.form_submit_button("Tiếp theo")

        if submitted:
            if fullname and phone and password:
                st.session_state.logged_in = True
                st.session_state.role = role
                st.success("Đăng nhập thành công ✅")
            else:
                st.error("Vui lòng điền đầy đủ thông tin!")

# -------------------------
# Giao diện theo chức vụ
# -------------------------
def main_app():
    role = st.session_state.role

    if role == "Giáo viên quản lý":
        st.title("📊 Giao diện Giáo viên quản lý")
        st.write("Xin chào thầy/cô! Đây là nơi quản lý toàn bộ hệ thống.")
    
    elif role == "Giáo viên thường":
        st.title("📘 Giao diện Giáo viên")
        st.write("Xin chào thầy/cô! Đây là nơi theo dõi và hỗ trợ học sinh.")

    elif role == "Học sinh":
        st.title("👩‍👩‍👧‍👦 Giao diện Học sinh")
        st.write("Chào bạn học sinh! Đây là nơi tham gia các hoạt động.")

# -------------------------
# Chạy app
# -------------------------
def main():
    if not st.session
