import streamlit as st
from datetime import datetime
import google.auth
from google.cloud import firestore
from google.oauth2 import service_account
import time

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(
    page_title="รายงานสอบสวน สภ.ไม้แก่น", 
    page_icon="👮‍♂️", 
    layout="wide",  
    initial_sidebar_state="collapsed"
)

# --- 2. ส่ง Meta Tags ซ่อนตัวสำหรับ LINE ---
st.html(
    """
    <style>
        .hidden-metadata { display: none !important; }
    </style>
    <div class="hidden-metadata">
        <p>ระบบรายงานสรุปผลการปฏิบัติงาน สภ.ไม้แก่น</p>
        <span data-og-title="ระบบรายงานสรุปผลการปฏิบัติงาน สภ.ไม้แก่น"></span>
        <span data-og-description="โปรแกรมช่วยงานสอบสวน สภ.ไม้แก่น สำหรับคัดลอกข้อความรายงานลงกลุ่ม Line"></span>
        <span data-og-image="https://github.com/nung304/police-report-app/blob/main/75858736-e9f9-4ae3-ad7b-2cc685c5f76e.png?raw=true"></span>
    </div>
    <script>
        document.title = "ระบบรายงานสรุปผลการปฏิบัติงาน สภ.ไม้แก่น";
        
        const updateOrCreateMeta = (property, content) => {
            let meta = document.querySelector(`meta[property="${property}"]`);
            if (!meta) {
                meta = document.createElement('meta');
                meta.setAttribute('property', property);
                document.head.appendChild(meta);
            }
            meta.content = content;
        };

        updateOrCreateMeta("og:title", "ระบบรายงานสรุปผลการปฏิบัติงาน สภ.ไม้แก่น");
        updateOrCreateMeta("og:description", "โปรแกรมช่วยงานสอบสวน สภ.ไม้แก่น สำหรับคัดลอกข้อความรายงานลงกลุ่ม Line");
        updateOrCreateMeta("og:image", "https://github.com/nung304/police-report-app/blob/main/75858736-e9f9-4ae3-ad7b-2cc685c5f76e.png?raw=true");
        updateOrCreateMeta("og:url", "https://police-report.streamlit.app/");
        updateOrCreateMeta("og:type", "website");
    </script>
    """
)

# --- 3. เชื่อมต่อฐานข้อมูล NoSQL (Firebase Firestore) ---
@st.cache_resource
def get_firestore_client():
    credentials_info = st.secrets["firebase"]
    creds = service_account.Credentials.from_service_account_info(credentials_info)
    db = firestore.Client(credentials=creds, project=credentials_info["project_id"])
    return db

db = get_firestore_client()

# --- ส่วนควบคุม CSS สำหรับจัดแต่งกรอบคอลัมน์และหน้าตาเว็บ ---
st.markdown("""
    <style>
        .stColumn > div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #ffffff !important;
            border-radius: 12px !important;
            border: 1px solid #e0e0e0 !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
            padding: 24px !important;
            margin-bottom: 20px !important;
        }
        
        @media (prefers-color-scheme: dark) {
            .stColumn > div[data-testid="stVerticalBlockBorderWrapper"] {
                background-color: #1e293b !important;
                border: 1px solid #334155 !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
            }
        }
        
        div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0px !important;
        }
        
        h3 {
            color: #0c2340 !important;
            border-left: 6px solid #0c2340;
            padding-left: 12px;
            font-weight: bold !important;
            margin-top: 0px !important;
            margin-bottom: 20px !important;
        }
        @media (prefers-color-scheme: dark) {
            h3 {
                color: #38bdf8 !important;
                border-left: 6px solid #38bdf8;
            }
        }
        
        div[data-testid="stCodeBlock"] {
            border: 2px solid #0c2340;
            background-color: #f8fafc !important;
            border-radius: 10px !important;
        }
        @media (prefers-color-scheme: dark) {
            div[data-testid="stCodeBlock"] {
                border: 2px solid #38bdf8;
                background-color: #0f172a !important;
            }
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            height: 3em;
            background-color: #0c2340 !important;
            color: white !important;
            font-weight: bold;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #1d3557 !important;
        }
        @media (prefers-color-scheme: dark) {
            .stButton>button {
                background-color: #38bdf8 !important;
                color: #0f172a !important;
            }
            .stButton>button:hover {
                background-color: #7dd3fc !important;
            }
        }
        
        /* สไตล์พิเศษสำหรับปุ่มบันทึกย่อยในแอป */
        .inline-save-btn button {
            background-color: #28a745 !important;
            height: 2.5em !important;
            margin-top: 5px !important;
        }
        .inline-save-btn button:hover {
            background-color: #218838 !important;
        }
        @media (prefers-color-scheme: dark) {
            .inline-save-btn button {
                background-color: #34d399 !important;
                color: #0f172a !important;
            }
            .inline-save-btn button:hover {
                background-color: #059669 !important;
            }
        }
        
        /* สไตล์พิเศษสำหรับปุ่มเคลียร์ข้อความ */
        .inline-clear-btn button {
            background-color: #dc3545 !important;
            height: 2.5em !important;
            margin-top: 5px !important;
            color: white !important;
        }
        .inline-clear-btn button:hover {
            background-color: #c82333 !important;
        }

        .main-title {
            text-align: center; 
            color: #0c2340; 
            font-weight: bold;
            margin-bottom: 0;
        }
        .main-subtitle {
            text-align: center; 
            color: #666666; 
            font-size: 0.95rem; 
            margin-bottom: 25px;
        }
        @media (prefers-color-scheme: dark) {
            .main-title { color: #ffffff; }
            .main-subtitle { color: #94a3b8; }
        }
    </style>
""", unsafe_allow_html=True)

