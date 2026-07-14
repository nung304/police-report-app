import streamlit as st
from datetime import datetime
import google.auth
from google.cloud import firestore
from google.oauth2 import service_account
import time
import base64

# ตั้งค่าหน้าจอให้เป็นแบบ "กว้างพิเศษ (Wide)" เพื่อให้แสดงผล 3 คอลัมน์บน PC ได้สวยงามพอดี
st.set_page_config(
    page_title="รายงานสอบสวน สภ.ไม้แก่น", 
    page_icon="👮‍♂️", 
    layout="wide",  # ปรับเป็น wide เพื่อให้เต็มหน้าจอ PC
    initial_sidebar_state="collapsed"
)

# --- ฟังก์ชันแปลงไฟล์ภาพที่อัปโหลดเป็น Base64 เพื่อใช้ใน CSS ---
def get_image_base64(image_file):
    encoded = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded}"

# --- ส่วนควบคุม CSS พื้นหลัง ---
bg_css = ""
# เพิ่มกล่องสำหรับอัปโหลดภาพพื้นหลังไว้ใน Session State
if "bg_image_base64" not in st.session_state:
    st.session_state["bg_image_base64"] = None

# ปรับแต่ง CSS หลัก และตั้งค่าพื้นหลังหากมีการอัปโหลดรูปภาพ
if st.session_state["bg_image_base64"]:
    bg_css = f"""
    <style>
        .stApp {{
            background-image: url("{st.session_state["bg_image_base64"]}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* เพิ่มกล่องโปร่งแสงทับพื้นหลังเพื่อให้ตัวหนังสืออ่านง่ายขึ้นบนทุกพื้นหลัง */
        .block-container {{
            background-color: rgba(255, 255, 255, 0.92);
            border-radius: 15px;
            padding: 2rem !important;
            margin-top: 1.5rem !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
    </style>
    """

