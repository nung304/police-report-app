from datetime import datetime
import io
import time
import urllib.parse
from firebase_admin import storage  # เพิ่มการใช้งาน Firebase Storage
from google.cloud import firestore
from google.oauth2 import service_account
import requests
import streamlit as st

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(
    page_title="รายงานสอบสวน สภ.ไม้แก่น",
    page_icon="👮‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ... (ส่วน Meta Tags เดิม) ...


# --- 3. เชื่อมต่อฐานข้อมูล Firebase Firestore & Storage ---
@st.cache_resource
def get_firebase_clients():
    cred_dict = dict(st.secrets["firebase"])
    if "private_key" in cred_dict:
        cred_dict["private_key"] = (
            cred_dict["private_key"].replace("\\n", "\n").strip()
        )

    creds = service_account.Credentials.from_service_account_info(cred_dict)
    db = firestore.Client(credentials=creds, project=cred_dict["project_id"])
    return db, creds, cred_dict["project_id"]


db, creds, project_id = get_firebase_clients()


# ฟังก์ชันอัปโหลดรูปภาพขึ้น Firebase Storage เพื่อรับ Public URL
def upload_image_to_storage(uploaded_file):
    try:
        # ใช้ Bucket Name ตาม Project ID ของ Firebase (หรือระบุใน secrets เช่น st.secrets["firebase"]["storage_bucket"])
        bucket_name = st.secrets["firebase"].get(
            "storage_bucket", f"{project_id}.appspot.com"
        )

        from google.cloud import storage as gcs

        storage_client = gcs.Client(credentials=creds, project=project_id)
        bucket = storage_client.bucket(bucket_name)

        # ตั้งชื่อไฟล์แบบไม่ซ้ำกันตามเวลา
        file_name = (
            f"reports/{int(time.time())}_{uploaded_file.name.replace(' ', '_')}"
        )
        blob = bucket.blob(file_name)

        # อัปโหลดไฟล์
        blob.upload_from_file(
            uploaded_file, content_type=uploaded_file.type
        )

        # กำหนดให้ไฟล์เปิดอ่านแบบ Public หรือสร้าง Public URL
        blob.make_public()
        return blob.public_url
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ: {e}")
        return None
