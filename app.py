import streamlit as st
from datetime import datetime
import pandas as pd
import os

st.set_page_config(page_title="ระบบสร้างข้อความรายงาน สภ.ไม้แก่น", page_icon="👮‍♂️", layout="centered")
st.title("👮‍♂️ ระบบข้อความรายงาน Line Group")
st.subheader("งานสอบสวน สภ.ไม้แก่น")

# ชื่อไฟล์สำหรับเก็บข้อมูลถาวร
PERSONNEL_FILE = "personnel_data.csv"
TASKS_FILE = "tasks_data.csv"

# --- 1. ฟังก์ชันโหลดและบันทึกข้อมูลระดับไฟล์ ---
def load_data():
    if os.path.exists(PERSONNEL_FILE):
        df_p = pd.read_csv(PERSONNEL_FILE)
        personnel = df_p.to_dict(orient="records")
    else:
        personnel = [
            {"rank": "พ.ต.ท.", "name": "ปฐมพงศ์ ศีรษะพล", "position": "สว.(สอบสวน) สภ.ไม้แก่น"},
            {"rank": "ร.ต.อ.", "name": "สมเจต ทองแผ่น", "position": "รอง สว.(สอบสวน) สภ.นาประดู่ ปรก.สภ.ไม้แก่น"},
            {"rank": "ร.ต.อ.", "name": "ตุลกร สุริยวงศ์", "position": "รอง สว.(สอบสวน) สภ.ไม้แก่น"},
            {"rank": "ด.ต.", "name": "ประสาน ปรงแก้ว", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
            {"rank": "จ.ส.ต.", "name": "อาลีฟ มะเก๊ะ", "position": "ผบ.หมู่(ป.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
            {"rank": "ส.ต.ท.", "name": "ธนกฤต คงบุญช่วย", "position": "ผบ.หมู่(ผช.พงส.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
            {"rank": "ส.ต.ต.", "name": "สุริยา บุญชูดวง", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"}
        ]
        pd.DataFrame(personnel).to_csv(PERSONNEL_FILE, index=False)

    if os.path.exists(TASKS_FILE):
        df_t = pd.read_csv(TASKS_FILE)
        tasks = df_t["task_detail"].dropna().tolist()
    else:
        tasks = [
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
        pd.DataFrame({"task_detail": tasks}).to_csv(TASKS_FILE, index=False)
        
    return personnel, tasks

personnel_list, tasks_list = load_data()
officer_options = {f"{p['rank']}{p['name']} ({p['position']})": p for p in personnel_list}

# --- 2. วันที่และเวลาภารกิจ ---
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

# --- 3. ผู้ปฏิบัติหน้าที่ ---
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

# --- 4. รายละเอียดภารกิจ ---
st.markdown("### 📝 รายละเอียดภารกิจ")
num_tasks = st.number_input("จำนวนภารกิจที่ต้องการรายงาน (กี่เรื่อง)", min_value=1, max_value=5, value=1, step=1)

all_task_details = []

for idx in range(int(num_tasks)):
    st.markdown(f"**📍 ภารกิจเรื่องที่ {idx+1}**")
    
    selected_task = st.selectbox(
        f"พิมพ์คำค้นหาหรือเลือกข้อความภารกิจที่ {idx+1}", 
        tasks_list, 
        key=f"select_{idx}"
    )
    if selected_task:
        processed_task = selected_task
        if processed_task.startswith("ได้นำ"):
            processed_task = processed_task.replace("ได้นำ", "นำ", 1)
        all_task_details.append(processed_task)

# ระบบพิมพ์เพิ่มด่วนกรณีไม่มีข้อความที่ต้องการในคลัง
with st.expander("➕ พิมพ์ภารกิจใหม่นอกเหนือจากในคลังเพื่อบันทึกถาวร"):
    new_detail = st.text_area("พิมพ์รายละเอียดภารกิจฉบับเต็มใหม่ที่นี่")
    if st.button("💾 บันทึกเข้าคลังภารกิจถาวร"):
        if new_detail:
            if new_detail not in tasks_list:
                tasks_list.append(new_detail)
                pd.DataFrame({"task_detail": tasks_list}).to_csv(TASKS_FILE, index=False)
                st.success("บันทึกภารกิจใหม่เรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("❌ มีข้อความภารกิจนี้อยู่ในระบบแล้ว")
        else:
            st.warning("⚠️ กรุณากรอกรายละเอียดภารกิจก่อนกดบันทึก")

# 🟢 นำเรื่องมาเชื่อมกันด้วย , และต่อท้ายด้วยคำว่า "เสร็จสิ้นเรียบร้อยแล้ว" หลังเรื่องสุดท้าย
final_tasks_text = ""
valid_tasks = [task for task in all_task_details if task]
if valid_tasks:
    final_tasks_text = " ,".join(valid_tasks) + " เสร็จสิ้นเรียบร้อยแล้ว"

# --- 5. ประมวลผลและสร้างข้อความรายงาน (Output) ---
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
st.info("💡 สามารถกดไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนของกล่องข้อความเพื่อ Copy ไปวางในไลน์ได้ทันที!")


# --- 6. เมนูพิเศษ: แผงควบคุมและแก้ไขจัดการฐานข้อมูลอัจฉริยะ ---
st.markdown("---")
with st.expander("⚙️ เมนูจัดการข้อมูลอย่างละเอียด (เพิ่ม / แก้ไข / ลบ รายชื่อและภารกิจ)"):
    
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
            personnel_list.append({"rank": n_rank, "name": n_name, "position": n_pos})
            pd.DataFrame(personnel_list).to_csv(PERSONNEL_FILE, index=False)
            st.success("บันทึกรายชื่อสำเร็จ!")
            st.rerun()

    st.markdown("**📋 รายชื่อทั้งหมดในระบบปัจจุบัน (สามารถกด แก้ไข หรือ ลบ ได้ที่ตารางด้านล่าง)**")
    for p_idx, person in enumerate(personnel_list):
        p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns([1, 2, 4, 1, 1])
        p_col1.write(person['rank'])
        p_col2.write(person['name'])
        p_col3.write(person['position'])
        
        if p_col4.button("✏️", key=f"edit_p_{p_idx}"):
            st.session_state[f"editing_p_{p_idx}"] = True
            
        if p_col5.button("🗑️", key=f"del_p_{p_idx}"):
            personnel_list.pop(p_idx)
            pd.DataFrame(personnel_list).to_csv(PERSONNEL_FILE, index=False)
            st.success("ลบรายชื่อเรียบร้อย!")
            st.rerun()
            
        if st.session_state.get(f"editing_p_{p_idx}", False):
            with st.container():
                st.markdown(f"**🛠️ กำลังแก้ไขข้อมูลของ: {person['rank']}{person['name']}**")
                e_rank = st.text_input("แก้ไขยศ", value=person['rank'], key=f"er_{p_idx}")
                e_name = st.text_input("แก้ไขชื่อ-สกุล", value=person['name'], key=f"en_{p_idx}")
                e_pos = st.text_input("แก้ไขตำแหน่ง", value=person['position'], key=f"ep_{p_idx}")
                if st.button("💾 บันทึกการแก้ไข", key=f"save_p_{p_idx}"):
                    personnel_list[p_idx] = {"rank": e_rank, "name": e_name, "position": e_pos}
                    pd.DataFrame(personnel_list).to_csv(PERSONNEL_FILE, index=False)
                    st.session_state[f"editing_p_{p_idx}"] = False
                    st.success("อัปเดตข้อมูลสำเร็จ!")
                    st.rerun()

    # ==================== ส่วนที่ 2: จัดการข้อความภารกิจ ====================
    st.markdown("---")
    st.markdown("### 📝 2. จัดการคลังข้อความภารกิจ")
    
    st.markdown("**📋 รายการภารกิจทั้งหมดในระบบ (สามารถกด แก้ไข หรือ ลบ ได้ที่รายการด้านล่าง)**")
    for t_idx, task in enumerate(tasks_list):
        t_col1, t_col2, t_col3 = st.columns([7, 1, 1])
        t_col1.write(f"{t_idx+1}. {task}")
        
        if t_col2.button("✏️", key=f"edit_t_{t_idx}"):
            st.session_state[f"editing_t_{t_idx}"] = True
            
        if t_col3.button("🗑️", key=f"del_t_{t_idx}"):
            tasks_list.pop(t_idx)
            pd.DataFrame({"task_detail": tasks_list}).to_csv(TASKS_FILE, index=False)
            st.success("ลบภารกิจเรียบร้อย!")
            st.rerun()
            
        if st.session_state.get(f"editing_t_{t_idx}", False):
            with st.container():
                st.markdown(f"**🛠️ กำลังแก้ไขข้อความภารกิจที่ {t_idx+1}**")
                e_task = st.text_area("แก้ไขข้อความภารกิจ", value=task, key=f"et_text_{t_idx}")
                if st.button("💾 บันทึกการแก้ไขข้อความ", key=f"save_t_{t_idx}"):
                    tasks_list[t_idx] = e_task
                    pd.DataFrame({"task_detail": tasks_list}).to_csv(TASKS_FILE, index=False)
                    st.session_state[f"editing_t_{t_idx}"] = False
                    st.success("อัปเดตข้อความสำเร็จ!")
                    st.rerun()

    # ==================== ส่วนที่ 3: ระบบสำรองข้อมูลดาวน์โหลด ====================
    st.markdown("---")
    st.markdown("### 📥 3. ดาวน์โหลดไฟล์สำรองข้อมูล (CSV)")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        if os.path.exists(PERSONNEL_FILE):
            with open(PERSONNEL_FILE, "rb") as f:
                st.download_button("📂 ดาวน์โหลดไฟล์รายชื่อทั้งหมด", f, file_name=PERSONNEL_FILE, mime="text/csv")
    with col_dl2:
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, "rb") as f:
                st.download_button("📂 ดาวน์โหลดไฟล์ภารกิจทั้งหมด", f, file_name=TASKS_FILE, mime="text/csv")
