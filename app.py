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
        key=f"select_{idx}",
        help="สามารถพิมพ์ค้นหาข้อความได้เลย"
    )
    if selected_task:
        # 🟢 ตัวตรวจสอบข้อความอัตโนมัติ: ถ้าขึ้นต้นด้วย "ได้นำ" ให้เปลี่ยนเป็น "นำ" ทันที
        processed_task = selected_task
        if processed_task.startswith("ได้นำ"):
            processed_task = processed_task.replace("ได้นำ", "นำ", 1)
        all_task_details.append(processed_task)

# ระบบพิมพ์เพิ่มกรณีไม่มีข้อความที่ต้องการในคลัง
with st.expander("➕ กรณีต้องการพิมพ์ภารกิจใหม่นอกเหนือจากในคลังเพื่อบันทึกถาวร"):
    new_detail = st.text_area("พิมพ์รายละเอียดภารกิจฉบับเต็มใหม่ที่นี่")
    if st.button("💾 บันทึกเข้าคลังภารกิจถาวร"):
        if new_detail:
            if new_detail not in tasks_list:
                tasks_list.append(new_detail)
                pd.DataFrame({"task_detail": tasks_list}).to_csv(TASKS_FILE, index=False)
                st.success("บันทึกภารกิจใหม่เข้าสู่ตัวเลือกถาวรเรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.error("❌ มีข้อความภารกิจนี้อยู่ในระบบแล้ว")
        else:
            st.warning("⚠️ กรุณากรอกรายละเอียดภารกิจก่อนกดบันทึก")

# ประมวลผลรวมข้อความ: เคาะ 1 ทีแล้วใส่เครื่องหมายจุลภาคคั่นระหว่างเรื่อง
final_tasks_text = " ,".join([task for task in all_task_details if task])

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

# --- 6. เมนูพิเศษ: จัดการฐานข้อมูล (เพิ่ม/ลบ ข้อมูล) ---
st.markdown("---")
with st.expander("⚙️ เมนูจัดการข้อมูล (เพิ่มหรือลบ รายชื่อ/ภารกิจ)"):
    
    st.markdown("#### 👤 จัดการรายชื่อเจ้าหน้าที่")
    col_add1, col_add2 = st.columns([2, 1])
    
    with col_add1:
        with st.form("add_officer_form", clear_on_submit=True):
            st.markdown("**➕ เพิ่มรายชื่อใหม่**")
            new_rank = st.text_input("ยศ (เช่น ด.ต. / ร.ต.อ.)")
            new_name = st.text_input("ชื่อ-นามสกุล")
            new_pos = st.text_input("ตำแหน่ง")
            submit_btn = st.form_submit_button("💾 บันทึกรายชื่อ")
            
            if submit_btn and new_rank and new_name and new_pos:
                personnel_list.append({"rank": new_rank, "name": new_name, "position": new_pos})
                pd.DataFrame(personnel_list).to_csv(PERSONNEL_FILE, index=False)
                st.success(f"บันทึกรายชื่อ {new_rank}{new_name} สำเร็จ!")
                st.rerun()
                
    with col_add2:
        st.markdown("**🗑️ ลบรายชื่อที่มีอยู่**")
        officer_to_delete = st.selectbox("เลือกชื่อที่ต้องการลบ", ["-- เลือกเพื่อลบ --"] + list(officer_options.keys()))
        if officer_to_delete != "-- เลือกเพื่อลบ --":
            if st.button("❌ ยืนยันลบรายชื่อนี้", type="primary"):
                target = officer_options[officer_to_delete]
                personnel_list = [p for p in personnel_list if not (p['name'] == target['name'] and p['rank'] == target['rank'])]
                pd.DataFrame(personnel_list).to_csv(PERSONNEL_FILE, index=False)
                st.success("ลบรายชื่อเรียบร้อยแล้ว!")
                st.rerun()

    st.markdown("---")
    
    st.markdown("#### 📝 จัดการข้อความภารกิจ")
    task_to_delete = st.selectbox("เลือกข้อความภารกิจที่ต้องการลบ", ["-- เลือกเพื่อลบ --"] + tasks_list)
    if task_to_delete != "-- เลือกเพื่อลบ --":
        if st.button("❌ ยืนยันลบภารกิจนี้", type="primary"):
            tasks_list.remove(task_to_delete)
            pd.DataFrame({"task_detail": tasks_list}).to_csv(TASKS_FILE, index=False)
            st.success("ลบข้อความภารกิจเรียบร้อยแล้ว!")
            st.rerun()
