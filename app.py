import streamlit as st
import datetime
import requests
from google.oauth2 import service_account
from google.cloud import firestore
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- 1. ตั้งค่าคอนฟิกของ Streamlit Page ---
st.set_page_config(
    page_title="ระบบบันทึกรายงานผลการปฏิบัติงาน - งานสอบสวน สภ.ไม้แก่น",
    page_icon="👮‍♂️",
    layout="centered"
)

# --- 2. ฟังก์ชันดึง Credentials และ Service ต่างๆ ---
@st.cache_resource
def get_firestore_db():
    cred_dict = dict(st.secrets["firebase"])
    if "private_key" in cred_dict:
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n").strip()
    
    creds = service_account.Credentials.from_service_account_info(
        cred_dict,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    return firestore.Client(credentials=creds, project=creds.project_id)

@st.cache_resource
def get_drive_service():
    cred_dict = dict(st.secrets["firebase"])
    if "private_key" in cred_dict:
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n").strip()
    
    creds = service_account.Credentials.from_service_account_info(
        cred_dict,
        scopes=["https://www.googleapis.com/auth/drive.file"]
    )
    return build("drive", "v3", credentials=creds)

# --- 3. ฟังก์ชันการอัปโหลดไฟล์ไป Google Drive ---
def upload_to_drive(file_obj, filename, folder_id):
    try:
        service = get_drive_service()
        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(file_obj, mimetype=file_obj.type, resumable=True)
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()
        
        # ปรับสิทธิ์ไฟล์เป็น Anyone with link can view (สำหรับแสดงผลรูป)
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=uploaded_file.get('id'), body=permission).execute()
        
        # สร้าง Direct Image URL สำหรับแสดงผล
        direct_url = f"https://lh3.googleusercontent.com/d/{uploaded_file.get('id')}"
        return direct_url
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลดไฟล์ไป Google Drive: {e}")
        return None

# --- 4. ฟังก์ชันส่งการแจ้งเตือนผ่าน LINE Notify / Messaging API ---
def send_line_notify(message_text):
    try:
        line_token = st.secrets["line"]["channel_access_token"]
        group_id = st.secrets["line"]["group_id"]
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "json",
            "Authorization": f"Bearer {line_token}"
        }
        payload = {
            "to": group_id,
            "messages": [
                {
                    "type": "text",
                    "text": message_text
                }
            ]
        }
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        st.warning(f"ไม่สามารถส่งการแจ้งเตือน LINE ได้: {e}")

# --- 5. จัดลำดับยศตำรวจ ---
def get_rank_priority(rank_str):
    ranks_priority = {
        "พล.ต.อ.": 1, "พล.ต.ท.": 2, "พล.ต.ต.": 3, "พ.ต.อ.": 4, "พ.ต.ท.": 5,
        "พ.ต.ต.": 6, "ร.ต.อ.": 7, "ร.ต.ฮ.": 8, "ร.ต.ต.": 9, "ด.ต.": 10,
        "จ.ส.ต.": 11, "ส.ต.อ.": 12, "ส.ต.ท.": 13, "ส.ต.ต.": 14,
    }
    return ranks_priority.get(rank_str.strip(), 99)

