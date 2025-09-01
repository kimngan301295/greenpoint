# app.py — GreenPoint (Streamlit) — full working demo
# Copy/paste toàn bộ file này. Không dùng tab, chỉ 4 spaces indent.
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
    except Exception:
        # environment may be read-only; fallback to session state only
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
if "app_data" not in st.rerun().:
    st.rerun().["app_data"] = load_data()
else:
    # ensure we have data even if file empty
    if not isinstance(st.session_state["app_data"], dict):
        st.session_state["app_data"] = seed_data()

if "current_user_id" not in st.session_state:
    st.session_state["current_user_id"] = None
if "page" not in st.session_state:
    st.session_state["page"] = "auth"  # auth | dashboard | ranking

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

def compute_points_for_user(userId, days=7):
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
# Auth page (login / register)
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
                st.rerun().
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
                        st.rerun().

# ------------------------
# Dashboard (role-based)
# ------------------------
def dashboard_page():
    uid = st.session_state.get("current_user_id")
    user = find_user_by_id(uid)
    if not user:
        st.session_state["page"] = "auth"
        st.rerun().
        return

    # Sidebar: info + logout + navigation
    st.sidebar.markdown(f"**{user.get('name')}**  \n_{user.get('role')}_")
    if user.get("schoolId"):
        school = find_school_by_id(user.get("schoolId"))
        if school:
            st.sidebar.markdown(f"🏫 {school.get('name')}")
    if st.sidebar.button("Đăng xuất"):
        st.session_state["current_user_id"] = None
        st.session_state["page"] = "auth"
        st.rerun().

    page = st.sidebar.radio("Trang", ["Bảng chính", "Bảng xếp hạng"])

    if page == "Bảng xếp hạng":
        ranking_page()
        return

    st.title(f"Xin chào, {user.get('name')} — {user.get('role')}")
    st.markdown("App ưu tiên nhẹ nhàng: mục tiêu cá nhân ≥10/tuần, lớp ≥100/30 ngày — khuyến khích, không gây áp lực.")

    # ------------------------
    # Học sinh
    # ------------------------
    if user.get("role") == "Học sinh":
        st.subheader("🌱 Điểm cá nhân")
        weekly_pts = compute_points_for_user(user.get("id"), days=7)
        st.metric("Điểm tuần (mục tiêu nhẹ ≥10)", weekly_pts)
        st.progress(min(1.0, weekly_pts / 10) if weekly_pts >= 0 else 0)

        st.subheader("🏫 Điểm lớp (30 ngày)")
        if user.get("classId"):
            class_pts = compute_points_for_class(user.get("classId"), days=30)
            st.write(f"Lớp: {find_class_by_id(user.get('classId')).get('name')} — {class_pts}/100")
            st.progress(min(1.0, class_pts / 100))
            if class_pts >= 100:
                st.success("🎉 Lớp đạt chuẩn — được tuyên dương!")
            else:
                st.info(f"Cần {max(0,100-class_pts)} điểm nữa để đạt chuẩn (mục tiêu lớp: 100).")
        else:
            st.info("Bạn chưa chọn lớp trong hồ sơ.")

        st.subheader("➕ Gửi hành vi xanh (đơn giản, không áp lực)")
        typ = st.selectbox("Loại hành vi", ["Nhặt rác", "Tiết kiệm điện", "Tái chế giấy", "Đi xe đạp", "Khác"])
        desc = st.text_input("Mô tả ngắn")
        img = st.file_uploader("Ảnh (tùy chọn)", type=["png", "jpg", "jpeg"])
        pts_map = {"Nhặt rác": 3, "Tiết kiệm điện": 2, "Tái chế giấy": 2, "Đi xe đạp": 2, "Khác": 1}
        if st.button("Gửi để duyệt"):
            if not desc.strip():
                st.warning("Nhập mô tả ngắn nhé (1-2 câu).")
            else:
                img_bytes = img.read() if img is not None else None
                add_action(user.get("id"), user.get("classId"), user.get("schoolId"), typ, desc.strip(), img_bytes, pts_map.get(typ,1))
                st.success("Gửi thành công — chờ Ban cán sự duyệt (khuyến khích phản hồi tích cực).")
                st.rerun().

    # ------------------------
    # Ban cán sự lớp (monitor)
    # ------------------------
    elif user.get("role") == "Ban cán sự lớp":
        st.subheader("🕹 Ban cán sự — Duyệt hành vi (lớp của bạn)")
        pending = [a for a in st.session_state["app_data"]["actions"] if a.get("status") == "pending" and a.get("classId") == user.get("classId")]
        st.info(f"Có {len(pending)} yêu cầu chờ duyệt trong lớp.")
        if not pending:
            st.write("Không có yêu cầu chờ duyệt.")
        for a in sorted(pending, key=lambda x: x.get("createdAt",0), reverse=True):
            u = find_user_by_id(a.get("userId"))
            st.markdown("---")
            st.write(f"**{u.get('name', a.get('userId'))}** — {a.get('type')} • +{a.get('points')} điểm")
            st.write(a.get("description"))
            if a.get("image"):
                try:
                    st.image(base64.b64decode(a.get("image")), width=320)
                except:
                    pass
            col1, col2, col3 = st.columns([1,1,1])
            if col1.button("✔ Duyệt", key=f"ap_{a.get('id')}"):
                update_action(a.get("id"), {"status": "approved"})
                st.success("Đã duyệt — điểm sẽ được cộng.")
                st.rerun().
            if col2.button("✖ Từ chối", key=f"rej_{a.get('id')}"):
                update_action(a.get("id"), {"status": "rejected"})
                st.info("Đã từ chối.")
                st.rerun().
            if col3.button("⚠ Trừ điểm", key=f"pen_{a.get('id')}"):
                add_action(a.get("userId"), a.get("classId"), a.get("schoolId"), "Penalty", "Trừ điểm (quyết định cán sự)", None, -2)
                update_action(a.get("id"), {"status": "rejected"})
                st.warning("Đã trừ điểm (penalty).")
                st.rerun().

    # ------------------------
    # Giáo viên chủ nhiệm
    # ------------------------
    elif user.get("role") == "Giáo viên chủ nhiệm":
        st.subheader("📈 Giáo viên chủ nhiệm — Tổng quan lớp/trường")
        classes = [c for c in st.session_state["app_data"]["classes"] if c.get("schoolId") == user.get("schoolId")]
        if not classes:
            st.info("Không có lớp trong trường bạn (demo).")
        for c in classes:
            pts = compute_points_for_class(c.get("id"), days=30)
            st.write(f"Lớp {c.get('name')} — {pts} điểm (30d)")
        st.markdown("---")
        st.subheader("🏅 Top cá nhân (30d) — trong trường")
        cutoff = int((time.time() - 30*24*3600) * 1000)
        approved = [a for a in st.session_state["app_data"]["actions"] if a.get("status") == "approved" and a.get("createdAt",0) >= cutoff and a.get("schoolId") == user.get("schoolId")]
        by_user = {}
        for a in approved:
            by_user[a.get("userId")] = by_user.get(a.get("userId"), 0) + int(a.get("points",0))
        top = sorted(by_user.items(), key=lambda x: -x[1])[:10]
        if top:
            for uid, pts in top:
                u = find_user_by_id(uid)
                st.write(f"{u.get('name')} — {pts} điểm")
        else:
            st.info("Chưa có ai được duyệt trong 30 ngày.")

    # ------------------------
    # Ban quản lý nhà trường (admin)
    # ------------------------
    elif user.get("role") == "Ban quản lý nhà trường":
        st.subheader("🏫 Ban quản lý — Xem thi đua các lớp")
        provinces = sorted(list({s.get("province") for s in st.session_state["app_data"]["schools"]}))
        prov = st.selectbox("Tỉnh/TP", [""] + provinces)
        districts = sorted(list({s.get("district") for s in st.session_state["app_data"]["schools"] if (not prov or s.get("province")==prov)}))
        dist = st.selectbox("Quận/Huyện", [""] + districts)
        school_list = [s for s in st.session_state["app_data"]["schools"] if (not prov or s.get("province")==prov) and (not dist or s.get("district")==dist)]
        if school_list:
            school_names = [""] + [s.get("name") for s in school_list]
            chosen = st.selectbox("Trường", school_names)
            if chosen:
                school_obj = next((s for s in school_list if s.get("name")==chosen), None)
                classes = [c for c in st.session_state["app_data"]["classes"] if c.get("schoolId")==school_obj.get("id")]
                rows = []
                for c in classes:
                    pts = compute_points_for_class(c.get("id"), days=30)
                    status = "🏆 Đạt chuẩn" if pts >= 100 else "⚠ Cần cố gắng"
                    rows.append({"Lớp": c.get("name"), "Điểm(30d)": pts, "Trạng thái": status})
                st.table(rows)
                # export CSV
                csv_buf = BytesIO()
                writer = csv.writer(csv_buf)
                writer.writerow(["Lớp","Điểm(30d)","Trạng thái"])
                for r in rows:
                    writer.writerow([r["Lớp"], r["Điểm(30d)"], r["Trạng thái"]])
                st.download_button("📑 Tải CSV báo cáo", data=csv_buf.getvalue(), file_name="school_report.csv", mime="text/csv")
        else:
            st.info("Chưa có trường trong dữ liệu demo (seed).")

