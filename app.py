import streamlit as st
from datetime import datetime
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="ระบบสร้างข้อความรายงาน สภ.ไม้แก่น", page_icon="👮‍♂️", layout="centered")
st.title("👮‍♂️ ระบบข้อความรายงาน Line Group")
st.subheader("งานสอบสวน สภ.ไม้แก่น")

# --- 1. เชื่อมต่อฐานข้อมูล Google Sheets ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_personnel = conn.read(worksheet="personnel", ttl="0m")
    df_tasks = conn.read(worksheet="tasks", ttl="0m")
except Exception as e:
    st.error("⚠️ กรุณาตั้งค่าการเชื่อมต่อ Google Sheets ใน Secrets ก่อนใช้งาน")
    st.stop()

# แปลงข้อมูลในชีตมาเป็น List เพื่อใช้งานในระบบ
personnel_list = df_personnel.to_dict(orient="records")
tasks_list = df_tasks["task_detail"].dropna().tolist()

# สร้างตัวเลือกสำหรับ Dropdown รายชื่อเจ้าหน้าที่
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
    time_input = st.time_input("เลือกเวลา", datetime.now().time())
    time_str = time_input.strftime("%H.%M")

# --- 3. ผู้ปฏิบัติหน้าที่ ---
st.markdown("### 👤 ผู้ปฏิบัติหน้าที่")
main_officer_select = st.selectbox("เลือกผู้ปฏิบัติหลัก (คนแรก)", list(officer_options.keys()))
main_officer = officer_options[main_officer_select]

# ฟังก์ชันติ๊กพร้อมพวกและเลือกจำนวนคน
with_team = st.checkbox("พร้อมพวก")
team_officers = []

if with_team:
    num_team = st.number_input("จำนวนผู้ปฏิบัติร่วม (กี่คน)", min_value=1, max_value=10, value=1, step=1)
    
    for i in range(int(num_team)):
        team_select = st.selectbox(f"เลือกผู้ปฏิบัติร่วม คนที่ {i+1}", ["-- ไม่ระบุชื่อ (เว้นว่างไว้) --"] + list(officer_options.keys()), key=f"team_{i}")
        if team_select != "-- ไม่ระบุชื่อ (เว้นว่างไว้) --":
            team_officers.append(officer_options[team_select])

# --- 4. รายละเอียดภารกิจ (เลือกจากรายละเอียดโดยตรง) ---
st.markdown("### 📝 รายละเอียดภารกิจ")
task_mode = st.radio("รูปแบบภารกิจ", ["เลือกจากฐานข้อมูลภารกิจ", "กรอกภารกิจใหม่เอง"])

if task_mode == "เลือกจากฐานข้อมูลภารกิจ":
    # แสดงข้อความรายละเอียดภารกิจฉบับเต็มให้กดเลือกเลย
    task_detail = st.selectbox("เลือกข้อความรายละเอียดภารกิจ", tasks_list)
else:
    # กรณีมีงานใหม่ พิมพ์รายละเอียดลงช่องนี้ได้เลย
    new_detail = st.text_area("พิมพ์รายละเอียดข้อความรายงานฉบับเต็มที่นี่")
    
    if st.button("💾 บันทึกภารกิจนี้เข้าสู่ฐานข้อมูลถาวร"):
        if new_detail:
            if new_detail not in tasks_list:
                new_row = pd.DataFrame([{"task_detail": new_detail}])
                updated_tasks = pd.concat([df_tasks, new_row], ignore_index=True)
                conn.update(worksheet="tasks", data=updated_tasks)
                st.success("บันทึกภารกิจใหม่ลงฐานข้อมูลถาวรเรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("❌ มีข้อความภารกิจนี้อยู่ในฐานข้อมูลแล้ว")
        else:
            st.warning("⚠️ กรุณากรอกรายละเอียดภารกิจก่อนกดบันทึก")
    task_detail = new_detail

# --- 5. ประมวลผลและสร้างข้อความรายงาน (Output) ---
st.markdown("---")
st.markdown("### 📋 ข้อความรายงานที่พร้อมส่ง (Output)")

suffix = " พร้อมพวก" if with_team else ""

# รวบรวมรายชื่อผู้ปฏิบัติงานร่วมทั้งหมด
team_member_lines = ""
for member in team_officers:
    team_member_lines += f"\n{member['rank']}{member['name']} {member['position']}"

# ประกอบร่างข้อความรายงาน
report_text = f"""สภ.ไม้แก่น 
งานสอบสวน
เรียน ผู้บังคับบัญชา
เมื่อ {date_str} เวลาประมาณ {time_str} น.
{main_officer['rank']}{main_officer['name']}
{main_officer['position']}{suffix}{team_member_lines}
{task_detail}
   จึงเรียนมาเพื่อโปรดทราบ"""

st.code(report_text, language="text")
st.info("💡 สามารถกดไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนของกล่องข้อความเพื่อ Copy ไปวางในไลน์ได้ทันที!")

# --- 6. เมนูพิเศษ: ระบบเพิ่มรายชื่อเจ้าหน้าที่ ---
with st.expander("➕ คลิกเพื่อเพิ่มรายชื่อเจ้าหน้าที่ใหม่เข้าฐานข้อมูลถาวร"):
    with st.form("add_officer_form", clear_on_submit=True):
        new_rank = st.text_input("ยศ (เช่น ด.ต. / ร.ต.อ.)")
        new_name = st.text_input("ชื่อ-นามสกุล")
        new_pos = st.text_input("ตำแหน่ง (เช่น ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน)")
        submit_btn = st.form_submit_button("💾 บันทึกรายชื่อเจ้าหน้าที่")
        
        if submit_btn and new_rank and new_name and new_pos:
            new_person = pd.DataFrame([{"rank": new_rank, "name": new_name, "position": new_pos}])
            updated_personnel = pd.concat([df_personnel, new_person], ignore_index=True)
            conn.update(worksheet="personnel", data=updated_personnel)
            st.success(f"บันทึกรายชื่อ {new_rank}{new_name} ลงฐานข้อมูลสำเร็จ!")
            st.rerun()
