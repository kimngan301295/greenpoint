# app.py - GreenPoint (Streamlit) - full working demo
import streamlit as st
import uuid
import base64
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="GreenPoint — Thi đua xanh", layout="wide")

# -------------------------
# Seed data (initial demo)
# -------------------------
def seed_data():
    schools = [
        {"id": "s1", "name": "THCS Nguyễn Văn A", "district": "Quận 1", "province": "TP.HCM"},
        {"id": "s2", "name": "THPT Trần Hưng Đạo", "district": "Quận 2", "province": "TP.HCM"},
        {"id": "s3", "name": "THCS Lê Lợi", "district": "Hà Đông", "province": "Hà Nội"},
    ]
    classes = [
        {"id": "c9A_s1", "name": "9A", "schoolId": "s1"},
        {"id": "c9B_s1", "name": "9B", "schoolId": "s1"},
        {"id": "c8C_s1", "name": "8C", "schoolId": "s1"},
        {"id": "c9A_s2", "name": "9A", "schoolId": "s2"},
        {"id": "c9A_s3", "name": "9A", "schoolId": "s3"},
    ]
    users = [
        {"id": "u1", "name": "Nguyễn An", "phone": "0900000001", "password": "1234", "role": "Học sinh", "schoolId": "s1", "classId": "c9A_s1"},
        {"id": "u2", "name": "Trần Bình", "phone": "0900000002", "password": "1234", "role": "Học sinh", "schoolId": "s1", "classId": "c9A_s1"},
        {"id": "m1", "name": "Hoàng Minh (Lớp trưởng 9A)", "phone": "0900000003", "password": "1234", "role": "Ban cán sự lớp", "schoolId": "s1", "classId": "c9A_s1"},
        {"id": "t1", "name": "Cô Mai (GV)", "phone": "0900000004", "password": "1234", "role": "Giáo viên chủ nhiệm", "schoolId": "s1"},
        {"id": "a1", "name": "Ban quản lý THCS s1", "phone": "0900000005", "password": "1234", "role": "Ban quản lý nhà trường", "schoolId": "s1"},
    ]
    now_ms = int(time.time() * 1000)
    actions = [
        {"id": "act1", "userId": "u1", "classId": "c9A_s1", "schoolId": "s1", "type": "Nhặt rác", "description": "Nhặt vỏ chai trong sân", "image": None, "points": 3, "status": "approved", "createdAt": now_ms - 3 * 24 * 3600 * 1000},
        {"id": "act2", "userId": "u2", "classId": "c9A_s1", "schoolId": "s1", "type": "Tắt điện", "description": "Tắt quạt sau tiết", "image": None, "points": 2, "status": "pending", "createdAt": now_ms - 1 * 3600 * 1000},
    ]
    return {"schools": schools, "classes": classes, "users": users, "actions": actions}

# initialize session data
if "data" not in st.session_state:
    st.session_state["data"] = seed_data()
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "auth"  # auth or dashboard or ranking

# -------------------------
# Helper functions
# -------------------------
def find_user_by_phone(phone):
    for u in st.session_state["data"]["users"]:
        if u.get("phone") == phone:
            return u
    return None

def find_user_by_id(uid):
    for u in st.session_state["data"]["users"]:
      if u.get("id") == uid:
            return u
    return None

def create_user(name, phone, password, role, province, district, schoolId=None, classId=None):
    # prevent duplicate phone
    if find_user_by_phone(phone):
        return None, "Số điện thoại đã được đăng ký"
    uid = "u" + uuid.uuid4().hex[:7]
    user = {"id": uid, "name": name, "phone": phone, "password": password, "role": role, "province": province, "district": district, "schoolId": schoolId, "classId": classId}
    st.session_state["data"]["users"].append(user)
    return user, None

def add_action(userId, classId, schoolId, typ, desc, image_bytes, points):
    aid = "a" + uuid.uuid4().hex[:7]
    img_b64 = None
    if image_bytes is not None:
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    rec = {"id": aid, "userId": userId, "classId": classId, "schoolId": schoolId, "type": typ, "description": desc, "image": img_b64, "points": points, "status": "pending", "createdAt": int(time.time() * 1000)}
    st.session_state["data"]["actions"].append(rec)
    return rec

def update_action(action_id, patch):
    for i, a in enumerate(st.session_state["data"]["actions"]):
        if a["id"] == action_id:
            st.session_state["data"]["actions"][i] = {**a, **patch}
            return st.session_state["data"]["actions"][i]
    return None

def compute_points_for_user(userId, days=7):
    cutoff = int((time.time() - days * 24 * 3600) * 1000)
    s = 0
    for a in st.session_state["data"]["actions"]:
        if a.get("userId") == userId and a.get("status") == "approved" and a.get("createdAt", 0) >= cutoff:
            s += int(a.get("points", 0))
    return s

def compute_points_for_class(classId, days=30):
    cutoff = int((time.time() - days * 24 * 3600) * 1000)
    s = 0
    for a in st.session_state["data"]["actions"]:
        if a.get("classId") == classId and a.get("status") == "approved" and a.get("createdAt", 0) >= cutoff:
            s += int(a.get("points", 0))
    return s