# ส่วนหัวหลักของแอปพลิเคชัน
st.markdown('<h2 class="main-title">👮‍♂️ ระบบรายงาน Line Group</h2>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">งานสอบสวน สภ.ไม้แก่น (ระบบฐานข้อมูล NoSQL Cloud)</p>', unsafe_allow_html=True)

# --- 4. ฟังก์ชัน โหลด/บันทึก และ จัดลำดับยศตำรวจ ---
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
            "ได้ส่งสำนวนการสอบสวนคดียาเสพติด จำนวน 1 เรื่อง ที่พนักงานสอบสวนทำการสอบสวนเสร็จสิ้นแล้ว ไปยังพนักงานอัยการจังหวัดปัตตานี",
            "ได้นำยาเสพติดของจัดการในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจพิสูจน์ยาเสพติด พิสูจน์หลักฐานจังหวัดปัตตานี"
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

tasks_list = [""] + [t["task_detail"] for t in tasks_data]

# ส่วนกลาง: ตั้งค่าวันที่สำหรับการทำงาน
date_input = st.date_input("เลือกวันที่", datetime.now(), key="global_date_input")
months_th = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
year_th = str(date_input.year + 543)[2:]
date_str = f"{date_input.day} {months_th[date_input.month-1]}{year_th}"

st.markdown("---")

# ==================== แบ่งหน้าการทำงานด้วยระบบ Tabs ====================
tab1, tab2 = st.tabs(["📝 1. รายงานสรุปผลการปฏิบัติประจำวัน (แยกคน/เวลา/ภารกิจ)", "👮‍♂️ 2. รายงานรูปแบบเดิม (เดี่ยว/พร้อมพวก)"])

