import streamlit as st
from datetime import datetime

st.set_page_config(page_title="ระบบสร้างข้อความรายงาน สภ.ไม้แก่น", page_icon="👮‍♂️", layout="centered")
st.title("👮‍♂️ ระบบข้อความรายงาน Line Group")
st.subheader("งานสอบสวน สภ.ไม้แก่น")

# ฐานข้อมูลในระบบออนไลน์ (สามารถแก้ไขเพิ่มรายชื่อตรงนี้ได้เลย)
if "personnel" not in st.session_state:
    st.session_state.personnel = [
        {"id": 1, "rank": "ด.ต.", "name": "ประสาน ปรงแก้ว", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
        {"id": 2, "rank": "ร.ต.อ.", "name": "สมชาย ตั้งใจ", "position": "รอง สว.(สอบสวน) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"}
    ]

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        "นำตัวผู้ต้องหาคดียาเสพติด ส่งตัวฝากขังต่อศาลจังหวัดปัตตานี เสร็จสิ้นเรียบร้อยแล้ว",
        "ได้รับมอบหมายจากพนักงานสอบสวน ยื่นคำร้องฝากขังต่อ ครั้งที่ 2,3 และ 4 ต่อศาลจังหวัดปัตตานี",
        "นำตัวผู้ต้องหาคดียาเสพติด ส่งตัวไปยังพนักงานอัยการจังหวัดปัตตานี เพื่อฟ้องต่อศาลจังหวัดปัตตานี เสร็จสิ้นเรียบร้อยแล้ว",
        "ส่งสำนวนการสอบสวนคดีอยาเสพติด จำนวน 1 เรื่อง ที่พนักงานสอบสวนทำการสอบสวนเสร็จสิ้นแล้ว ไปยังพนักงานอัยการจังหวัดปัตตานี เพื่อดำเนินการตามกฎหมายต่อไป",
        "นำยาเสพติดของกลางในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจพิสูจน์ยาเสพติด พิสูจน์หลักฐานจังหวัดปัตตานี",
        "ดำเนินการติดตามผลการตรวจพิสูจน์ของกลางในคดีอาญา   กลุ่มงานตรวจทางเคมี ฟิสิกส์ ศุูนย์พิสูจน์หลักฐาน 10 ศูนย์นิติวิทยาศาสตร์จังหวัดชายแดนภาคใต้ เพื่อนำมาประกอบสำนวนการสอบสวน"
    ]

officer_options = {f"{p['rank']}{p['name']} ({p['position']})": p for p in st.session_state.personnel}

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

st.markdown("### 👤 ผู้ปฏิบัติหน้าที่")
main_officer_select = st.selectbox("เลือกผู้ปฏิบัติหลัก (คนแรก)", list(officer_options.keys()))
main_officer = officer_options[main_officer_select]

with_team = st.checkbox("พร้อมพวก")
team_officer_str = ""
has_team_member = False

if with_team:
    team_options = ["-- เว้นว่างไว้ (ไม่ระบุชื่อคนถัดไป) --"] + list(officer_options.keys())
    second_officer_select = st.selectbox("เลือกผู้ปฏิบัติร่วม (คนที่ 2)", team_options)
    if second_officer_select != "-- เว้นว่างไว้ (ไม่ระบุชื่อคนถัดไป) --":
        sec_officer = officer_options[second_officer_select]
        team_officer_str = f"{sec_officer['rank']}{sec_officer['name']} {sec_officer['position']}"
        has_team_member = True

st.markdown("### 📝 รายละเอียดภารกิจ")
task_mode = st.radio("รูปแบบภารกิจ", ["เลือกจากรายการที่มีอยู่", "กรอกภารกิจใหม่เอง"])

if task_mode == "เลือกจากรายการที่มีอยู่":
    task_detail = st.selectbox("เลือกภารกิจ", st.session_state.tasks)
else:
    new_task = st.text_area("พิมพ์ภารกิจใหม่ที่นี่")
    if st.button("💾 บันทึกภารกิจนี้เข้าสู่รายการคราวหน้า"):
        if new_task and new_task not in st.session_state.tasks:
            st.session_state.tasks.append(new_task)
            st.success("บันทึกภารกิจใหม่เข้าสู่ระบบเรียบร้อย!")
            st.rerun()
    task_detail = new_task

st.markdown("---")
st.markdown("### 📋 ข้อความรายงานที่พร้อมส่ง (Output)")

suffix = " พร้อมพวก" if with_team else ""

if with_team and has_team_member:
    report_text = f"""สภ.ไม้แก่น 
งานสอบสวน
เรียน ผู้บังคับบัญชา
เมื่อ {date_str} เวลาประมาณ {time_str} น.
{main_officer['rank']}{main_officer['name']}
{main_officer['position']}{suffix}
{team_officer_str}
{task_detail}
   จึงเรียนมาเพื่อโปรดทราบ"""
else:
    report_text = f"""สภ.ไม้แก่น 
งานสอบสวน
เรียน ผู้บังคับบัญชา
เมื่อ {date_str} เวลาประมาณ {time_str} น.
{main_officer['rank']}{main_officer['name']}
{main_officer['position']}{suffix}
{task_detail}
   จึงเรียนมาเพื่อโปรดทราบ"""

st.code(report_text, language="text")
st.info("💡 สามารถกดไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนของกล่องข้อความด้านบนเพื่อ Copy ไปวางในไลน์ได้เลย!")
