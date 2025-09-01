# app.py — GreenPoint Full Demo
import streamlit as st
import uuid
import json
import base64
import time
from datetime import datetime, timedelta
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
    except:
        # environment may be read-only
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
        {"id": "u1", "name": "Nguyễn An", "phone": "0900000001", "password": "1234", "role": "Học sinh",
         "province":"TP.HCM", "district":"Quận 1", "schoolId": "s1", "classId": "c9A_s1", "badges": []},
        {"id": "m1", "name": "Hoàng Minh (Lớp trưởng 9A)", "phone": "0900000003", "password": "1234",
         "role": "Ban cán sự lớp", "province":"TP.HCM", "district":"Quận 1", "schoolId": "s1", "classId": "c9A_s1", "badges": []},
        {"id": "t1", "name": "Cô Mai (GV)", "phone": "0900000004", "password": "1234",
         "role": "Giáo viên chủ nhiệm", "province":"TP.HCM", "district":"Quận 1", "schoolId": "s1", "badges": []},
        {"id": "a1", "name": "Ban quản lý THCS s1", "phone": "0900000005", "password": "1234",
         "role": "Ban quản lý nhà trường", "province":"TP.HCM", "district":"Quận 1", "schoolId": "s1", "badges": []},
    ]
    actions = []
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
    st.session_state["page"] = "auth"  # auth | dashboard

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
    user = {"id": uid, "name": name, "phone": phone, "password": password, "role": role,
            "province": province, "district": district, "schoolId": schoolId, "classId": classId, "badges": [],
            "actions": []}
    st.session_state["app_data"]["users"].append(user)
    save_data(st.session_state["app_data"])
    return user, None

def add_action(userId, classId, schoolId, typ, desc, image_bytes, points):
    aid = "a" + uuid.uuid4().hex[:8]
    img_b64 = None
    if image_bytes:
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")
    rec = {"id": aid, "userId": userId, "classId": classId, "schoolId": schoolId,
           "type": typ, "description": desc, "image": img_b64, "points": points,
           "status": "pending", "createdAt": now_ms()}
    st.session_state["app_data"]["actions"].append(rec)
    save_data(st.session_state["app_data"])
    return rec

def update_action(action_id, patch):
    for i, a in enumerate(st.session_state["app_data"]["actions"]):
        if a.get("id") == action_id:
            st.session_state["app_data"]["actions"][i] = {**a, **patch}
            save_data(st.session_state["app_data"])
            return st.session_state["app_data"]["actions"][i]
    return None

def compute_points_for_user(userId):
    total = 0
    for a in st.session_state["app_data"]["actions"]:
        if a.get("userId")==userId and a.get("status")=="approved":
            total += a.get("points",0)
    return total

