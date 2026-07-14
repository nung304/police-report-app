import streamlit as st
from datetime import datetime
import google.auth
from google.cloud import firestore
from google.oauth2 import service_account

st.set_page_config(page_title="ระบบสร้างข้อความรายงาน สภ.ไม้แก่น", page_icon="👮‍♂️", layout="centered")
st.title("👮‍♂️ ระบบข้อความรายงาน Line Group")
st.subheader("งานสอบสวน สภ.ไม้แก่น")

# --- 1. เชื่อมต่อฐานข้อมูล NoSQL (Firebase Firestore) ---
@st.cache_resource
def get_firestore_client():
    # ดึงค่าสิทธิ์การเข้าถึงจาก Streamlit Secrets ที่เพิ่งบันทึกไป
    credentials_info = st.secrets["firebase"]
    creds = service_account.Credentials.from_service_account_info(credentials_info)
    db = firestore.Client(credentials=creds, project=credentials_info["project_id"])
    return db

db = get_firestore_client()

# --- 2. ฟังก์ชัน โหลด/บันทึก ข้อมูลจากคลาวด์ ---
def load_personnel():
    # ดึงข้อมูลจากคอลเลกชัน 'personnel'
    docs = db.collection("personnel").stream()
    personnel = []
    for doc in docs:
        p_data = doc.to_dict()
        p_data["id"] = doc.id
        personnel.append(p_data)
        
    # ถ้าฐานข้อมูลว่างเปล่า (การรันครั้งแรก) ให้ใส่ข้อมูลเริ่มต้นเป็นตัวอย่างให้อัตโนมัติ
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
    return personnel

def load_tasks():
    # ดึงข้อมูลจากคอลเลกชัน 'tasks'
    docs = db.collection("tasks").stream()
    tasks = []
    for doc in docs:
        t_data = doc.to_dict()
        t_data["id"] = doc.id
        tasks.append(t_data)
        
    # ถ้าคลังภารกิจว่างเปล่า ให้ใส่ค่าเริ่มต้น
    if not tasks:
        default_tasks = [
            "ได้นำตัวผู้ต้องหาคดียาเสพติด ส่งตัวฝากขังต่อศาลจังหวัดปัตตานี",
            "ได้รับมอบหมายจากพนักงานสอบสวน ยื่นคำร้องฝากขังต่อ ครั้งที่ 2,3 และ 4 ต่อศาลจังหวัดปัตตานี",
            "ได้ส่งสำนวนการสอบสวนคดีอยาเสพติด จำนวน 1 เรื่อง ที่พนักงานสอบสวนทำการสอบสวนเสร็จสิ้นแล้ว ไปยังพนักงานอัยการจังหวัดปัตตานี",
            "ได้นำยาเสพติดของกลางในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจพิสูจน์ยาเสพติด พิสูจน์หลักฐานจังหวัดปัตตานี",
            "ดำเนินการติดตามผลการตรวจพิสูจน์ประวัติการต้องหาคดีอาญาของผู้ขออนุญาต กลุ่มงานทะเบียนประวัติอาชญากร",
            "ได้นำอาวุธปืนของกลางในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจพิสูจน์อาวุธปืน และเครื่องกระสุนปืน ศุ์นย์พิสูจน์หลักฐาน 10",
            "ดำเนินการติดตามผลการตรวจพิสูจน์อาวุธปืน และเครื่องกระสุนปืน กลุ่มงานตรวจพิสูจน์อาวุธปืน และเครื่องกระสุนปืน ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้ เพื่อนำมาประกอบสำนวนการสอบสวน",
            "ได้นำของกลางในคดีอาญา ส่งตรวจพิสูจน์เพื่อหาสารพันธุกรรม DNA กลุ่มงานตรวจชีววิทยาและดีเอ็นเอ ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้",
            "ดำเนินการติดตามผลการตรวจพิสูจน์ของกลางในคดีอาญา กลุ่มงานตรวจชีววิทยาและดีเอ็นเอ (DNA) ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้ เพื่อนำมาประกอบสำนวนการสอบสวน",
            "ได้นำของกลางในคดีอาญา ส่งตรวจพิสูจน์เพื่อตรวจหารอยลายนิ้วมือแฝง กลุ่มงานตรวจลายนิ้วมือแฝง ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้",
            "ดำเนินการติดตามผลการตรวจพิสูจน์รอยลายนิ้วมือแฝง กลุ่มงานตรวจลายนิ้วมือแฝง ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้ เพื่อนำมาประกอบสำนวนการสอบสวน",
            "ได้นำโทรศัพท์มือถือของกลางในคดีอาญา ส่งตรวจพิสูจน์เพื่อตรวจหาความเชื่อมโยงในภาพรวม กลุ่มงานตรวจพิสูจน์อาชญากรรมคอมพิวเตอร์ ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้",
            "ดำเนินการติดตามผลการตรวจพิสูจน์โทรศัพท์มือถือของกลางในคดีอาญา กลุ่มงานตรวจพิสูจน์อาชญากรรมคอมพิวเตอร์ ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้ เพื่อนำมาประกอบสำนวนการสอบสวน",
            "ได้นำของกลางในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจทางเคมี ฟิสิกส์ ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้",
            "ดำเนินการติดตามผลการตรวจพิสูจน์ของกลางในคดีอาญา กลุ่มงานตรวจทางเคมี ฟิสิกส์ ศุ์นย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้ เพื่อนำมาประกอบสำนวนการสอบสวน"
        ]
        for t in default_tasks:
            db.collection("tasks").add({"task_detail": t})
        st.rerun()
    return tasks

