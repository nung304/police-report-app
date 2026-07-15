# ==================== แบ่งหน้าการทำงานด้วยระบบ Tabs (สลับตำแหน่งใหม่) ====================
tab1, tab2 = st.tabs(["📝 1. รายงานสรุปผลการปฏิบัติประจำวัน (แยกคน/เวลา/ภารกิจ)", "👮‍♂️ 2. รายงานรูปแบบเดิม (เดี่ยว/พร้อมพวก)"])

# ----------------- TAB 1: รายงานสรุปผลการปฏิบัติประจำวัน (สลับมาเป็นอันแรก) -----------------
with tab1:
    t2_col1, t2_col2 = st.columns([1.2, 1])
    
    # คอลัมน์กรอกข้อมูลรายการภารกิจรายบุคคล
    with t2_col1:
        with st.container(border=True):
            st.markdown("### 📝 สรุปรายการภารกิจวันนี้")
            num_tasks_t2 = st.number_input("จำนวนภารกิจที่ต้องการสรุป (เรื่อง)", min_value=1, max_value=10, value=1, step=1, key="t2_num_tasks")
            
            report_items_t2 = []
            
            for i in range(int(num_tasks_t2)):
                st.markdown(f"**📍 รายการภารกิจที่ {i+1}**")
                
                # 1. เลือกผู้ปฏิบัติหลักประจำข้อนั้น ๆ
                selected_officer_t2 = st.selectbox(f"👮‍♂️ ผู้ปฏิบัติหลัก คนที่ {i+1}", list(officer_options.keys()), key=f"t2_off_{i}")
                officer_t2 = officer_options[selected_officer_t2]
                
                # ตัวเลือกสำหรับเพิ่มรายชื่อผู้ปฏิบัติร่วมในภารกิจย่อย
                with_team_t2 = st.checkbox("➕ มีผู้ปฏิบัติร่วมในภารกิจนี้", value=False, key=f"t2_with_team_{i}")
                team_member_lines_t2 = ""
                has_team_names_t2 = False
                
                if_team_t2 = st.checkbox if with_team_t2:
                    num_team_t2 = st.number_input(f"จำนวนผู้ปฏิบัติร่วม (ภารกิจที่ {i+1})", min_value=1, max_value=10, value=1, step=1, key=f"t2_num_team_{i}")
                    for j in range(int(num_team_t2)):
                        team_select_t2 = st.selectbox(f"👤 เลือกผู้ปฏิบัติร่วมคนที่ {j+1} (ภารกิจที่ {i+1})", ["-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --"] + list(officer_options.keys()), key=f"t2_team_member_{i}_{j}")
                        if team_select_t2 != "-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --":
                            member_t2 = officer_options[team_select_t2]
                            # จัดให้เรียงลงบรรทัดล่าง มีชื่อและตำแหน่งครบถ้วน
                            team_member_lines_t2 += f"\n{member_t2['rank']}{member_t2['name']}\n{member_t2['position']}"
                            has_team_names_t2 = True
                
                suffix_t2 = ""
                if with_team_t2:
                    suffix_t2 = " พร้อมด้วย" if has_team_names_t2 else " พร้อมพวก"
                
                # 2. ระบุเวลาเฉพาะของภารกิจนั้น
                time_input_t2 = st.text_input(f"⏰ เวลาภารกิจที่ {i+1} (น.)", value="08.30", key=f"t2_time_{i}")
                
                # 3. ค้นหาข้อความภารกิจหรือพิมพ์อิสระ
                task_select_t2 = st.selectbox(f"🔍 เลือกคลังข้อความภารกิจ ({i+1})", ["-- พิมพ์ข้อความเองอิสระ --"] + tasks_list, key=f"t2_select_{i}")
                if task_select_t2 == "-- พิมพ์ข้อความเองอิสระ --":
                    task_detail_t2 = st.text_input(f"✍️ พิมพ์ภารกิจเอง ({i+1})", key=f"t2_custom_{i}")
                else:
                    task_detail_t2 = task_select_t2
                
                # จัดเรียงโครงสร้างข้อความแบบใหม่ตามแพตเทิร์นที่คุณตำรวจกำหนด
                if task_detail_t2:
                    item_text = f"{i+1}. เวลา {time_input_t2} น.\n{officer_t2['rank']}{officer_t2['name']}\n{officer_t2['position']}{suffix_t2}{team_member_lines_t2}\n{task_detail_t2}"
                    report_items_t2.append(item_text)
                    
                st.divider() # ขีดเส้นกั้นจบแต่ละรายการ

    # คอลัมน์แสดงผลลัพธ์ของแพตเทิร์นข้อความชุดใหม่
    with t2_col2:
        with st.container(border=True):
            st.markdown("### 📋 ข้อความสรุปรวม Line")
            
            joined_items_t2 = "\n".join(report_items_t2)
            final_text_t2 = f"สภ.ไม้แก่น \nงานสอบสวน\nเรียนผู้บังคับบัญชา\nรายงานสรุปผลการปฏิบัติประจำวันที่ {date_str}\n{joined_items_t2}\n\nจึงเรียนมาเพื่อโปรดทราบ"
            
            st.code(final_text_t2, language="text")
            st.success("👆 แตะปุ่มไอคอนสี่เหลี่ยมซ้อนกันที่มุมขวาบนเพื่อ Copy ไปส่งกลุ่ม Line สรุปงานประจำวันได้ทันที")


# ----------------- TAB 2: รายงานรูปแบบเดิม (สลับมาเป็นอันหลัง) -----------------
with tab2:
    main_col1, main_col2, main_col3 = st.columns([1, 1, 1.1])

    # คอลัมน์ที่ 1: เวลา / เจ้าหน้าที่
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

    # คอลัมน์ที่ 2: รายละเอียดภารกิจ
    with main_col2:
        with st.container(border=True):
            st.markdown("### 📝 รายละเอียดภารกิจ")
            num_tasks = st.number_input("📌 จำนวนภารกิจที่ต้องการรายงาน (เรื่อง)", min_value=1, max_value=5, value=1, step=1, key="t1_num_tasks")

            all_task_details = []
            for idx in range(int(num_tasks)):
                st.markdown(f"**📍 ภารกิจเรื่องที่ {idx+1}**")
                selected_task = st.selectbox(
                    f"เลือกหรือค้นหาข้อความภารกิจที่ {idx+1}", 
                    [""] + tasks_list, 
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

    # คอลัมน์ที่ 3: ข้อความรายงานสำหรับส่ง
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
