import streamlit as st
from datetime import datetime
import google.auth
from google.cloud import firestore
from google.oauth2 import service_account
import time
import base64
from PIL import Image
import io

# ตั้งค่าหน้าจอให้เป็นแบบ "กว้างพิเศษ (Wide)" เพื่อให้แสดงผล 3 คอลัมน์บน PC ได้สวยงามพอดี
st.set_page_config(
    page_title="รายงานสอบสวน สภ.ไม้แก่น", 
    page_icon="👮‍♂️", 
    layout="wide",  # ปรับเป็น wide เพื่อให้เต็มหน้าจอ PC
    initial_sidebar_state="collapsed"
)

# --- ฟังก์ชันย่อขนาดภาพระดับ HD และแปลงเป็น Base64 แบบคำนวณขนาดไฟล์อัตโนมัติ ---
def process_and_get_base64(image_file):
    img = Image.open(image_file)
    max_size = 1920
    img.thumbnail((max_size, max_size))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    quality = 85
    step = 5
    while quality > 30:
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG", quality=quality, optimize=True)
        file_size = len(buffered.getvalue())
        if file_size < 950000:
            encoded = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/jpeg;base64,{encoded}"
        quality -= step
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=30, optimize=True)
    encoded = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{encoded}"

# --- 1. เชื่อมต่อฐานข้อมูล NoSQL (Firebase Firestore) ---
@st.cache_resource
def get_firestore_client():
    credentials_info = st.secrets["firebase"]
    creds = service_account.Credentials.from_service_account_info(credentials_info)
    db = firestore.Client(credentials=creds, project=credentials_info["project_id"])
    return db

db = get_firestore_client()

# --- 2. ฟังก์ชันโหลดและบันทึกภาพพื้นหลังจาก Cloud ---
def load_background_image():
    doc_ref = db.collection("settings").document("current_bg")
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict().get("image_base64", None)
    return None

def save_background_image(image_base64):
    doc_ref = db.collection("settings").document("current_bg")
    doc_ref.set({"image_base64": image_base64})

def delete_background_image():
    doc_ref = db.collection("settings").document("current_bg")
    doc_ref.delete()

# โหลดภาพพื้นหลังจากฐานข้อมูลขึ้นมาแสดงผล
bg_image_base64 = load_background_image()

# ==================== ส่วนควบคุม UI สำหรับปรับสีและการแสดงผล ====================

# 1. จัดการสถานะโหมดสี (Session State) เพื่อล็อกค่าไม่ให้รีเฟรชแล้วเด้งกลับ
if "selected_color_mode" not in st.session_state:
    st.session_state["selected_color_mode"] = "โหมดกล่องขาว ตัวอักษรเข้ม (สำหรับรูปพื้นหลังสีมืด)"

if "selected_opacity" not in st.session_state:
    st.session_state["selected_opacity"] = 90

# แถบควบคุมด้านบนสุด
ctrl_col1, ctrl_col2 = st.columns([2, 1])

with ctrl_col1:
    color_mode = st.radio(
        "🎨 เลือกโหมดสีตัวอักษรและกล่องข้อมูล (ล็อกสถานะไว้ให้หลังจากรีเฟรช)",
        ["โหมดกล่องขาว ตัวอักษรเข้ม (สำหรับรูปพื้นหลังสีมืด)", "โหมดกล่องดำ ตัวอักษรขาว (สำหรับรูปพื้นหลังสีสว่าง)"],
        index=0 if "สำหรับรูปพื้นหลังสีมืด" in st.session_state["selected_color_mode"] else 1,
        horizontal=True,
        key="color_mode_radio"
    )
    # อัปเดตค่าเก็บลง Session State
    st.session_state["selected_color_mode"] = color_mode

with ctrl_col2:
    # เพิ่ม Slider ให้ปรับความโปร่งแสงของกรอบข้อความได้อิสระ
    opacity_percent = st.slider(
        "💡 ปรับค่าความทึบ/โปร่งแสงของกล่อง (%)",
        min_value=10,
        max_value=100,
        value=st.session_state["selected_opacity"],
        step=5,
        key="opacity_slider"
    )
    st.session_state["selected_opacity"] = opacity_percent

# คำนวณค่า Alpha (ความโปร่งแสง 0.0 - 1.0)
alpha = opacity_percent / 100.0

# กำหนดสไตล์ CSS ตามที่ผู้ใช้งานตั้งค่าไว้
if "สำหรับรูปพื้นหลังสีมืด" in st.session_state["selected_color_mode"]:
    # โหมดกล่องขาว และตัวอักษรสีน้ำเงินเข้ม
    card_bg = f"rgba(255, 255, 255, {alpha})"
    text_color = "#0c2340"
    label_color = "#0c2340"
    border_color = f"rgba(12, 35, 64, {min(alpha + 0.1, 1.0)})"
    shadow_color = "rgba(0, 0, 0, 0.2)"
    input_bg = "#ffffff"
    input_text = "#111111"