# ------------------------
# Ranking (global)
# ------------------------
def ranking_page():
    st.title("🏆 Bảng xếp hạng (30 ngày)")
    classes = st.session_state["app_data"]["classes"]
    totals = []
    for c in classes:
        pts = compute_points_for_class(c.get("id"), days=30)
        school_name = next((s.get("name") for s in st.session_state["app_data"]["schools"] if s.get("id")==c.get("schoolId")), "")
        totals.append({"class": f"{c.get('name')} ({school_name})", "points": pts})
    totals = sorted(totals, key=lambda x: -x["points"])
    st.subheader("Top lớp")
    for i, r in enumerate(totals[:10], start=1):
        st.write(f"#{i} {r['class']} — {r['points']} điểm")

    st.subheader("Top cá nhân")
    cutoff = int((time.time() - 30*24*3600) * 1000)
    approved = [a for a in st.session_state["app_data"]["actions"] if a.get("status")=="approved" and a.get("createdAt",0) >= cutoff]
    by_user = {}
    for a in approved:
        by_user[a.get("userId")] = by_user.get(a.get("userId"), 0) + int(a.get("points",0))
    top_users = sorted(by_user.items(), key=lambda x: -x[1])[:10]
    for i, (uid, pts) in enumerate(top_users, start=1):
        u = find_user_by_id(uid)
        st.write(f"#{i} {u.get('name')} ({u.get('classId', '-')}) — {pts} điểm")

# ------------------------
# Main routing
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
