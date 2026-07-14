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

# --- ปุ่มปรับโหมดสีอัจฉริยะ (วางไว้ด้านบนสุดเพื่อให้เลือกตามใจชอบ) ---
# โดยจะสร้างตัวเลือกให้เหมาะสมกับพื้นหลังของระบบ
color_mode = st.radio(
    "🎨 ปรับโหมดสีตัวอักษรและกล่องข้อมูล (เลือกให้ตัดกับรูปภาพพื้นหลังของคุณ)",
    ["โหมดกล่องขาว ตัวอักษรเข้ม (สำหรับรูปพื้นหลังสีมืด)", "โหมดกล่องดำ ตัวอักษรขาว (สำหรับรูปพื้นหลังสีสว่าง)"],
    horizontal=True
)

# ตั้งค่าตัวแปร CSS ตามโหมดที่ผู้ใช้เลือก
if "สำหรับรูปพื้นหลังสีมืด" in color_mode:
    # โหมดกล่องขาว ตัวอักษรสีน้ำเงินเข้ม
    card_bg = "rgba(255, 255, 255, 0.96)"
    text_color = "#0c2340"
    label_color = "#0c2340"
    border_color = "rgba(12, 35, 64, 0.25)"
    shadow_color = "rgba(0, 0, 0, 0.2)"
    input_bg = "#ffffff"
    input_text = "#111111"