else:
    # โหมดกล่องดำ และตัวอักษรสีขาวสว่าง
    card_bg = f"rgba(15, 23, 42, {alpha})"
    text_color = "#ffffff"
    label_color = "#38bdf8"  # สีฟ้าสว่าง
    border_color = f"rgba(56, 189, 248, {min(alpha + 0.1, 1.0)})"
    shadow_color = "rgba(0, 0, 0, 0.5)"
    input_bg = "#1e293b"
    input_text = "#ffffff"

# --- ส่วนควบคุม CSS พื้นหลัง, ตัวอักษร และแผ่นเลเยอร์ฟิล์ม ---
bg_style = ""
if bg_image_base64:
    bg_style = f"""
        .stApp {{
            background-image: url("{bg_image_base64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stApp::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(12, 35, 64, 0.25); 
            z-index: -1;
        }}
    """

st.markdown(f"""
    <style>
        {bg_style}
        
        /* สไตล์บังคับกล่อง Container ทั้ง 3 คอลัมน์ */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: {card_bg} !important;
            border-radius: 16px !important;
            border: 2px solid {border_color} !important;
            box-shadow: 0 10px 30px {shadow_color} !important;
            padding: 18px !important;
            backdrop-filter: blur(8px); /* เพิ่มเอฟเฟกต์กระจกฝ้าเมื่อโปร่งแสงเพื่อให้ดูพรีเมียมและอ่านง่ายขึ้น */
        }}
        
        /* สไตล์ตัวอักษรหัวข้อภายในกล่อง */
        h3 {{
            color: {text_color} !important;
            border-left: 5px solid {text_color};
            padding-left: 10px;
            font-weight: bold !important;
        }}
        
        /* สไตล์ชื่อหัวข้อของช่องกรอกข้อมูลต่างๆ */
        label[data-testid="stWidgetLabel"] p {{
            color: {label_color} !important;
            font-weight: bold !important;
        }}
        
        /* สไตล์ข้อความทั่วไปและการแจ้งเตือน */
        .block-container p {{
            color: {text_color} !important;
        }}
        
        /* บังคับช่องกรอกข้อมูล (Input & Selectbox) ให้สีชัดเจนตามโหมด */
        div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input, select {{
            background-color: {input_bg} !important;
            color: {input_text} !important;
        }}
        
        /* สไตล์กล่องผลลัพธ์ Code Block สำหรับก๊อปปี้ */
        div[data-testid="stCodeBlock"] {{
            border: 2px solid #0c2340;
            background-color: #ffffff !important;
        }}
        div[data-testid="stCodeBlock"] span {{
            color: #111111 !important; /* บังคับตัวอักษรในส่วนที่จะก๊อปปี้ไปส่งไลน์ให้เป็นสีดำเข้มคมชัดเสมอ */
        }}
        
        /* สไตล์ปุ่มกดหลัก */
        .stButton>button {{
            width: 100%;
            border-radius: 10px;
            height: 3em;
            background-color: #0c2340 !important;
            color: white !important;
            font-weight: bold;
            border: none;
        }}
        
        /* ปรับแต่งส่วนหัวข้อหลักสุดของแอป */
        .main-title {{
            text-align: center; 
            color: { '#ffffff' if bg_image_base64 else '#0c2340' }; 
            text-shadow: 2px 2px 8px rgba(0,0,0,0.85);
            margin-bottom: 0;
            font-weight: bold;
        }}
        .main-subtitle {{
            text-align: center; 
            color: { '#f0f0f0' if bg_image_base64 else '#666666' }; 
            text-shadow: 1px 1px 5px rgba(0,0,0,0.7);
            font-size: 0.95rem; 
            margin-bottom: 20px;
        }}
        
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }}
    </style>
""", unsafe_allow_html=True)

# ส่วนหัวหลักของแอปพลิเคชัน
st.markdown('<h2 class="main-title">👮‍♂️ ระบบรายงาน Line Group</h2>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">งานสอบสวน สภ.ไม้แก่น (ระบบฐานข้อมูล NoSQL Cloud)</p>', unsafe_allow_html=True)

# --- 3. ฟังก์ชัน โหลด/บันทึก และ จัดลำดับยศตำรวจ ---
def get_rank_priority(rank_str):
    ranks_priority = {
        "พล.ต.อ.": 1, "พล.ต.ท.": 2, "พล.ต.ต.": 3,
        "พ.ต.อ.": 4, "พ.ต.ท.": 5, "พ.ต.ต.": 6,
        "ร.ต.อ.": 7, "ร.ต.ท.": 8, "ร.ต.ต.": 9,
        "ด.ต.": 10, "จ.ส.ต.": 11, "ส.ต.อ.": 12, "ส.ต.ท.": 13, "ส.ต.ต.": 14
    }
    return ranks_priority.get(rank_str.strip(), 99)

def load_personnel():
    docs = db.collection("personnel").stream()
    personnel = []
    for doc in docs:
        p_data = doc.to_dict()
        p_data["id"] = doc.id
        personnel.append(p_data)
        
    if not personnel:
        default_p =
