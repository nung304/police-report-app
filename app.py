import streamlit as st
from datetime import datetime
import google.auth
from google.cloud import firestore
from google.oauth2 import service_account
import time

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="รายงานสอบสวน สภ.ไม้แก่น", page_icon="👮‍♂️", layout="wide", initial_sidebar_state="collapsed")

# --- การเชื่อมต่อ Firestore ---
@st.cache_resource
def get_firestore_client():
    credentials_info = st.secrets["firebase"]
    creds = service_account.Credentials.from_service_account_info(credentials_info)
    return firestore.Client(credentials=creds, project=credentials_info["project_id"])

db = get_firestore_client()

# --- CSS ปรับแต่ง (เน้นลดช่องว่างให้กระชับขึ้น) ---
st.markdown("""
    <style>
        /* จัดกรอบคอลัมน์ */
        .stColumn > div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            padding: 15px !important; /* ลด padding ลง */
            margin-bottom: 10px !important; /* ลดช่องว่างด้านล่าง */
        }
        
        /* สลับสีพื้นหลังแบบกระชับ */
        .list-row-even {
            background-color: #f8fafc;
            padding: 6px 10px !important; /* ปรับ padding ให้เล็กลง */
            border-radius: 4px;
            margin-bottom: 2px !important; /* ลด margin ระหว่างแถว */
            font-size: 0.9em;
        }
        .list-row-odd {
            background-color: #ffffff;
            padding: 6px 10px !important;
            border-radius: 4px;
            margin-bottom: 2px !important;
            font-size: 0.9em;
        }
        
        @media (prefers-color-scheme: dark) {
            .list-row-even { background-color: #1e293b; }
            .list-row-odd { background-color: #0f172a; }
        }
    </style>
""", unsafe_allow_html=True)

# --- ฟังก์ชันจัดการข้อมูล (ตัดมาเฉพาะส่วนที่แสดงผล) ---
def load_data(collection):
    docs = db.collection(collection).stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        data.append(d)
    return data

# ตัวอย่างการแสดงผลใน Expander หลังบ้าน
with st.expander("⚙️ ตั้งค่าระบบหลังบ้าน"):
    st.markdown("#### 👤 จัดการรายชื่อเจ้าหน้าที่")
    personnel_list = load_data("personnel")
    for idx, person in enumerate(personnel_list):
        bg_class = "list-row-even" if idx % 2 == 0 else "list-row-odd"
        st.markdown(f'<div class="{bg_class}">', unsafe_allow_html=True)
        col1, col2 = st.columns([8, 2])
        col1.write(f"{person['rank']}{person['name']} - {person['position']}")
        if col2.button("🗑️ ลบ", key=f"del_{person['id']}"):
            db.collection("personnel").document(person['id']).delete()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
