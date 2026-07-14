import streamlit as st
from datetime import datetime
import google.auth
from google.cloud import firestore
from google.oauth2 import service_account

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="รายงานสอบสวน สภ.ไม้แก่น", page_icon="👮‍♂️", layout="wide")

# --- 1. เชื่อมต่อ Firestore ---
@st.cache_resource
def get_firestore_client():
    credentials_info = st.secrets["firebase"]
    creds = service_account.Credentials.from_service_account_info(credentials_info)
    return firestore.Client(credentials=creds, project=credentials_info["project_id"])

db = get_firestore_client()

# ฟังก์ชันดึงข้อมูล
def load_data(collection):
    docs = db.collection(collection).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

# --- 2. ส่วนแสดงผล ---
st.title("👮‍♂️ ระบบรายงาน Line Group")

# แบ่ง 3 คอลัมน์หลัก
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⏱️ วันที่และเวลา")
    st.date_input("วันที่", datetime.now())
    st.text_input("เวลา (น.)", datetime.now().strftime("%H.%M"))

with col2:
    st.subheader("📝 ภารกิจ")
    st.number_input("จำนวนเรื่อง", 1, 5)

with col3:
    st.subheader("📋 ข้อความสำหรับส่ง")
    st.info("ระบบพร้อมใช้งาน")

# --- 3. ส่วนหลังบ้าน (ใช้เส้นกั้นแยกรายการ) ---
st.markdown("---")
with st.expander("⚙️ ตั้งค่าระบบหลังบ้าน", expanded=False):
    st.write("#### 👤 รายชื่อเจ้าหน้าที่")
    personnel = load_data("personnel")
    
    for p in personnel:
        # ใช้ columns แบ่งพื้นที่ชื่อกับปุ่ม
        c_name, c_btn = st.columns([8, 2])
        c_name.write(f"**{p.get('rank', '')}{p.get('name', '')}** - {p.get('position', '')}")
        
        if c_btn.button("🗑️ ลบ", key=f"del_{p['id']}"):
            db.collection("personnel").document(p['id']).delete()
            st.rerun()
        
        # ขีดเส้นกั้นแต่ละรายการ
        st.divider() 
        
    st.write("#### 📝 รายการภารกิจ")
    tasks = load_data("tasks")
    for t in tasks:
        c_task, c_btn = st.columns([8, 2])
        c_task.write(f"{t.get('task_detail', '')}")
        if c_btn.button("🗑️ ลบ ", key=f"del_t_{t['id']}"):
            db.collection("tasks").document(t['id']).delete()
            st.rerun()
        st.divider()