def compute_points_for_class(classId):
    total = 0
    for a in st.session_state["app_data"]["actions"]:
        if a.get("classId")==classId and a.get("status")=="approved":
            total += a.get("points",0)
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
            schools = st.session_state["app_data"]["schools"]
            school_options = [""] + [f'{s.get("province")} • {s.get("name")}' for s in schools]
            r_school_choice = st.selectbox("Trường (tùy chọn)", school_options)
            r_schoolId = None
            r_classId = None
            if r_school_choice:
                r_schoolId = next((s.get("id") for s in schools if f'{s.get("province")} • {s.get("name")}'==r_school_choice), None)
                classes = [c for c in st.session_state["app_data"]["classes"] if c.get("schoolId")==r_schoolId]
                class_names = [""] + [c.get("name") for c in classes]
                r_class_name = st.selectbox("Lớp (tùy chọn)", class_names)
                if r_class_name:
                    r_classId = next((c.get("id") for c in classes if c.get("name")==r_class_name), None)
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
# Dashboard
# ------------------------
def dashboard_page():
    uid = st.session_state.get("current_user_id")
    user = find_user_by_id(uid)
    if not user:
        st.session_state["page"] = "auth"
        st.experimental_rerun()
        return

    st.sidebar.markdown(f"**{user.get('name')}**  \n_{user.get('role')}_")
    if user.get("schoolId"):
        school = find_school_by_id(user.get("schoolId"))
        if school:
            st.sidebar.markdown(f"🏫 {school.get('name')}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state["current_user_id"] = None
        st.session_state["page"] = "auth"
        st.experimental_rerun()

    # Tabs cho dashboard
    tabs = st.tabs(["Trang chính", "Upload ảnh xanh", "Điểm & Bảng xếp hạng", "Cài đặt"])
    main_tab, upload_tab, score_tab, setting_tab = tabs

    with main_tab:
        st.subheader(f"Xin chào, {user.get('name')} — {user.get('role')}")

    with upload_tab:
        st.subheader("🌱 Chia sẻ hành vi xanh (upload ảnh + status)")
        typ = st.selectbox("Loại hành vi", ["Nhặt rác", "Tiết kiệm điện", "Tái chế giấy", "Đi xe đạp", "Khác"])
        desc = st.text_area("Mô tả ngắn")
        img = st.file_uploader("Ảnh (tùy chọn)", type=["png","jpg","jpeg"])
        pts_map = {"Nhặt rác":3,"Tiết kiệm điện":2,"Tái chế giấy":2,"Đi xe đạp":2,"Khác":1}
        if st.button("Gửi hành vi"):
            if not desc.strip():
                st.warning("Nhập mô tả ngắn nhé.")
            else:
                img_bytes = img.read() if img else None
                add_action(user.get("id"), user.get("classId"), user.get("schoolId"), typ, desc.strip(), img_bytes, pts_map.get(typ,1))
                st.success("Gửi thành công — chờ duyệt.")
                st.experimental_rerun()

# ------------------------
# Main
# ------------------------
def main():
    if st.session_state["page"] == "auth":
        auth_page()
    elif st.session_state["page"] == "dashboard":
        dashboard_page()
    else:
        st.session_state["page"] = "auth"
        auth_page()

if __name__ == "__main__":
    main()
    with score_tab:
        st.subheader("📊 Điểm & Bảng xếp hạng")
        user_points = compute_points_for_user(uid)
        st.markdown(f"**Tổng điểm cá nhân:** {user_points} điểm")

        # Bảng xếp hạng cá nhân trong lớp
        if user.get("classId"):
            class_members = [u for u in st.session_state["app_data"]["users"] if u.get("classId")==user.get("classId")]
            ranking = sorted([(u.get("name"), compute_points_for_user(u.get("id"))) for u in class_members], key=lambda x: x[1], reverse=True)
            st.markdown("**🏆 Bảng xếp hạng cá nhân trong lớp:**")
            for i, (n, p) in enumerate(ranking,1):
                st.write(f"{i}. {n} — {p} điểm")

        # Bảng xếp hạng lớp trong trường
        if user.get("schoolId"):
            classes_in_school = [c for c in st.session_state["app_data"]["classes"] if c.get("schoolId")==user.get("schoolId")]
            class_scores = [(c.get("name"), compute_points_for_class(c.get("id"))) for c in classes_in_school]
            class_scores_sorted = sorted(class_scores, key=lambda x:x[1], reverse=True)
            st.markdown("**📚 Bảng xếp hạng lớp trong trường:**")
            for i, (cls, pts) in enumerate(class_scores_sorted,1):
                st.write(f"{i}. {cls} — {pts} điểm")

    with setting_tab:
        st.subheader("⚙️ Cài đặt & Thông tin cá nhân")
        with st.form("setting_form"):
            s_name = st.text_input("Họ và tên", value=user.get("name"))
            s_phone = st.text_input("Số điện thoại", value=user.get("phone"))
            s_pwd = st.text_input("Mật khẩu", type="password", value=user.get("password"))
            s_role = st.selectbox("Chức vụ", ["Học sinh", "Ban cán sự lớp", "Giáo viên chủ nhiệm", "Ban quản lý nhà trường"], index=["Học sinh", "Ban cán sự lớp", "Giáo viên chủ nhiệm", "Ban quản lý nhà trường"].index(user.get("role")))
            s_province = st.text_input("Tỉnh/Thành phố", value=user.get("province",""))
            s_district = st.text_input("Quận/Huyện", value=user.get("district",""))

            schools = st.session_state["app_data"]["schools"]
            school_names = [""] + [s.get("name") for s in schools]
            s_school_name = st.selectbox("Trường", school_names, index=school_names.index(find_school_by_id(user.get("schoolId")).get("name")) if user.get("schoolId") else 0)
            s_schoolId = next((s.get("id") for s in schools if s.get("name")==s_school_name), None)
            classes_in_school = [c for c in st.session_state["app_data"]["classes"] if c.get("schoolId")==s_schoolId]
            class_names = [""] + [c.get("name") for c in classes_in_school]
            s_class_name = st.selectbox("Lớp", class_names, index=class_names.index(find_class_by_id(user.get("classId")).get("name")) if user.get("classId") else 0)
            s_classId = next((c.get("id") for c in classes_in_school if c.get("name")==s_class_name), None)

            submitted_setting = st.form_submit_button("Cập nhật thông tin")
            if submitted_setting:
                user.update({
                    "name": s_name,
                    "phone": s_phone,
                    "password": s_pwd,
                    "role": s_role,
                    "province": s_province,
                    "district": s_district,
                    "schoolId": s_schoolId,
                    "classId": s_classId
                })
                save_data(st.session_state["app_data"])
                st.success("Cập nhật thành công")
                st.experimental_rerun()

        # Lịch sử điểm cả năm
        st.subheader("📜 Lịch sử điểm hành vi cả năm")
        actions_user = [a for a in st.session_state["app_data"]["actions"] if a.get("userId")==uid]
        actions_user_sorted = sorted(actions_user, key=lambda x:x.get("createdAt"), reverse=True)
        for a in actions_user_sorted:
            dt = datetime.fromtimestamp(a.get("createdAt")/1000).strftime("%d/%m/%Y %H:%M")
            status_icon = "✅" if a.get("status")=="approved" else "⏳"
            st.write(f"{dt} — [{a.get('type')}] {a.get('description')} — +{a.get('points')} điểm {status_icon}")