# ----------------- TAB 1: รายงานสรุปผลการปฏิบัติประจำวัน -----------------
with tab1:
    t2_col1, t2_col2 = st.columns([1.2, 1])
    
    with t2_col1:
        with st.container(border=True):
            st.markdown("### 📝 สรุปรายการภารกิจวันนี้")
            
            no_cases = st.checkbox("❌ วันนี้ไม่มีประชาชนมาแจ้งความหรือลงบันทึกประจำวัน (เหตุการณ์ปกติ)", value=False, key="t2_no_cases")
            
            report_items_t2 = []
            
            if not no_cases:
                num_tasks_t2 = st.number_input("จำนวนภารกิจที่ต้องการสรุป (เรื่อง)", min_value=1, max_value=10, value=1, step=1, key="t2_num_tasks")
                
                for i in range(int(num_tasks_t2)):
                    st.markdown(f"**📍 รายการภารกิจที่ {i+1}**")
                    
                    selected_officer_t2 = st.selectbox(f"👮‍♂️ ผู้ปฏิบัติหลัก คนที่ {i+1}", list(officer_options.keys()), key=f"t2_off_{i}")
                    officer_t2 = officer_options[selected_officer_t2]
                    
                    with_team_t2 = st.checkbox("➕ มีผู้ปฏิบัติร่วมในภารกิจนี้", value=False, key=f"t2_with_team_{i}")
                    team_member_lines_t2 = ""
                    has_team_names_t2 = False
                    
                    if with_team_t2:
                        num_team_t2 = st.number_input(f"จำนวนผู้ปฏิบัติร่วม (ภารกิจที่ {i+1})", min_value=1, max_value=10, value=1, step=1, key="t2_num_team_idx_" + str(i))
                        for j in range(int(num_team_t2)):
                            team_select_t2 = st.selectbox(f"👤 เลือกผู้ปฏิบัติร่วมคนที่ {j+1} (ภารกิจที่ {i+1})", ["-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --"] + list(officer_options.keys()), key=f"t2_team_member_{i}_{j}")
                            if team_select_t2 != "-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --":
                                member_t2 = officer_options[team_select_t2]
                                team_member_lines_t2 += f"\n{member_t2['rank']}{member_t2['name']}\n{member_t2['position']}"
                                has_team_names_t2 = True
                    
                    suffix_t2 = ""
                    if with_team_t2:
                        suffix_t2 = " พร้อมด้วย" if has_team_names_t2 else " พร้อมพวก"
                    
                    time_input_t2 = st.text_input(f"⏰ เวลาภารกิจที่ {i+1} (น.)", value="08.30", key=f"t2_time_{i}")
                    
                    selectbox_options = ["-- เลือกภารกิจจากคลัง (หรือเลือกพิมพ์อิสระด้านล่าง) --", "-- พิมพ์ข้อความเองอิสระ --"] + [t for t in tasks_list if t]
                    
                    task_select_t2 = st.selectbox(
                        f"🔍 เลือกคลังข้อความภารกิจ ({i+1})", 
                        selectbox_options, 
                        key=f"t2_select_{i}"
                    )
                    
                    # ตรรกะรองรับการแก้ไขและล้างค่ากล่องข้อความอิสระ (ให้กลายเป็นช่องว่างพร้อมพิมพ์ใหม่)
                    if task_select_t2 == "-- พิมพ์ข้อความเองอิสระ --":
                        custom_key = f"t2_custom_input_val_{i}"
                        if custom_key not in st.session_state:
                            st.session_state[custom_key] = ""
                            
                        # ใช้กลไก value=st.session_state[custom_key] เพื่อบังคับให้เปลี่ยนเป็นช่องว่างได้เมื่อกดปุ่มสั่ง
                        task_detail_t2 = st.text_input(
                            f"✍️ พิมพ์ภารกิจเอง ({i+1})", 
                            value=st.session_state[custom_key],
                            key=f"t2_custom_field_{i}"
                        )
                        st.session_state[custom_key] = task_detail_t2
                        
                        # สร้างปุ่มแบบแถวคู่: บันทึกเข้าคลัง / ล้างข้อความเพื่อพิมพ์ใหม่
                        btn_c1, btn_c2 = st.columns(2)
                        
                        with btn_c1:
                            st.markdown('<div class="inline-save-btn">', unsafe_allow_html=True)
                            if st.button(f"💾 บันทึกภารกิจที่ {i+1} เข้าคลังถาวร", key=f"inline_save_btn_{i}"):
                                current_text = st.session_state[custom_key].strip()
                                if current_text:
                                    if current_text not in tasks_list:
                                        db.collection("tasks").add({"task_detail": current_text})
                                        st.toast("🎉 บันทึกภารกิจเข้าคลังฐานข้อมูลสำเร็จ!", icon="💾")
                                        # ล้างกล่องข้อความอิสระให้เป็นช่องว่างทันที
                                        st.session_state[custom_key] = ""
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.warning("⚠️ มีภารกิจนี้อยู่ในคลังข้อความแล้ว")
                                else:
                                    st.error("❌ กรุณาพิมพ์ข้อความภารกิจก่อนกดบันทึกครับ")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        with btn_c2:
                            st.markdown('<div class="inline-clear-btn">', unsafe_allow_html=True)
                            if st.button(f"🧹 ล้างช่องพิมพ์เป็นช่องว่าง ({i+1})", key=f"inline_clear_btn_{i}"):
                                # บังคับล้างข้อความในกล่องพิมพ์อิสระให้กลายเป็นช่องว่าง "" ทันที
                                st.session_state[custom_key] = ""
                                st.toast("🧹 ล้างข้อความเป็นช่องว่างเรียบร้อย พิมพ์ใหม่ได้เลยครับ!", icon="✅")
                                time.sleep(0.5)
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    elif task_select_t2 == "-- เลือกภารกิจจากคลัง (หรือเลือกพิมพ์อิสระด้านล่าง) --":
                        task_detail_t2 = ""
                    else:
                        task_detail_t2 = task_select_t2
                    
                    if task_detail_t2:
                        item_text = f"{i+1}. เวลา {time_input_t2} น.\n{officer_t2['rank']}{officer_t2['name']}\n{officer_t2['position']}{suffix_t2}{team_member_lines_t2}\n{task_detail_t2}"
                        report_items_t2.append(item_text)
                        
                    st.divider()
            else:
                st.info("ℹ️ เปิดโหมดรายงานกรณีเหตุการณ์ปกติเรียบร้อยแล้ว ตรวจสอบข้อความสรุปทางด้านขวาได้เลยครับ")

    with t2_col2:
        with st.container(border=True):
            st.markdown("### 📋 ข้อความสรุปรวม Line")
            
            if no_cases:
                final_text_t2 = f"สภ.ไม้แก่น \nงานสอบสวน\nเรียนผู้บังคับบัญชา\nรายงานสรุปผลการปฏิบัติประจำวันที่ {date_str}\nไม่มีประชาชนมาแจ้งความหรือลงบันทึกประจำวันแต่อย่างใด\nเหตุการณ์ทั่วไปปกติ\n\nจึงเรียนมาเพื่อโปรดทราบ"
            else:
                joined_items_t2 = "\n".join(report_items_t2)
                final_text_t2 = f"สภ.ไม้แก่น \nงานสอบสวน\nเรียนผู้บังคับบัญชา\nรายงานสรุปผลการปฏิบัติประจำวันที่ {date_str}\n{joined_items_t2}\n\nจึงเรียนมาเพื่อโปรดทราบ"
            
            st.code(final_text_t2, language="text")
            st.success("👆 แตะปุ่มไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนเพื่อ Copy ไปส่งกลุ่ม Line สรุปงานประจำวันได้ทันที")