else:
    # โหมดกล่องดำ ตัวอักษรสีขาวสว่าง
    card_bg = "rgba(15, 23, 42, 0.95)"
    text_color = "#ffffff"
    label_color = "#38bdf8" # สีฟ้าสว่างเพื่อให้เห็นหัวข้อชัดเจน
    border_color = "rgba(56, 189, 248, 0.4)"
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
            background-color: rgba(12, 35, 64, 0.3); 
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
            color: #111111 !important; /* บังคับตัวอักษรรายงานที่สลับไป Line ให้เป็นสีดำเข้มเสมอ */
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
        default_p = [
            {"rank": "พ.ต.ท.", "name": "ปฐมพงศ์ ศีรษะพล", "position": "สว.(สอบสวน) สภ.ไม้แก่น"},
            {"rank": "ร.ต.อ.", "name": "สมเจต ทองแผ่น", "position": "รอง สว.(สอบสวน) สภ.นาประดู่ ปรก.สภ.ไม้แก่น"},
            {"rank": "ร.ต.อ.", "name": "ตุลกร สุริยวงศ์", "position": "รอง สว.(สอบสวน) สภ.ไม้แก่น"},
            {"rank": "ด.ต.", "name": "ประสาน ปรงแก้ว", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
            {"rank": "จ.ส.ต.", "name": "อาลีฟ มะเก๊ะ", "position": "ผบ.หมู่(ป.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
            {"rank": "ส.ต.ท.", "name": "ธนกฤต คงบุญช่วย", "position": "ผบ.หมู่(ผช.พงส.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
            {"rank": "ส.ต.ต.", "name": "สุริยา บุญชูดวง", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"}
        ]
        for p in default_p:
            db.collection("personnel").add(p)
        st.rerun()
        
    personnel.sort(key=lambda x: get_rank_priority(x["rank"]))
    return personnel

def load_tasks():
    docs = db.collection("tasks").stream()
    tasks = []
    for doc in docs:
        t_data = doc.to_dict()
        t_data["id"] = doc.id
        tasks.append(t_data)
        
    if not tasks:
        default_tasks = [
            "ได้นำตัวผู้ต้องหาคดียาเสพติด ส่งตัวฝากขังต่อศาลจังหวัดปัตตานี",
            "ได้รับมอบหมายจากพนักงานสอบสวน ยื่นคำร้องฝากขังต่อ ครั้งที่ 2,3 และ 4 ต่อศาลจังหวัดปัตตานี",
            "ได้ส่งสำนวนการสอบสวนคดีอยาเสพติด จำนวน 1 เรื่อง ที่พนักงานสอบสวนทำการสอบสวนเสร็จสิ้นแล้ว ไปยังพนักงานอัยการจังหวัดปัตตานี",
            "ได้นำยาเสพติดของกลางในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจพิสูจน์ยาเสพติด พิสูจน์หลักฐานจังหวัดปัตตานี"
        ]
        for t in default_tasks:
            db.collection("tasks").add({"task_detail": t})
        st.rerun()
    return tasks

personnel_list = load_personnel()
tasks_data = load_tasks()

officer_options = {}
for p in personnel_list:
    key_name = f"{p['rank']}{p['name']} ({p['position']})"
    officer_options[key_name] = p

tasks_list = [t["task_detail"] for t in tasks_data]

# ==================== แบ่งหน้าจอออกเป็น 3 คอลัมน์ใหญ่ (PC) ====================
main_col1, main_col2, main_col3 = st.columns([1, 1, 1.1])

# ----------------- คอลัมน์ที่ 1: วันที่เวลา / เจ้าหน้าที่ -----------------
with main_col1:
    with st.container(border=True):
        st.markdown("### ⏱️ วันที่และเวลาภารกิจ")
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            date_input = st.date_input("📅 เลือกวันที่", datetime.now())
            months_th = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
            year_th = str(date_input.year + 543)[2:]
            date_str = f"{date_input.day} {months_th[date_input.month-1]}{year_th}"
        with sub_col2:
            current_time_str = datetime.now().strftime("%H.%M")
            time_str = st.text_input("⏰ กรอกเวลา (น.)", value=current_time_str)

        st.markdown("### 👤 เจ้าหน้าที่ผู้ปฏิบัติงาน")
        main_officer_select = st.selectbox("👮‍♂️ เลือกผู้ปฏิบัติหลัก (คนแรก)", list(officer_options.keys()))
        main_officer = officer_options[main_officer_select]

        with_team = st.checkbox("➕ มีผู้ปฏิบัติร่วม (พร้อมพวก/พร้อมด้วย)", value=False)
        team_member_lines = ""
        has_team_names = False

        if with_team:
            num_team = st.number_input("จำนวนผู้ปฏิบัติร่วม (คน)", min_value=1, max_value=10, value=1, step=1)
            for i in range(int(num_team)):
                team_select = st.selectbox(f"👤 เลือกผู้ปฏิบัติร่วมคนที่ {i+1}", ["-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --"] + list(officer_options.keys()), key=f"team_{i}")
                if team_select != "-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --":
                    member = officer_options[team_select]
                    team_member_lines += f"\n{member['rank']}{member['name']}\n{member['position']}"
                    has_team_names = True

        suffix = ""
        if with_team:
            suffix = " พร้อมด้วย" if has_team_names else " พร้อมพวก"

# ----------------- คอลัมน์ที่ 2: รายละเอียดภารกิจ -----------------
with main_col2:
    with st.container(border=True):
        st.markdown("### 📝 รายละเอียดภารกิจ")
        num_tasks = st.number_input("📌 จำนวนภารกิจที่ต้องการรายงาน (เรื่อง)", min_value=1, max_value=5, value=1, step=1)

        all_task_details = []

        for idx in range(int(num_tasks)):
            st.markdown(f"**📍 ภารกิจเรื่องที่ {idx+1}**")
            selected_task = st.selectbox(
                f"เลือกหรือค้นหาข้อความภารกิจที่ {idx+1}", 
                [""] + tasks_list, 
                key=f"select_{idx}"
            )
            if selected_task:
                processed_task = selected_task
                if processed_task.startswith("ได้นำ"):
                    processed_task = processed_task.replace("ได้นำ", "นำ", 1)
                all_task_details.append(processed_task)

        with st.expander("➕ เพิ่มภารกิจใหม่บันทึกเข้าฐานข้อมูล"):
            new_detail = st.text_area("พิมพ์รายละเอียดภารกิจใหม่ที่นี่")
            if st.button("💾 บันทึกภารกิจถาวร"):
                if new_detail:
                    if new_detail not in tasks_list:
                        db.collection("tasks").add({"task_detail": new_detail})
                        st.toast("🎉 เพิ่มภารกิจใหม่สำเร็จ!", icon="💾")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ มีภารกิจนี้ในคลังแล้ว")
                else:
                    st.warning("⚠️ กรุณากรอกข้อความ")

        final_tasks_text = ""
        valid_tasks = [task for task in all_task_details if task]

        if len(valid_tasks) == 1:
            final_tasks_text = valid_tasks[0]
        elif len(valid_tasks) > 1:
            final_tasks_text = "\n".join([f"- {task}" for task in valid_tasks])

# ----------------- คอลัมน์ที่ 3: ข้อความรายงานสำหรับส่ง -----------------
with main_col3:
    with st.container(border=True):
        st.markdown("### 📋 ข้อความรายงานสำหรับส่ง Line")

        report_text = f"""สภ.ไม้แก่น 
งานสอบสวน
เรียน ผู้บังคับบัญชา
เมื่อ {date_str} เวลาประมาณ {time_str} น.
{main_officer['rank']}{main_officer['name']}
{main_officer['position']}{suffix}{team_member_lines}
{final_tasks_text}
   จึงเรียนมาเพื่อโปรดทราบ"""

        st.code(report_text, language="text")
        st.success("👆 แตะปุ่มไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนเพื่อ Copy")

# --- แผงควบคุมหลังบ้านและจัดการภาพพื้นหลัง ---
st.markdown("---")
with st.expander("⚙️ ตั้งค่าระบบหลังบ้าน (รายชื่อ / ภารกิจ / เปลี่ยนพื้นหลัง)"):
    # รายชื่อตำรวจ
    st.markdown("#### 👤 1. จัดการรายชื่อเจ้าหน้าที่")
    with st.form("new_officer_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n_rank = c1.text_input("ยศ (เช่น พ.ต.ท., ร.ต.อ.)")
        n_name = c2.text_input("ชื่อ-นามสกุล")
        n_pos = st.text_input("ตำแหน่ง")
        if st.form_submit_button("💾 บันทึกรายชื่อ") and n_rank and n_name and n_pos:
            db.collection("personnel").add({"rank": n_rank, "name": n_name, "position": n_pos})
            st.rerun()

    for person in personnel_list:
        p_col1, p_col2 = st.columns([8, 2])
        p_col1.write(f"**{person['rank']}{person['name']}** - {person['position']}")
        if p_col2.button("🗑️ ลบ", key=f"del_p_{person['id']}"):
            db.collection("personnel").document(person['id']).delete()
            st.rerun()

    # จัดการภาพพื้นหลัง
    st.markdown("---")
    st.markdown("#### 🖼️ 2. ตั้งค่าภาพพื้นหลังเว็บ")
    uploaded_bg = st.file_uploader("อัปโหลดภาพใหม่เพื่อเปลี่ยนพื้นหลัง", type=["jpg", "jpeg", "png"])
    if uploaded_bg:
        new_bg_base64 = process_and_get_base64(uploaded_bg)
        save_background_image(new_bg_base64)
        st.rerun()
    if bg_image_base64 is not None:
        if st.button("❌ ลบภาพพื้นหลัง กลับไปใช้สีเทาปกติ"):
            delete_background_image()
            st.rerun()
