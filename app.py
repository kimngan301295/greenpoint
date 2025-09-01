# app.py — GreenPoint full working demo
# Copy/paste nguyên file này, chỉ dùng 4 spaces indent, không tab
import streamlit as st
import uuid
import json
import base64
import time
from datetime import datetime
from io import BytesIO
import csv

st.set_page_config(page_title="GreenPoint — Thi đua xanh", layout="wide")

DATA_FILE = "data.json"

# ------------------------
# Persistence helpers
# ------------------------
def now_ms():
    return int(time.time() * 1000)

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return seed_data()

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        # fallback to session_state only
        pass

# ------------------------
# Seed demo data
# ------------------------
def seed_data():
    now = now_ms()
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
    ]
    users = [
        {"id": "u1", "name": "Nguyễn An", "phone": "0900000001", "password": "1234", "role": "Học sinh", "schoolId": "s1", "classId": "c9A_s1", "badges": []},
        {"id": "u2", "name": "Trần Bình", "phone": "0900000002", "password": "1234", "role": "Học sinh", "schoolId": "s1", "classId": "c9A_s1", "badges": []},
        {"id": "m1", "name": "Hoàng Minh (Lớp trưởng 9A)", "phone": "0900000003", "password": "1234", "role": "Ban cán sự lớp", "schoolId": "s1", "classId": "c9A_s1", "badges": []},
        {"id": "t1", "name": "Cô Mai (GV)", "phone": "0900000004", "password": "1234", "role": "Giáo viên chủ nhiệm", "schoolId": "s1", "badges": []},
        {"id": "a1", "name": "Ban quản lý THCS s1", "phone": "0900000005", "password": "1234", "role": "Ban quản lý nhà trường", "schoolId": "s1", "badges": []},
    ]
    actions = [
        {"id": "act1", "userId": "u1", "classId": "c9A_s1", "schoolId": "s1", "type": "Nhặt rác", "description": "Nhặt vỏ chai", "image": None, "points": 3, "status": "approved", "createdAt": now - 3 * 24 * 3600 * 1000},
        {"id": "act2", "userId": "u2", "classId": "c9A_s1", "schoolId": "s1", "type": "Tắt điện", "description": "Tắt đèn sau tiết", "image": None, "points": 2, "status": "pending", "createdAt": now - 4 * 3600 * 1000},
    ]
    return {"schools": schools, "classes": classes, "users": users, "actions": actions}

# ------------------------
# Init session / data
# ------------------------
if "app_data" not in st.session_state:
    st.session_state["app_data"] = load_data()
else:
    if not isinstance(st.session_state["app_data"], dict):
        st.session_state["app_data"] = seed_data()

