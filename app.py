import os
import json
from datetime import datetime
import streamlit as st

# ----------------------------------------------------
# 1. การตั้งค่าไดเรกทอรีและไฟล์เก็บข้อมูล
# ----------------------------------------------------
UPLOAD_DIR = "uploaded_images"  # โฟลเดอร์สำหรับเก็บรูปภาพทั้งหมด
DATA_FILE = "messages_data.json" # ไฟล์ JSON สำหรับเก็บประวัติข้อความ

# สร้างโฟลเดอร์เก็บภาพให้อัตโนมัติหากยังไม่มี
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ----------------------------------------------------
# 2. ฟังก์ชันจัดการข้อมูล (Data Management Functions)
# ----------------------------------------------------
def load_messages():
    """โหลดประวัติข้อความจากไฟล์ JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_message(text_content, image_path=None):
    """บันทึกข้อความและ Path ของรูปภาพลงไฟล์ JSON"""
    messages = load_messages()
    new_entry = {
        "id": len(messages) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text_content,
        "image_path": image_path
    }
    messages.append(new_entry)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

def get_stored_images():
    """ดึงรายชื่อไฟล์รูปภาพที่มีทั้งหมดในโฟลเดอร์คลังภาพ"""
    valid_extensions = (".jpg", ".jpeg", ".png", ".webp")
    if os.path.exists(UPLOAD_DIR):
        files = [f for f in os.listdir(UPLOAD_DIR) if f.lower().endswith(valid_extensions)]
        files.sort(reverse=True) # เอาไฟล์ใหม่ขึ้นก่อน
        return files
    return []

# ----------------------------------------------------
# 3. ส่วนการแสดงผล UI (Streamlit Interface)
# ----------------------------------------------------
st.set_page_config(page_title="ระบบส่งข้อความพร้อมรูปภาพ", layout="centered")

st.title("💬 ระบบส่งข้อความและจัดการรูปภาพ")
st.write("พิมพ์ข้อความ พร้อมเลือกรูปภาพจากคลัง หรืออัปโหลดภาพใหม่เพื่อส่งร่วมกัน")

st.divider()

# --- ฟอร์มส่งข้อความ ---
st.subheader("📝 ส่งข้อความใหม่")

with st.form("message_form", clear_on_submit=True):
    # กล่องพิมพ์ข้อความ
    message_text = st.text_area("เนื้อหาข้อความ:", placeholder="พิมพ์ข้อความที่ต้องการส่งที่นี่...")

    # ส่วนการจัดการภาพ
    st.write("**🖼️ แนบรูปภาพ (เลือกอย่างใดอย่างหนึ่ง หรือไม่อยู่ในเงื่อนไขก็ได้):**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ตัวเลือกที่ 1: อัปโหลดภาพใหม่
        uploaded_file = st.file_uploader("อัปโหลดภาพใหม่:", type=["jpg", "jpeg", "png", "webp"])
        
    with col2:
        # ตัวเลือกที่ 2: เลือกภาพที่มีอยู่แล้วในคลัง
        existing_images = get_stored_images()
        selected_gallery_img = st.selectbox(
            "หรือเลือกภาพจากคลังเดิม:",
            options=["-- ไม่เลือกภาพจากคลัง --"] + existing_images
        )

    # ปุ่มส่งข้อความ
    submit_button = st.form_submit_button("🚀 ส่งข้อความ", use_container_width=True)

# --- ประมวลผลเมื่อกดปุ่มส่ง ---
if submit_button:
    final_image_path = None
    
    # 1. จัดการรูปภาพอัปโหลดใหม่ (ให้สิทธิ์สูงสุด)
    if uploaded_file is not None:
        filename = f"{int(datetime.now().timestamp())}_{uploaded_file.name}"
        final_image_path = os.path.join(UPLOAD_DIR, filename)
        with open(final_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
    # 2. ถ้าไม่อัปโหลดใหม่ แต่เลือกภาพจากคลังเดิม
    elif selected_gallery_img != "-- ไม่เลือกภาพจากคลัง --":
        final_image_path = os.path.join(UPLOAD_DIR, selected_gallery_img)

    # บันทึกข้อมูล (ต้องมีข้อความหรือรูปภาพอย่างน้อย 1 อย่าง)
    if message_text.strip() or final_image_path:
        save_message(message_text, final_image_path)
        st.success("บันทึกและส่งข้อความเรียบร้อยแล้ว!")
        st.rerun()
    else:
        st.warning("⚠️ กรุณากรอกข้อความ หรือเลือก/อัปโหลดรูปภาพอย่างน้อยหนึ่งอย่าง")

st.divider()

# --- ส่วนแสดงประวัติข้อความ (Message Feed) ---
st.subheader("📜 ประวัติรายการข้อความ")

all_messages = load_messages()

if not all_messages:
    st.info("ยังไม่มีข้อความในระบบ")
else:
    # แสดงผลรายการล่าสุดขึ้นก่อน (Reversed)
    for msg in reversed(all_messages):
        with st.chat_message("user"):
            st.caption(f"🕒 {msg['timestamp']}")
            
            # แสดงข้อความ
            if msg.get("text"):
                st.write(msg["text"])
                
            # แสดงรูปภาพแนบ (ถ้ามี)
            img_path = msg.get("image_path")
            if img_path and os.path.exists(img_path):
                st.image(img_path, caption=os.path.basename(img_path), use_container_width=True)