# -------------------------
# UI: Auth (Login / Register)
# -------------------------
def auth_page():
    st.title("🌱 GreenPoint — Đăng nhập / Đăng ký")
    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])

    with tab1:
        st.subheader("Đăng nhập")
        phone = st.text_input("Số điện thoại (đăng nhập)", key="li_phone")
        password = st.text_input("Mật khẩu", type="password", key="li_pwd")
        if st.button("Đăng nhập"):
            user = find_user_by_phone(phone)
            if user and user.get("password") == password:
                st.session_state["current_user"] = user
                st.session_state["page"] = "dashboard"
                st.success(f"Đăng nhập thành công — {user.get('name')}")
                st.experimental_rerun()
            else:
                st.error("Sai số điện thoại hoặc mật khẩu")

   with tab2:
   st.subheader("Đăng ký tài khoản mới")
        with st.form("reg_form"):
            name = st.text_input("Họ và tên")
            phone_r = st.text_input("Số điện thoại")
            pwd_r = st.text_input("Mật khẩu", type="password")
            role = st.selectbox("Chức vụ", ["Học sinh", "Ban cán sự lớp", "Giáo viên chủ nhiệm", "Ban quản lý nhà trường"])
            province = st.text_input("Tỉnh/Thành phố")
            district = st.text_input("Quận/Huyện")
            # choose school from seed list (optional)
            schools = st.session_state["data"]["schools"]
            school_choice = st.selectbox("Trường (tùy chọn)", [""] + [f'{s["province"]} • {s["name"]}' for s in schools])
            schoolId = None
            classId = None
            if school_choice:
                # find schoolId
                schoolId = next((s["id"] for s in schools if f'{s["province"]} • {s["name"]}' == school_choice), None)
                # show class selection
                classes = [c for c in st.session_state["data"]["classes"] if c["schoolId"] == schoolId]
                class_names = [c["name"] for c in classes]
                class_sel = st.selectbox("Lớp (tùy chọn)", [""] + class_names)
                if class_sel:
                    classId = next((c["id"] for c in classes if c["name"] == class_sel), None)

            submitted = st.form_submit_button("Tạo tài khoản & Đăng nhập")
            if submitted:
                if not (name and phone_r and pwd_r):
                    st.error("Vui lòng điền tên, số điện thoại và mật khẩu")
                else:
                    user, err = create_user(name, phone_r, pwd_r, role, province, district, schoolId, classId)
                    if err:
                        st.error(err)
                    else:
                        st.success("Đăng ký thành công! Tự động đăng nhập...")
                        st.session_state["current_user"] = user
                        st.session_state["page"] = "dashboard"
                        st.experimental_rerun()

# -------------------------
# UI: Dashboard (role-based)
# -------------------------
def dashboard_page():
    user = st.session_state["current_user"]
    if not user:
        st.session_state["page"] = "auth"
        st.experimental_rerun()
        return

    # Sidebar info + logout + navigation
    st.sidebar.markdown(f"**{user.get('name')}**  \n_{user.get('role')}_")
    if user.get("schoolId"):
        school = next((s for s in st.session_state["data"]["schools"] if s["id"] == user.get("schoolId")), None)
        if school:
            st.sidebar.markdown(f"🏫 {school.get('name')}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state["current_user"] = None
        st.session_state["page"] = "auth"
        st.experimental_rerun()
page = st.sidebar.radio("Trang", ["Bảng chính", "Bảng xếp hạng"])

    if page == "Bảng xếp hạng":
        ranking_page()
        return

    st.title(f"Xin chào, {user.get('name')} — {user.get('role')}")

    # Role: Học sinh
    if user.get("role") == "Học sinh":
        st.subheader("🌱 Điểm cá nhân")
        weekly = compute_points_for_user(user.get("id"), days=7)
        st.metric("Điểm tuần (mục tiêu ≥10)", weekly)
        st.progress(min(1.0, weekly / 10) if weekly >= 0 else 0)

        st.subheader("🏫 Điểm lớp (30 ngày)")
        if user.get("classId"):
            class_pts = compute_points_for_class(user.get("classId"), days=30)
            st.write(f"Lớp {user.get('classId')} — {class_pts} / 100")
            st.progress(min(1.0, class_pts / 100))
        else:
            st.write("Bạn chưa chọn lớp trong hồ sơ.")

        st.subheader("➕ Gửi hành vi mới (sẽ chờ Ban cán sự duyệt)")
        typ = st.selectbox("Loại hành vi", ["Nhặt rác", "Tiết kiệm điện", "Tái chế giấy", "Đi xe đạp", "Khác"])
        desc = st.text_input("Mô tả (ngắn)")
        img = st.file_uploader("Ảnh (tùy chọn)", type=["png", "jpg", "jpeg"])
        pts_map = {"Nhặt rác": 3, "Tiết kiệm điện": 2, "Tái chế giấy": 2, "Đi xe đạp": 2, "Khác": 1}
        if st.button("Gửi để duyệt"):
            if not desc.strip():
                st.warning("Nhập mô tả ngắn nhé")
            else:
               st.session_state["page"] = "auth"
        auth_page()

if __name__ == "__main__":
    main()

