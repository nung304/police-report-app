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
            fields='id, webViewLink'
        ).execute()
        
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=uploaded_file.get('id'), body=permission).execute()
        
        direct_url = f"https://lh3.googleusercontent.com/d/{uploaded_file.get('id')}"
        return direct_url
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลดไฟล์ไป Google Drive: {e}")
        return None

# --- 4. ฟังก์ชันส่ง LINE Push Message (พร้อมภาพ) ---
def send_line_message(text_message, image_urls=None):
    try:
        line_token = st.secrets["line"]["channel_access_token"]
        group_id = st.secrets["line"]["group_id"]
        
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {line_token}"
        }
        
        messages = [
            {
                "type": "text",
                "text": text_message
            }
        ]
        
        if image_urls:
            for img_url in image_urls[:4]:  # จำกัดส่งไม่เกิน 4 รูปตามโควต้า LINE
                messages.append({
                    "type": "image",
                    "originalContentUrl": img_url,
                    "previewImageUrl": img_url
                })
                
        payload = {
            "to": group_id,
            "messages": messages
        }
        res = requests.post(url, json=payload, headers=headers)
        return res.status_code == 200
    except Exception as e:
        st.warning(f"ไม่สามารถส่งการแจ้งเตือน LINE ได้: {e}")
        return False

# --- 5. จัดลำดับยศตำรวจ ---
def get_rank_priority(rank_str):
    ranks_priority = {
        "พล.ต.อ.": 1, "พล.ต.ท.": 2, "พล.ต.ต.": 3, "พ.ต.อ.": 4, "พ.ต.ท.": 5,
        "พ.ต.ต.": 6, "ร.ต.อ.": 7, "ร.ต.ท.": 8, "ร.ต.ต.": 9, "ด.ต.": 10,
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

# --- 7. ส่วนการจัดการ UI และสร้างรายงาน ---
st.title("👮‍♂️ ระบบบันทึกรายงานผลการปฏิบัติงาน")
st.caption("งานสอบสวน สถานีตำรวจภูธรไม้แก่น")

personnel_list = load_personnel()
task_list = load_tasks()

st.subheader("📝 สร้างข้อความรายงานผลการปฏิบัติงาน")

# วันที่ปฏิบัติงาน
report_date = st.date_input("วันที่ปฏิบัติงาน", datetime.date.today())
th_year = report_date.year + 543
date_str = f"{report_date.day}/{report_date.month}/{th_year}"

# เลือกเจ้าหน้าที่
personnel_names = [f"{p['rank']} {p['name']}" for p in personnel_list]
selected_personnel = st.multiselect("ข้าราชการตำรวจผู้ปฏิบัติงาน", personnel_names, default=personnel_names[-1:] if personnel_names else None)

# เลือกภารกิจ
task_options = [t['task_detail'] for t in task_list] + ["อื่นๆ (ระบุเอง)"]
selected_task = st.selectbox("ภารกิจที่ได้รับมอบหมาย", task_options)

custom_task = ""
if selected_task == "อื่นๆ (ระบุเอง)":
    custom_task = st.text_area("รายละเอียดภารกิจเพิ่มเติม")

final_task_detail = custom_task if selected_task == "อื่นๆ (ระบุเอง)" else selected_task

# แนบรูปภาพผลการปฏิบัติงาน
uploaded_files = st.file_uploader("📸 แนบรูปภาพผลการปฏิบัติงาน (อัปโหลดเข้า Google Drive เพื่อส่งเข้า LINE)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

st.divider()

# รวมข้อความรายงานผลสำหรับนำไปส่ง LINE
officers_text = "\n".join([f"- {name}" for name in selected_personnel])
line_report_text = f"""เรียน ผู้บังคับบัญชา
งานสอบสวน สภ.ไม้แก่น ขอรายงานผลการปฏิบัติงาน ประจำวันที่ {date_str}

📌 ภารกิจ:
{final_task_detail}

👮‍♂️ ผู้ปฏิบัติงาน:
{officers_text}

จึงเรียนมาเพื่อโปรดทราบ"""

st.subheader("📋 ข้อความสำหรับส่ง LINE")
st.code(line_report_text, language="text")

col1, col2 = st.columns(2)

with col1:
    # ปุ่มกดส่งไลน์อัตโนมัติพร้อมแนบรูป
    if st.button("🚀 บันทึกข้อมูล & ส่งเข้ากลุ่ม LINE", type="primary"):
        with st.spinner("กำลังอัปโหลดรูปภาพและส่งข้อความเข้า LINE..."):
            image_urls = []
            folder_id = st.secrets["gdrive"]["folder_id"]
            
            if uploaded_files:
                for file in uploaded_files:
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{timestamp}_{file.name}"
                    url = upload_to_drive(file, filename, folder_id)
                    if url:
                        image_urls.append(url)
            
            # บันทึกข้อมูลลง Firestore
            try:
                db = get_firestore_db()
                db.collection("reports").add({
                    "report_date": report_date.strftime("%Y-%m-%d"),
                    "reporters": selected_personnel,
                    "task_detail": final_task_detail,
                    "images": image_urls,
                    "created_at": firestore.SERVER_TIMESTAMP
                })
            except Exception as e:
                st.error(f"เกิดข้อผิดพลาดในการบันทึกลงฐานข้อมูล: {e}")
            
            # ส่ง LINE Message
            success = send_line_message(line_report_text, image_urls)
            if success:
                st.success("ส่งรายงานและรูปภาพเข้ากลุ่ม LINE เรียบร้อยแล้ว!")
            else:
                st.error("เกิดข้อผิดพลาดในการส่งข้อความเข้ากลุ่ม LINE")

with col2:
    st.caption("สามารถคัดลอกชุดข้อความในกล่องด้านบนเพื่อส่งแมนนวลได้เช่นกันครับ")