st.markdown(bg_css + """
    <style>
        /* สไตล์ปุ่มกดหลัก */
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 3em;
            background-color: #0c2340;
            color: white;
            font-weight: bold;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #1d3557;
            color: #f1faee;
        }
        /* สไตล์กรอบกล่องสำหรับข้อมูลรายงาน */
        div[data-testid="stCodeBlock"] {
            border-radius: 12px;
            border: 2px solid #0c2340;
            background-color: #f8f9fa;
        }
        /* หัวข้อย่อยให้มีระยะห่างที่พอดี */
        h3 {
            margin-top: 1rem !important;
            margin-bottom: 0.8rem !important;
            font-size: 1.25rem !important;
            color: #0c2340;
            border-left: 5px solid #0c2340;
            padding-left: 10px;
        }
        /* ลดช่องว่างส่วนหัวเว็บบนมือถือและ PC */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# ส่วนหัวหลักของแอปพลิเคชัน
st.markdown("<h2 style='text-align: center; color: #0c2340; margin-bottom: 0;'>👮‍♂️ ระบบรายงาน Line Group</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 0.95rem; margin-bottom: 20px;'>งานสอบสวน สภ.ไม้แก่น (ระบบฐานข้อมูล NoSQL Cloud)</p>", unsafe_allow_html=True)

# --- 1. เชื่อมต่อฐานข้อมูล NoSQL (Firebase Firestore) ---
@st.cache_resource
def get_firestore_client():
    credentials_info = st.secrets["firebase"]
    creds = service_account.Credentials.from_service_account_info(credentials_info)
    db = firestore.Client(credentials=creds, project=credentials_info["project_id"])
    return db

db = get_firestore_client()

# --- 2. ฟังก์ชัน โหลด/บันทึก และ จัดลำดับยศตำรวจ ---
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


# ==================== แบ่งหน้าจอออกเป็น 3 คอลัมน์ใหญ่ ====================
main_col1, main_col2, main_col3 = st.columns([1, 1, 1.1])

# ----------------- คอลัมน์ที่ 1: วันที่เวลา / เจ้าหน้าที่ / เปลี่ยนพื้นหลัง -----------------
with main_col1:
    # ฟีเจอร์อัปโหลดเปลี่ยนภาพพื้นหลัง
    st.markdown("### 🖼️ ภาพพื้นหลังระบบ")
    uploaded_bg = st.file_uploader("อัปโหลดภาพเพื่อตั้งเป็นพื้นหลังเว็บ", type=["jpg", "jpeg", "png"], key="bg_uploader")
    if uploaded_bg:
        st.session_state["bg_image_base64"] = get_image_base64(uploaded_bg)
        st.rerun()
    elif st.session_state["bg_image_base64"] is not None:
        if st.button("❌ ลบภาพพื้นหลัง (ใช้พื้นหลังปกติ)"):
            st.session_state["bg_image_base64"] = None
            st.rerun()

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
    st.success("👆 แตะปุ่มไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนของรายงานด้านบนเพื่อ Copy ได้ทันที!")


# --- แผงควบคุมและแก้ไขจัดการฐานข้อมูล NoSQL ด้านล่างสุด ---
st.markdown("---")
with st.expander("⚙️ ตั้งค่าระบบหลังบ้าน (เพิ่ม / แก้ไข / ลบ รายชื่อและภารกิจบนคลาวด์)"):
    
    # จัดการรายชื่อตำรวจ
    st.markdown("#### 👤 1. จัดการรายชื่อเจ้าหน้าที่")
    
    with st.form("new_officer_form", clear_on_submit=True):
        st.markdown("**➕ เพิ่มรายชื่อใหม่ (ระบบจะนำไปจัดเรียงลำดับตามยศให้อัตโนมัติ)**")
        c1, c2 = st.columns(2)
        n_rank = c1.text_input("ยศ (เช่น พ.ต.ท., ร.ต.อ., ด.ต.)")
        n_name = c2.text_input("ชื่อ-นามสกุล")
        n_pos = st.text_input("ตำแหน่ง")
        btn_add_p = st.form_submit_button("💾 บันทึกรายชื่อ")
        if btn_add_p and n_rank and n_name and n_pos:
            db.collection("personnel").add({"rank": n_rank, "name": n_name, "position": n_pos})
            st.toast("🎉 เพิ่มรายชื่อเจ้าหน้าที่และเรียงลำดับยศสำเร็จ!", icon="👤")
            time.sleep(1)
            st.rerun()

    st.markdown("**📋 รายชื่อเจ้าหน้าที่ทั้งหมดในระบบ (เรียงตามลำดับอาวุโสยศ)**")
    for p_idx, person in enumerate(personnel_list):
        p_col1, p_col2, p_col3 = st.columns([7, 1.5, 1.5])
        p_col1.write(f"**{person['rank']}{person['name']}**\n{person['position']}")
        
        if p_col2.button("✏️", key=f"edit_p_{person['id']}"):
            st.session_state[f"editing_p_{person['id']}"] = True
            
        if p_col3.button("🗑️", key=f"del_p_{person['id']}"):
            db.collection("personnel").document(person['id']).delete()
            st.toast("🗑️ ลบรายชื่อเจ้าหน้าที่เรียบร้อยแล้ว!", icon="✅")
            time.sleep(1)
            st.rerun()
            
        if st.session_state.get(f"editing_p_{person['id']}", False):
            with st.container():
                e_rank = st.text_input("แก้ไขยศ", value=person['rank'], key=f"er_{person['id']}")
                e_name = st.text_input("แก้ไขชื่อ-สกุล", value=person['name'], key=f"en_{person['id']}")
                e_pos = st.text_input("แก้ไขตำแหน่ง", value=person['position'], key=f"ep_{person['id']}")
                if st.button("💾 อัปเดตข้อมูล", key=f"save_p_{person['id']}"):
                    db.collection("personnel").document(person['id']).update({
                        "rank": e_rank, "name": e_name, "position": e_pos
                    })
                    st.session_state[f"editing_p_{person['id']}"] = False
                    st.toast("📝 อัปเดตข้อมูลและจัดเรียงลำดับยศเรียบร้อย!", icon="🎉")
                    time.sleep(1)
                    st.rerun()

    # จัดการข้อความภารกิจ
    st.markdown("---")
    st.markdown("#### 📝 2. จัดการคลังข้อความภารกิจ")
    
    for t_idx, t_obj in enumerate(tasks_data):
        t_col1, t_col2, t_col3 = st.columns([7, 1.5, 1.5])
        t_col1.write(f"**{t_idx+1}.** {t_obj['task_detail']}")
        
        if t_col2.button("✏️", key=f"edit_t_{t_obj['id']}"):
            st.session_state[f"editing_t_{t_obj['id']}"] = True
            
        if t_col3.button("🗑️", key=f"del_t_{t_obj['id']}"):
            db.collection("tasks").document(t_obj['id']).delete()
            st.toast("🗑️ ลบข้อความภารกิจออกจากระบบแล้ว!", icon="✅")
            time.sleep(1)
            st.rerun()
            
        if st.session_state.get(f"editing_t_{t_obj['id']}", False):
            with st.container():
                e_task = st.text_area("แก้ไขรายละเอียดภารกิจ", value=t_obj['task_detail'], key=f"et_text_{t_obj['id']}")
                if st.button("💾 อัปเดตภารกิจ", key=f"save_t_{t_obj['id']}"):
                    db.collection("tasks").document(t_obj['id']).update({"task_detail": e_task})
                    st.session_state[f"editing_t_{t_obj['id']}"] = False
                    st.toast("📝 แก้ไขข้อความภารกิจสำเร็จ!", icon="🎉")
                    time.sleep(1)
                    st.rerun()
