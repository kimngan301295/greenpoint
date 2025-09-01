import streamlit as st

# --------------------------
# Fake Database (tạm thời)
# --------------------------
if "users" not in st.session_state:
    st.session_state["users"] = []  # Danh sách người dùng đã đăng ký
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "login"

# --------------------------
# Hàm xử lý đăng ký
# --------------------------
def register():
    st.title("📌 Đăng ký tài khoản")
    name = st.text_input("Họ và tên")
    phone = st.text_input("Số điện thoại")
    password = st.text_input("Mật khẩu", type="password")
    role = st.selectbox("Chức vụ", ["Học sinh", "Ban cán sự lớp", "Giáo viên chủ nhiệm", "Ban quản lý nhà trường"])
    region = st.text_input("Khu vực (Tỉnh/TP, Quận/Huyện, Xã/Phường)")
    school = st.text_input("Tên trường")

    if st.button("Đăng ký"):
        user = {"name": name, "phone": phone, "password": password,
                "role": role, "region": region, "school": school}
        st.session_state["users"].append(user)
        st.success("Đăng ký thành công! Hãy đăng nhập.")
        st.session_state["page"] = "login"

    if st.button("Đã có tài khoản? Đăng nhập"):
        st.session_state["page"] = "login"

# --------------------------
# Hàm xử lý đăng nhập
# --------------------------
def login():
    st.title("🔑 Đăng nhập")
    phone = st.text_input("Số điện thoại")
    password = st.text_input("Mật khẩu", type="password")

    if st.button("Đăng nhập"):
        for user in st.session_state["users"]:
            if user["phone"] == phone and user["password"] == password:
                st.session_state["current_user"] = user
                st.success("Đăng nhập thành công!")
                st.session_state["page"] = "dashboard"
                return
        st.error("Sai số điện thoại hoặc mật khẩu!")

    if st.button("Chưa có tài khoản? Đăng ký"):
        st.session_state["page"] = "register"

# --------------------------
# Dashboard theo chức vụ
# --------------------------
def show_dashboard(user):
    role = user["role"]
    st.sidebar.write(f"👤 {user['name']} ({role})")
    st.sidebar.write(f"🏫 {user['school']} - {user['region']}")
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

 if role == "Giáo viên quản lý":
    st.title("📚 Giao diện Giáo viên quản lý")
    st.write("Đây là nơi quản lý lớp học, học sinh và giáo viên.")

elif role == "Học sinh":
    st.title("👩‍👩‍👧‍👦 Giao diện Học sinh")
    st.write("Đây là nơi học sinh xem điểm, hành vi xanh, và nhiệm vụ.")

elif role == "Giáo viên":
    st.title("👨‍🏫 Giao diện Giáo viên")
    st.write("Đây là nơi giáo viên chấm điểm hành vi xanh cho học sinh.")

elif role == "Ban cán sự":
    st.title("📝 Giao diện Ban cán sự")
    st.write("Đây là nơi ban cán sự theo dõi và tổng hợp điểm hành vi xanh.")
    st.title("📊 Giao diện Giáo viên Quản lý")
    st.write("Xem điểm thi đua của tất cả các lớp.")
elif role == "Ban cán sự lớp":
    st.title("📝 Giao diện Ban cán sự lớp")
    st.write("Quản lý điểm thi đua của lớp mình.")
elif role == "Học sinh":
    st.title("👩‍👩‍👧‍👦 Giao diện Học sinh")
    st.write("Xem và đóng góp điểm hành vi xanh cho bản thân.")
else:
    st.warning("Vui lòng chọn chức vụ để tiếp tục!")
        st.title("👩‍👩‍👧‍👦 Giao diện Học sinh")
        st.write("Xem điểm cá nhân và điểm lớp.")

# --------------------------
# Điều hướng chính
# --------------------------
if st.session_state["page"] == "register":
    register()
elif st.session_state["page"] == "login":
    login()
elif st.session_state["page"] == "dashboard":
    show_dashboard(st.session_state["current_user"])

