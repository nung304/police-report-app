import streamlit as st
import datetime
from datetime import timezone, timedelta
import requests
import json

# ==========================================
# 1. การตั้งค่าหน้าเว็บ & เวลา (Timezone UTC+7)
# ==========================================
st.set_page_config(
    page_title="ระบบรายงานสรุปผลการปฏิบัติงาน สภ.ไม้แก่น",
    page_icon="ตำรวจ",
    layout="wide"
)

# กำหนดเวลามาตรฐานประเทศไทย (UTC+7)
TZ_THAI = timezone(timedelta(hours=7))

def get_current_thai_datetime():
    return datetime.datetime.now(TZ_THAI)

# ==========================================
# 2. ฟังก์ชั่นเรียงลำดับอาวุโสยศตำรวจ (Rank Priority)
# ==========================================
RANK_ORDER = {
    "พล.ต.อ.": 1, "พล.ต.ท.": 2, "พล.ต.ต.": 3,
    "พ.ต.อ.": 4, "พ.ต.ท.": 5, "พ.ต.ต.": 6,
    "ร.ต.อ.": 7, "ร.ต.ท.": 8, "ร.ต.ต.": 9,
    "ด.ต.": 10, "จ.ส.ต.": 11, "ส.ต.อ.": 12, "ส.ต.ท.": 13, "ส.ต.ต.": 14
}

def get_rank_priority(personnel_name):
    """ คืนค่าตัวเลขลำดับความสำคัญของยศ เพื่อนำไปใช้ sort() """
    for rank, priority in RANK_ORDER.items():
        if rank in personnel_name:
            return priority
    return 99  # กรณีไม่พบยศ ให้ไว้อยู่ท้ายสุด

# ==========================================
# 3. การเชื่อมต่อบริการภายนอก (LINE / Cloudinary)
# ==========================================
def send_line_oa_push(channel_access_token, target_id, message_text):
    """ ส่งข้อความเข้ากลุ่ม/ผู้ใช้ผ่าน LINE Messaging API Push """
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }
    payload = {
        "to": target_id,
        "messages": [{"type": "text", "text": message_text}]
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        return response.status_code == 200, response.json()
    except Exception as e:
        return False, str(e)

# ==========================================
# 4. ส่วนแสดงผลหลัก (Streamlit Interface)
# ==========================================
st.title("🛡️ ระบบรายงานสรุปผลการปฏิบัติงาน สภ.ไม้แก่น")
st.caption(f"วันที่ปัจจุบัน: {get_current_thai_datetime().strftime('%d/%m/%Y %H:%M น.')}")

tab1, tab2, tab3 = st.tabs([
    "📝 รายงานแยกรายบุคคล/เวลา", 
    "📋 รายงานรูปแบบมาตรฐาน", 
    "⚙️ จัดการคลังภารกิจ & รายชื่อ"
])

# ------------------------------------------
# TAB 1: รายงานแยกรายบุคคล/เวลา
# ------------------------------------------
with tab1:
    st.subheader("สร้างข้อความรายงานประจำวัน")
    
    col1, col2 = st.columns(2)
    with col1:
        report_date = st.date_input("วันที่ปฏิบัติงาน", get_current_thai_datetime().date())
        duty_shift = st.selectbox("ผลการปฏิบัติหน้าที่", ["ผลการปฏิบัติเวรประจำวัน", "ภารกิจพิเศษ/สนับสนุน"])
    
    with col2:
        reporter_name = st.text_input("ผู้ลงนาม/ผู้รายงาน", value="ส.ต.ต.สุริยา บุญชูดวง")
        station_name = st.text_input("หน่วยงาน", value="สภ.ไม้แก่น จว.ปัตตานี")
    
    task_detail = st.text_area("รายละเอียดการปฏิบัติงาน / เหตุการณ์สำคัญ", height=150)
    
    if st.button("🚀 สร้างข้อความรายงาน", type="primary"):
        formatted_report = (
            f"เรียน ผู้บังคับบัญชา\n"
            f"สภ.ไม้แก่น ขอรายงานผลการปฏิบัติงาน ประจำวันที่ {report_date.strftime('%d/%m/%Y')}\n"
            f"-----------------------------------\n"
            f"📌 {duty_shift}\n"
            f"{task_detail}\n"
            f"-----------------------------------\n"
            f"ผู้รายงาน: {reporter_name}\n"
            f"หน่วยงาน: {station_name}"
        )
        st.success("สร้างข้อความรายงานเรียบร้อยแล้ว!")
        st.code(formatted_report, language="text")

# ------------------------------------------
# TAB 2: รายงานรูปแบบมาตรฐาน
# ------------------------------------------
with tab2:
    st.subheader("รายงานรูปแบบสรุปผู้ปฏิบัติงาน")
    # สามารถดึงรายชื่อจาก Firestore แล้วนำมาจัดลำดับด้วย get_rank_priority()
    sample_personnel = ["ส.ต.อ. สมชาย เข็มกลัด", "พ.ต.ท. สมศักดิ์ ภักดี", "ร.ต.อ. วิชัย ใจดี", "ส.ต.ต.สุริยา บุญชูดวง"]
    sorted_personnel = sorted(sample_personnel, key=get_rank_priority)
    
    st.markdown("**รายชื่อเจ้าหน้าที่ผู้ปฏิบัติงาน (เรียงตามลำดับยศ):**")
    for idx, name in enumerate(sorted_personnel, 1):
        st.write(f"{idx}. {name}")

# ------------------------------------------
# TAB 3: จัดการคลังภารกิจ & รายชื่อ (CRUD)
# ------------------------------------------
with tab3:
    st.subheader("จัดการข้อมูลในระบบ")
    st.info("ส่วนนี้ใช้สำหรับบันทึก เพิ่ม ลด หรือแก้ไขหัวข้อภารกิจและรายชื่อข้าราชการตำรวจในฐานข้อมูล Firestore")