# ----------------- TAB 2: รายงานรูปแบบเดิม (เดี่ยว/พร้อมพวก) -----------------
with tab2:
    main_col1, main_col2, main_col3 = st.columns([1, 1, 1.1])

    with main_col1:
        with st.container(border=True):
            st.markdown("### ⏱️ เวลาภารกิจ")
            current_time_str = datetime.now().strftime("%H.%M")
            time_str = st.text_input("⏰ กรอกเวลา (น.)", value=current_time_str, key="t1_time_str")

            st.markdown("### 👤 เจ้าหน้าที่ผู้ปฏิบัติงาน")
            main_officer_select = st.selectbox("👮‍♂️ เลือกผู้ปฏิบัติหลัก (คนแรก)", list(officer_options.keys()), key="t1_main_officer")
            main_officer = officer_options[main_officer_select]

            with_team = st.checkbox("➕ มีผู้ปฏิบัติร่วม (พร้อมพวก/พร้อมด้วย)", value=False, key="t1_with_team")
            team_member_lines = ""
            has_team_names = False

            if with_team:
                num_team = st.number_input("จำนวนผู้ปฏิบัติร่วม (คน)", min_value=1, max_value=10, value=1, step=1, key="t1_num_team")
                for i in range(int(num_team)):
                    team_select = st.selectbox(f"👤 เลือกผู้ปฏิบัติร่วมคนที่ {i+1}", ["-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --"] + list(officer_options.keys()), key=f"t1_team_{i}")
                    if team_select != "-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --":
                        member = officer_options[team_select]
                        team_member_lines += f"\n{member['rank']}{member['name']}\n{member['position']}"
                        has_team_names = True

            suffix = ""
            if with_team:
                suffix = " พร้อมด้วย" if has_team_names else " พร้อมพวก"

    with main_col2:
        with st.container(border=True):
            st.markdown("### 📝 รายละเอียดภารกิจ")
            num_tasks = st.number_input("📌 จำนวนภารกิจที่ต้องการรายงาน (เรื่อง)", min_value=1, max_value=5, value=1, step=1, key="t1_num_tasks")

            all_task_details = []
            for idx in range(int(num_tasks)):
                st.markdown(f"**📍 ภารกิจเรื่องที่ {idx+1}**")
                selected_task = st.selectbox(
                    f"เลือกหรือค้นหาข้อความภารกิจที่ {idx+1}", 
                    tasks_list, 
                    key=f"t1_select_{idx}"
                )
                if selected_task:
                    processed_task = selected_task
                    if processed_task.startswith("ได้นำ"):
                        processed_task = processed_task.replace("ได้นำ", "นำ", 1)
                    all_task_details.append(processed_task)

            with st.expander("➕ เพิ่มภารกิจใหม่บันทึกเข้าฐานข้อมูล"):
                new_detail = st.text_area("พิมพ์รายละเอียดภารกิจใหม่ที่นี่", key="t1_new_detail")
                if st.button("💾 บันทึกภารกิจถาวร", key="t1_save_task"):
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


