import streamlit as st

# ------------------------
# CẤU HÌNH APP
# ------------------------
st.set_page_config(page_title="Thi đua xanh", layout="wide")

# ------------------------
# THANH MENU
# ------------------------
menu = st.sidebar.radio(
    "Chọn giao diện",
    ["🏫 Ban quản lý nhà trường", "👨‍🏫 Giáo viên chủ nhiệm", "🧑‍🎓 Ban cán sự lớp", "👩‍👩‍👧‍👦 Học sinh"]
)

# ------------------------
# BAN QUẢN LÝ NHÀ TRƯỜNG
# ------------------------
if menu == "🏫 Ban quản lý nhà trường":
    st.title("🏫 Trang quản lý thi đua toàn trường")
    province = st.selectbox("Chọn Tỉnh/Thành phố", ["TP.HCM", "Hà Nội", "Đà Nẵng"])
    district = st.selectbox("Chọn Quận/Huyện", ["Quận 1", "Quận 2", "Quận 3"])
    school = st.selectbox("Chọn Trường", ["THCS A", "THCS B", "THCS C"])
    st.subheader(f"Điểm thi đua của {school}")
    st.progress(0.75)  # ví dụ lớp đạt 75%

# ------------------------
# GIÁO VIÊN CHỦ NHIỆM
# ------------------------
elif menu == "👨‍🏫 Giáo viên chủ nhiệm":
    st.title("👨‍🏫 Trang quản lý của GVCN")
    st.write("📊 Xem và xác nhận điểm thi đua của lớp mình.")

    st.metric("Điểm lớp", "120", "👍 Đạt yêu cầu")
    st.dataframe({
        "Học sinh": ["Nguyễn A", "Trần B", "Lê C"],
        "Điểm tuần": [15, 25, 8]
    })

# ------------------------
# BAN CÁN SỰ LỚP
# ------------------------
elif menu == "🧑‍🎓 Ban cán sự lớp":
    st.title("🧑‍🎓 Trang quản lý của Ban cán sự")
    st.write("✅ Cộng điểm hoặc trừ điểm hành vi xanh cho thành viên lớp.")
    name = st.selectbox("Chọn học sinh", ["Nguyễn A", "Trần B", "Lê C"])
    action = st.radio("Hành động", ["Cộng điểm", "Trừ điểm"])
    points = st.number_input("Số điểm", 1, 10, 1)
    if st.button("Xác nhận"):
        st.success(f"Đã {action.lower()} {points} điểm cho {name}")

# ------------------------
# HỌC SINH
# ------------------------
elif menu == "👩‍👩‍👧‍👦 Học sinh":
    st.title("👩‍👩‍👧‍👦 Giao diện Học sinh")
    st.write("📌 Xem điểm cá nhân và đóng góp cho lớp.")
    st.metric("Điểm tuần của bạn", "18", "⚠️ Cần cố gắng")
    st.metric("Điểm lớp", "120", "👍 Đạt chuẩn")