personnel_list = load_personnel()
tasks_data = load_tasks()

officer_options = {f"{p['rank']}{p['name']} ({p['position']})": p for p in personnel_list}
tasks_list = [t["task_detail"] for t in tasks_data]

# --- 3. วันที่และเวลาภารกิจ ---
st.markdown("### ⏱️ วันที่และเวลาภารกิจ")
col1, col2 = st.columns(2)
with col1:
    date_input = st.date_input("เลือกวันที่", datetime.now())
    months_th = ["ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.", "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."]
    year_th = str(date_input.year + 543)[2:]
    date_str = f"{date_input.day} {months_th[date_input.month-1]}{year_th}"

with col2:
    current_time_str = datetime.now().strftime("%H.%M")
    time_str = st.text_input("กรอกเวลา (น.)", value=current_time_str)

# --- 4. ผู้ปฏิบัติหน้าที่ ---
st.markdown("### 👤 ผู้ปฏิบัติหน้าที่")
main_officer_select = st.selectbox("เลือกผู้ปฏิบัติหลัก (คนแรก)", list(officer_options.keys()))
main_officer = officer_options[main_officer_select]

with_team = st.checkbox("พร้อมพวก")
team_member_lines = ""
has_team_names = False

if with_team:
    num_team = st.number_input("จำนวนผู้ปฏิบัติร่วม (กี่คน)", min_value=1, max_value=10, value=1, step=1)
    for i in range(int(num_team)):
        team_select = st.selectbox(f"เลือกผู้ปฏิบัติร่วม คนที่ {i+1}", ["-- ไม่ระบุชื่อ (เว้นว่างไว้) --"] + list(officer_options.keys()), key=f"team_{i}")
        if team_select != "-- ไม่ระบุชื่อ (เว้นว่างไว้) --":
            member = officer_options[team_select]
            team_member_lines += f"\n{member['rank']}{member['name']}\n{member['position']}"
            has_team_names = True

suffix = ""
if with_team:
    suffix = " พร้อมด้วย" if has_team_names else " พร้อมพวก"

# --- 5. รายละเอียดภารกิจ ---
st.markdown("### 📝 รายละเอียดภารกิจ")
num_tasks = st.number_input("จำนวนภารกิจที่ต้องการรายงาน (กี่เรื่อง)", min_value=1, max_value=5, value=1, step=1)

all_task_details = []

for idx in range(int(num_tasks)):
    st.markdown(f"**📍 ภารกิจเรื่องที่ {idx+1}**")
    
    selected_task = st.selectbox(
        f"พิมพ์คำค้นหาหรือเลือกข้อความภารกิจที่ {idx+1}", 
        [""] + tasks_list, 
        key=f"select_{idx}"
    )
    if selected_task:
        processed_task = selected_task
        if processed_task.startswith("ได้นำ"):
            processed_task = processed_task.replace("ได้นำ", "นำ", 1)
        all_task_details.append(processed_task)