# --- แผงควบคุมหลังบ้าน ---
st.markdown("---")
with st.expander("⚙️ ตั้งค่าระบบหลังบ้าน (จัดการรายชื่อ / จัดการคลังภารกิจ)", expanded=False):
    
    st.markdown("#### 👤 1. จัดการรายชื่อเจ้าหน้าที่")
    with st.form("new_officer_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        n_rank = c1.text_input("ยศ (เช่น พ.ต.ท., ร.ต.о.)")
        n_name = c2.text_input("ชื่อ-นามสกุล")
        n_pos = st.text_input("ตำแหน่ง")
        if st.form_submit_button("💾 บันทึกรายชื่อ") and n_rank and n_name and n_pos:
            db.collection("personnel").add({"rank": n_rank, "name": n_name, "position": n_pos})
            st.rerun()

    for person in personnel_list:
        p_col1, p_col2, p_col3 = st.columns([6, 2, 2])
        p_col1.write(f"**{person['rank']}{person['name']}** - {person['position']}")
        
        if p_col2.button("✏️ แก้ไข", key=f"edit_p_{person['id']}"):
            st.session_state[f"editing_p_{person['id']}"] = True
            
        if p_col3.button("🗑️ ลบ", key=f"del_p_{person['id']}"):
            db.collection("personnel").document(person['id']).delete()
            st.toast("🗑️ ลบรายชื่อเจ้าหน้าที่สำเร็จ!", icon="✅")
            time.sleep(1)
            st.rerun()
            
        if st.session_state.get(f"editing_p_{person['id']}", False):
            with st.container():
                ep_rank = st.text_input("แก้ไขยศ", value=person['rank'], key=f"ep_rank_{person['id']}")
                ep_name = st.text_input("แก้ไขชื่อ-นามสกุล", value=person['name'], key=f"ep_name_{person['id']}")
                ep_pos = st.text_input("แก้ไขตำแหน่ง", value=person['position'], key=f"ep_pos_{person['id']}")
                
                if st.button("💾 อัปเดตรายชื่อ", key=f"save_p_{person['id']}"):
                    db.collection("personnel").document(person['id']).update({
                        "rank": ep_rank,
                        "name": ep_name,
                        "position": ep_pos
                    })
                    st.session_state[f"editing_p_{person['id']}"] = False
                    st.toast("📝 แก้ไขรายชื่อเจ้าหน้าที่สำเร็จ!", icon="🎉")
                    time.sleep(1)
                    st.rerun()

    st.markdown("---")
    st.markdown("#### 📝 2. จัดการคลังข้อความภารกิจ")
    for t_idx, t_obj in enumerate(tasks_data):
        t_col1, t_col2, t_col3 = st.columns([6, 2, 2])
        t_col1.write(f"**{t_idx+1}.** {t_obj['task_detail']}")
        
        if t_col2.button("✏️ แก้ไข", key=f"edit_t_{t_obj['id']}"):
            st.session_state[f"editing_t_{t_obj['id']}"] = True
            
        if t_col3.button("🗑️ ลบ", key=f"del_t_{t_obj['id']}"):
            db.collection("tasks").document(t_obj['id']).delete()
            st.toast("🗑️ ลบข้อความภารกิจสำเร็จ!", icon="✅")
            time.sleep(1)
            st.rerun()
            
        if st.session_state.get(f"editing_t_{t_obj['id']}", False):
            with st.container():
                e_task = st.text_area("แก้ไขรายละเอียดภารกิจ", value=t_obj['task_detail'], key=f"et_text_{t_obj['id']}")
                if st.button("💾 อัปเดตภารกิจ", key=f"save_t_{t_obj['id']}"):
                    db.collection("tasks").document(t_obj['id']).update({"task_detail": e_task})
                    st.session_state[f"editing_t_{t_obj['id']}"] = False
                    st.toast("📝 แก้ไขข้อความสำเร็จ!", icon="🎉")
                    time.sleep(1)
                    st.rerun()