if "current_user_id" not in st.session_state:
    st.session_state["current_user_id"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "auth"

# ------------------------
# Utility functions
# ------------------------
def find_user_by_phone(phone):
    for u in st.session_state["app_data"]["users"]:
        if u.get("phone") == phone:
            return u
    return None

def find_user_by_id(uid):
    for u in st.session_state["app_data"]["users"]:
        if u.get("id") == uid:
            return u
    return None

def find_class_by_id(cid):
    for c in st.session_state["app_data"]["classes"]:
        if c.get("id") == cid:
            return c
    return None

def find_school_by_id(sid):
    for s in st.session_state["app_data"]["schools"]:
        if s.get("id") == sid:
            return s
    return None

def create_user(name, phone, password, role, province, district, schoolId=None, classId=None):
    if find_user_by_phone(phone):
        return None, "Số điện thoại đã tồn tại"
    uid = "u" + uuid.uuid4().hex[:8]
    user = {"id": uid, "name": name, "phone": phone, "password": password, "role": role, "province": province, "district": district, "schoolId": schoolId, "classId": classId, "badges": []}
    st.session_state["app_data"]["users"].append(user)
    try:
        save_data(st.session_state["app_data"])
    except:
        pass
    return user, None

def add_action(userId, classId, schoolId, typ, desc, image_bytes, points):
    aid = "a" + uuid.uuid4().hex[:8]
    img_b64 = None
    if image_bytes is not None:
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    rec = {"id": aid, "userId": userId, "classId": classId, "schoolId": schoolId, "type": typ, "description": desc, "image": img_b64, "points": points, "status": "pending", "createdAt": now_ms()}
    st.session_state["app_data"]["actions"].append(rec)
    try:
        save_data(st.session_state["app_data"])
    except:
        pass
    return rec

def update_action(action_id, patch):
    for i, a in enumerate(st.session_state["app_data"]["actions"]):
        if a.get("id") == action_id:
            st.session_state["app_data"]["actions"][i] = {**a, **patch}
            try:
                save_data(st.session_state["app_data"])
            except:
                pass
            return st.session_state["app_data"]["actions"][i]
    return None

def compute_points_for_user(userId, days=None):
    if days is None:
        cutoff = 0
    else:
        cutoff = int((time.time() - days * 24 * 3600) * 1000)
    total = 0
    for a in st.session_state["app_data"]["actions"]:
        if a.get("userId") == userId and a.get("status") == "approved" and a.get("createdAt", 0) >= cutoff:
            total += int(a.get("points", 0))
    return total

def compute_points_for_class(classId, days=30):
    cutoff = int((time.time() - days * 24 * 3600) * 1000)
    total = 0
    for a in st.session_state["app_data"]["actions"]:
        if a.get("classId") == classId and a.get("status") == "approved" and a.get("createdAt", 0) >= cutoff:
            total += int(a.get("points", 0))
    return total

# ------------------------
# Auth page
# ------------------------
def auth_page():
    st.title("🌱 GreenPoint — Đăng nhập / Đăng ký")
    tab_login, tab_register = st.tabs(["Đăng nhập", "Đăng ký"])

    with tab_login:
        st.subheader("Đăng nhập")
        li_phone = st.text_input("Số điện thoại", key="li_phone")
        li_pwd = st.text_input("Mật khẩu", type="password", key="li_pwd")
        if st.button("Đăng nhập"):
            user = find_user_by_phone(li_phone)
            if user and user.get("password") == li_pwd:
                st.session_state["current_user_id"] = user.get("id")
                st.session_state["page"] = "dashboard"
                st.success(f"Chào {user.get('name')} — bạn đã đăng nhập")
                st.experimental_rerun()
            else:
                st.error("Sai số điện thoại hoặc mật khẩu")

    with tab_register:
        st.subheader("Đăng ký tài khoản mới")
        with st.form("reg_form"):
            r_name = st.text_input("Họ và tên")
            r_phone = st.text_input("Số điện thoại")
            r_pwd = st.text_input("Mật khẩu", type="password")
            r_role = st.selectbox("Chức vụ", ["Học sinh", "Ban cán sự lớp", "Giáo viên chủ nhiệm", "Ban quản lý nhà trường"])
            r_province = st.text_input("Tỉnh/Thành phố")
            r_district = st.text_input("Quận/Huyện")
            r_xa = st.text_input("Xã/Phường")
            # choose school/class optionally
            schools = st.session_state["app_data"]["schools"]
            school_options = [""] + [f'{s.get("province")} • {s.get("name")}' for s in schools]
            r_school_choice = st.selectbox("Trường (tùy chọn)", school_options)
            r_schoolId = None
            r_classId = None
            if r_school_choice:
                r_schoolId = next((s.get("id") for s in schools if f'{s.get("province")} • {s.get("name")}' == r_school_choice), None)
                classes = [c for c in st.session_state["app_data"]["classes"] if c.get("schoolId") == r_schoolId]
                class_names = [""] + [c.get("name") for c in classes]
                r_class_name = st.selectbox("Lớp (tùy chọn)", class_names)
                if r_class_name:
                    r_classId = next((c.get("id") for c in classes if c.get("name") == r_class_name), None)
            submitted = st.form_submit_button("Tạo tài khoản & Đăng nhập")
            if submitted:
                if not (r_name and r_phone and r_pwd):
                    st.error("Nhập tên, số điện thoại và mật khẩu")
                else:
                    user, err = create_user(r_name, r_phone, r_pwd, r_role, r_province, r_district, r_schoolId, r_classId)
                    if err:
                        st.error(err)
                    else:
                        st.success("Đăng ký thành công — bạn đã được đăng nhập")
                        st.session_state["current_user_id"] = user.get("id")
                        st.session_state["page"] = "dashboard"
                        st.experimental_rerun()

# ------------------------
# Main routing
# ------------------------
def main():
    if st.session_state["page"] == "auth":
        auth_page()
    elif st.session_state["page"] == "dashboard":
        from dashboard import dashboard_page
        dashboard_page()
    else:
        st.session_state["page"] = "auth"
        auth_page()

if __name__ == "__main__":
    main()