# พิมพ์ภารกิจใหม่บันทึกลง Firebase NoSQL ถาวร
with st.expander("➕ พิมพ์ภารกิจใหม่นอกเหนือจากในคลังเพื่อบันทึกถาวร"):
    new_detail = st.text_area("พิมพ์รายละเอียดภารกิจฉบับเต็มใหม่ที่นี่")
    if st.button("💾 บันทึกเข้าฐานข้อมูล NoSQL"):
        if new_detail:
            if new_detail not in tasks_list:
                db.collection("tasks").add({"task_detail": new_detail})
                st.success("บันทึกภารกิจใหม่เข้าสู่คลาวด์ NoSQL เรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("❌ มีข้อความภารกิจนี้อยู่ในระบบแล้ว")
        else:
            st.warning("⚠️ กรุณากรอกรายละเอียดภารกิจก่อนกดบันทึก")

# จัดรูปแบบข้อความตามเงื่อนไข (เรื่องเดียวไม่มีขีด / หลายเรื่องขึ้นบรรทัดใหม่พร้อมใส่ - )
final_tasks_text = ""
valid_tasks = [task for task in all_task_details if task]

if len(valid_tasks) == 1:
    final_tasks_text = valid_tasks[0]
elif len(valid_tasks) > 1:
    final_tasks_text = "\n".join([f"- {task}" for task in valid_tasks])

# --- 6. ประมวลผลและสร้างข้อความรายงาน (Output) ---
st.markdown("---")
st.markdown("### 📋 ข้อความรายงานที่พร้อมส่ง (Output)")

report_text = f"""สภ.ไม้แก่น 
งานสอบสวน
เรียน ผู้บังคับบัญชา
เมื่อ {date_str} เวลาประมาณ {time_str} น.
{main_officer['rank']}{main_officer['name']}
{main_officer['position']}{suffix}{team_member_lines}
{final_tasks_text}
   จึงเรียนมาเพื่อโปรดทราบ"""

st.code(report_text, language="text")
st.info("💡 ข้อมูลจะถูกดึงและจัดเก็บผ่าน Firebase Firestore อัตโนมัติ!")


# --- 7. แผงควบคุมและแก้ไขจัดการฐานข้อมูล NoSQL ---
st.markdown("---")
with st.expander("⚙️ เมนูจัดการข้อมูลอย่างละเอียด (เพิ่ม / แก้ไข / ลบ บนคลาวด์ NoSQL)"):
    
    # ==================== ส่วนที่ 1: จัดการรายชื่อตำรวจ ====================
    st.markdown("### 👤 1. จัดการรายชื่อเจ้าหน้าที่")
    
    with st.form("new_officer_form", clear_on_submit=True):
        st.markdown("**➕ เพิ่มรายชื่อใหม่ลงระบบถาวร**")
        c1, c2, c3 = st.columns([1, 2, 3])
        n_rank = c1.text_input("ยศ")
        n_name = c2.text_input("ชื่อ-นามสกุล")
        n_pos = c3.text_input("ตำแหน่ง")
        btn_add_p = st.form_submit_button("💾 บันทึกรายชื่อใหม่")
        if btn_add_p and n_rank and n_name and n_pos:
            db.collection("personnel").add({"rank": n_rank, "name": n_name, "position": n_pos})
            st.success("บันทึกรายชื่อสำเร็จ!")
            st.rerun()

    st.markdown("**📋 รายชื่อทั้งหมดในระบบปัจจุบัน**")
    for p_idx, person in enumerate(personnel_list):
        p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns([1, 2, 4, 1, 1])
        p_col1.write(person['rank'])
        p_col2.write(person['name'])
        p_col3.write(person['position'])
        
        if p_col4.button("✏️", key=f"edit_p_{person['id']}"):
            st.session_state[f"editing_p_{person['id']}"] = True
            
        if p_col5.button("🗑️", key=f"del_p_{person['id']}"):
            db.collection("personnel").document(person['id']).delete()
            st.success("ลบรายชื่อเรียบร้อย!")
            st.rerun()
            
        if st.session_state.get(f"editing_p_{person['id']}", False):
            with st.container():
                st.markdown(f"**🛠️ กำลังแก้ไขข้อมูลของ: {person['rank']}{person['name']}**")
                e_rank = st.text_input("แก้ไขยศ", value=person['rank'], key=f"er_{person['id']}")
                e_name = st.text_input("แก้ไขชื่อ-สกุล", value=person['name'], key=f"en_{person['id']}")
                e_pos = st.text_input("แก้ไขตำแหน่ง", value=person['position'], key=f"ep_{person['id']}")
                if st.button("💾 บันทึกการแก้ไข", key=f"save_p_{person['id']}"):
                    db.collection("personnel").document(person['id']).update({
                        "rank": e_rank, "name": e_name, "position": e_pos
                    })
                    st.session_state[f"editing_p_{person['id']}"] = False
                    st.success("อัปเดตข้อมูลสำเร็จ!")
                    st.rerun()

    # ==================== ส่วนที่ 2: จัดการข้อความภารกิจ ====================
    st.markdown("---")
    st.markdown("### 📝 2. จัดการคลังข้อความภารกิจ")
    
    st.markdown("**📋 รายการภารกิจทั้งหมดในระบบ**")
    for t_idx, t_obj in enumerate(tasks_data):
        t_col1, t_col2, t_col3 = st.columns([7, 1, 1])
        t_col1.write(f"{t_idx+1}. {t_obj['task_detail']}")
        
        if t_col2.button("✏️", key=f"edit_t_{t_obj['id']}"):
            st.session_state[f"editing_t_{t_obj['id']}"] = True
            
        if t_col3.button("🗑️", key=f"del_t_{t_obj['id']}"):
            db.collection("tasks").document(t_obj['id']).delete()
            st.success("ลบภารกิจเรียบร้อย!")
            st.rerun()
            
        if st.session_state.get(f"editing_t_{t_obj['id']}", False):
            with st.container():
                st.markdown(f"**🛠️ กำลังแก้ไขข้อความภารกิจที่ {t_idx+1}**")
                e_task = st.text_area("แก้ไขข้อความภารกิจ", value=t_obj['task_detail'], key=f"et_text_{t_obj['id']}")
                if st.button("💾 บันทึกการแก้ไขข้อความ", key=f"save_t_{t_obj['id']}"):
                    db.collection("tasks").document(t_obj['id']).update({"task_detail": e_task})
                    st.session_state[f"editing_t_{t_obj['id']}"] = False
                    st.success("อัปเดตข้อความสำเร็จ!")
                    st.rerun()
