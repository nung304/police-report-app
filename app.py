import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import requests
import json

# ==========================================
# 1. INITIALIZE FIREBASE (ระบบฐานข้อมูล)
# ==========================================
if not firebase_admin._apps:
    try:
        # แปลง st.secrets["firebase"] ให้เป็น Pure Dict เพื่อป้องกันปัญหา Certificate Error
        firebase_dict = json.loads(json.dumps(dict(st.secrets["firebase"])))
        
        # จัดการเรื่อง \n ใน private_key ให้ถูกต้อง
        if "private_key" in firebase_dict:
            firebase_dict["private_key"] = firebase_dict["private_key"].replace("\\n", "\n")
        
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ Firebase: {e}")

db = firestore.client()

# ==========================================
# 2. FUNCTION SEND LINE MESSAGE (ระบบส่งไลน์)
# ==========================================
def send_line_group_message(message_text):
    """ฟังก์ชันส่งข้อความรายงานเข้ากลุ่ม LINE ผ่าน Messaging API (Push Message)"""
    try:
        line_access_token = st.secrets["line"]["channel_access_token"]
        line_group_id = st.secrets["line"]["group_id"]
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {line_access_token}"
        }
        payload = {
            "to": line_group_id,
            "messages": [
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True, "ส่งรายงานเข้ากลุ่ม LINE เรียบร้อยแล้ว!"
        else:
            return False, f"ส่งไม่สำเร็จ (Status {response.status_code}): {response.text}"
            
    except Exception as e:
        return False, f"เกิดข้อผิดพลาดในการส่ง LINE: {str(e)}"

# ==========================================
# 3. STREAMLIT UI (หน้าจอใช้งาน)
# ==========================================
st.set_page_config(page_title="ระบบรายงานผลงานสอบสวน", page_icon="🚓", layout="centered")

st.title("🚓 ระบบจัดทำและส่งรายงานผลงานสอบสวน")
st.caption("สภ.ไม้แก่น จว.ปัตตานี")

st.markdown("---")

# --- ส่วนที่ 1: ฟอร์มกรอกข้อมูลรายงาน ---
st.subheader("📝 กรอกรายละเอียดรายงาน")

case_number = st.text_input("เลขคดี / ปจว. ข้อที่", placeholder="เช่น คดีอาญาที่ 12/2569")
investigator_name = st.text_input("พนักงานสอบสวนผู้รับผิดชอบ", placeholder="เช่น พ.ต.ต. สมชาย ใจดี")
case_detail = st.text_area("รายละเอียดการดำเนินการ / รายงานผล", height=150, placeholder="ระบุรายละเอียดผลการปฏิบัติ...")

# --- ส่วนที่ 2: ประมวลผลสร้างข้อความรายงาน ---
if case_number and case_detail:
    # จัดรูปแบบข้อความที่จะส่งลงกลุ่ม LINE
    report_text = (
        f"📢 รายงานผลการปฏิบัติงานสอบสวน\n"
        f"หน่วย: สภ.ไม้แก่น\n\n"
        f"📌 เลขคดี: {case_number}\n"
        f"👮‍♂️ พนักงานสอบสวน: {investigator_name}\n"
        f"📝 รายละเอียด:\n{case_detail}"
    )

    st.markdown("---")
    st.subheader("📋 ตัวอย่างข้อความที่จะแสดง/ส่งออก")
    
    # แสดงกล่องข้อความสรุป
    st.code(report_text, language="text")

    col1, col2 = st.columns(2)

    # ปุ่มที่ 1: บันทึกลง Firebase อย่างเดียว
    with col1:
        if st.button("💾 บันทึกลงฐานข้อมูล (Firebase)", use_container_width=True):
            try:
                doc_ref = db.collection("reports").document()
                doc_ref.set({
                    "case_number": case_number,
                    "investigator": investigator_name,
                    "detail": case_detail,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
                st.success("บันทึกข้อมูลลง Firebase เรียบร้อย!")
            except Exception as e:
                st.error(f"บันทึก Firebase ไม่สำเร็จ: {e}")

    # ปุ่มที่ 2: บันทึก + ส่งตรงเข้ากลุ่ม LINE ทันที
    with col2:
        if st.button("📲 ส่งรายงานเข้ากลุ่ม LINE ทันที", type="primary", use_container_width=True):
            with st.spinner("กำลังส่งข้อความเข้ากลุ่ม LINE..."):
                # 1. บันทึกลง Firebase ก่อน
                try:
                    db.collection("reports").add({
                        "case_number": case_number,
                        "investigator": investigator_name,
                        "detail": case_detail,
                        "created_at": firestore.SERVER_TIMESTAMP
                    })
                except Exception as e:
                    st.warning(f"บันทึก Firebase ไม่สำเร็จ แต่กำลังลองส่ง LINE: {e}")

                # 2. ส่งข้อความเข้ากลุ่ม LINE
                success, msg = send_line_group_message(report_text)
                
                if success:
                    st.success(msg)
                    st.balloons()
                else:
                    st.error(msg)
else:
    st.info("💡 กรุณากรอกข้อมูลเลขคดีและรายละเอียดเพื่อพรีวิวและส่งรายงาน")