# --- 6. โหลดข้อมูลบุคลากรและภารกิจ ---
@st.cache_data(ttl=300)
def load_personnel():
    default_p = [
        {"rank": "พ.ต.ท.", "name": "ปฐมพงศ์ ศีรษะพล", "position": "สว.(สอบสวน) สภ.ไม้แก่น"},
        {"rank": "ร.ต.อ.", "name": "สมเจต ทองแผ่น", "position": "รอง สว.(สอบสวน) สภ.นาประดู่ ปรก.สภ.ไม้แก่น"},
        {"rank": "ร.ต.อ.", "name": "ตุลกร สุริยวงศ์", "position": "รอง สว.(สอบสวน) สภ.ไม้แก่น"},
        {"rank": "ด.ต.", "name": "ประสาน ปรงแก้ว", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
        {"rank": "จ.ส.ต.", "name": "อาลีฟ มะเก๊ะ", "position": "ผบ.หมู่(ป.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
        {"rank": "ส.ต.ท.", "name": "ธนกฤต คงบุญช่วย", "position": "ผบ.หมู่(ผช.พงส.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
        {"rank": "ส.ต.ต.", "name": "สุริยา บุญชูดวง", "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน"},
    ]
    try:
        client = get_firestore_db()
        docs = list(client.collection("personnel").stream())
        personnel = []
        for doc in docs:
            p_data = doc.to_dict()
            p_data["id"] = doc.id
            personnel.append(p_data)

        if not personnel:
            batch = client.batch()
            for p in default_p:
                doc_ref = client.collection("personnel").document()
                batch.set(doc_ref, p)
                p["id"] = doc_ref.id
                personnel.append(p)
            batch.commit()

        personnel.sort(key=lambda x: get_rank_priority(x["rank"]))
        return personnel
    except Exception as e:
        default_p.sort(key=lambda x: get_rank_priority(x["rank"]))
        return default_p

@st.cache_data(ttl=300)
def load_tasks():
    default_tasks = [
        "ได้นำตัวผู้ต้องหาคดียาเสพติด ส่งตัวฝากขังต่อศาลจังหวัดปัตตานี",
        "ได้รับมอบหมายจากพนักงานสอบสวน ยื่นคำร้องฝากขังต่อ ครั้งที่ 2,3 และ 4 ต่อศาลจังหวัดปัตตานี",
        "ได้ส่งสำนวนการสอบสวนคดียาเสพติด จำนวน 1 เรื่อง ที่พนักงานสอบสวนทำการสอบสวนเสร็จสิ้นแล้ว ไปยังพนักงานอัยการจังหวัดปัตตานี",
        "ได้นำยาเสพติดของกลางในคดีอาญา ส่งตรวจพิสูจน์ กลุ่มงานตรวจพิสูจน์ยาเสพติด พิสูจน์หลักฐานจังหวัดปัตตานี",
    ]
    try:
        client = get_firestore_db()
        docs = list(client.collection("tasks").stream())
        tasks = []
        for doc in docs:
            t_data = doc.to_dict()
            t_data["id"] = doc.id
            tasks.append(t_data)

        if not tasks:
            batch = client.batch()
            for t in default_tasks:
                doc_ref = client.collection("tasks").document()
                batch.set(doc_ref, {"task_detail": t})
                tasks.append({"id": doc_ref.id, "task_detail": t})
            batch.commit()
        return tasks
    except Exception as e:
        return [{"id": str(i), "task_detail": t} for i, t in enumerate(default_tasks)]

# --- 7. ส่วนแสดงผล UI หน้าแอปพลิเคชัน ---
st.title("👮‍♂️ ระบบบันทึกรายงานผลการปฏิบัติงาน")
st.caption("งานสอบสวน สถานีตำรวจภูธรไม้แก่น")

personnel_list = load_personnel()
task_list = load_tasks()

with st.form("report_form", clear_on_submit=True):
    st.subheader("📝 กรอกข้อมูลรายงานผลการปฏิบัติงาน")
    
    # เลือกระบุวันที่
    report_date = st.date_input("วันที่ปฏิบัติงาน", datetime.date.today())
    
    # เลือกชื่อผู้รายงาน
    personnel_options = [f"{p['rank']} {p['name']} ({p['position']})" for p in personnel_list]
    selected_personnel = st.selectbox("ข้าราชการตำรวจผู้รายงาน", personnel_options)
    
    # เลือกภารกิจ
    task_options = [t['task_detail'] for t in task_list] + ["อื่นๆ (ระบุเอง)"]
    selected_task = st.selectbox("ภารกิจที่ได้รับมอบหมาย", task_options)
    
    custom_task = ""
    if selected_task == "อื่นๆ (ระบุเอง)":
        custom_task = st.text_area("รายละเอียดภารกิจเพิ่มเติม")
        
    # อัปโหลดรูปภาพผลการปฏิบัติงาน
    uploaded_files = st.file_uploader(
        "แนบรูปภาพผลการปฏิบัติงาน (อัปโหลดเข้า Google Drive)", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=True
    )
    
    submit_button = st.form_submit_button("บันทึกและส่งรายงาน")

if submit_button:
    task_final = custom_task if selected_task == "อื่นๆ (ระบุเอง)" else selected_task
    
    if not task_final.strip():
        st.error("กรุณาระบุรายละเอียดภารกิจ")
    else:
        with st.spinner("กำลังบันทึกข้อมูลและอัปโหลดรูปภาพ..."):
            image_urls = []
            folder_id = st.secrets["gdrive"]["folder_id"]
            
            if uploaded_files:
                for file in uploaded_files:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{file.name}"
                    url = upload_to_drive(file, filename, folder_id)
                    if url:
                        image_urls.append(url)
            
            # บันทึกลง Firestore
            try:
                db = get_firestore_db()
                report_data = {
                    "report_date": report_date.strftime("%Y-%m-%d"),
                    "reporter": selected_personnel,
                    "task_detail": task_final,
                    "images": image_urls,
                    "created_at": firestore.SERVER_TIMESTAMP
                }
                db.collection("reports").add(report_data)
                
                # ส่งแจ้งเตือนทาง LINE
                line_msg = f"\n📢 **รายงานผลการปฏิบัติงาน**\n📅 วันที่: {report_date.strftime('%d/%m/%Y')}\n👤 ผู้รายงาน: {selected_personnel}\n📌 ภารกิจ: {task_final}"
                if image_urls:
                    line_msg += f"\n🖼️ รูปภาพ ({len(image_urls)} รูป): {image_urls[0]}"
                send_line_notify(line_msg)
                
                st.success("บันทึกข้อมูลและส่งรายงานเรียบร้อยแล้ว!")
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}")
