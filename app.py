from datetime import datetime
import io
import time
import urllib.parse
from google.cloud import firestore
from google.cloud import storage as gcs
from google.oauth2 import service_account
import requests
import streamlit as st

# --- 1. ตั้งค่าหน้าจอ ---
st.set_page_config(
    page_title="รายงานสอบสวน สภ.ไม้แก่น",
    page_icon="👮‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- 2. ซ่อน Header/Footer และ Meta Tags ---
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    </style>
""",
    unsafe_allow_html=True,
)


# --- 3. เชื่อมต่อฐานข้อมูล Firebase Firestore & Storage ---
@st.cache_resource
def get_firebase_clients():
    cred_dict = dict(st.secrets["firebase"])
    if "private_key" in cred_dict:
        cred_dict["private_key"] = (
            cred_dict["private_key"].replace("\\n", "\n").strip()
        )

    creds = service_account.Credentials.from_service_account_info(cred_dict)
    db = firestore.Client(credentials=creds, project=cred_dict["project_id"])
    return db, creds, cred_dict["project_id"]


db, creds, project_id = get_firebase_clients()


# ฟังก์ชันอัปโหลดรูปภาพขึ้น Firebase Storage เพื่อขอ Public URL สำหรับ LINE API
def upload_image_to_storage(uploaded_file):
    try:
        bucket_name = st.secrets["firebase"].get(
            "storage_bucket", f"{project_id}.appspot.com"
        )
        storage_client = gcs.Client(credentials=creds, project=project_id)
        bucket = storage_client.bucket(bucket_name)

        # ตั้งชื่อไฟล์ใหม่ป้องกันชื่อซ้ำ
        file_name = (
            f"reports/{int(time.time())}_{uploaded_file.name.replace(' ', '_')}"
        )
        blob = bucket.blob(file_name)

        # อัปโหลดไฟล์
        blob.upload_from_file(uploaded_file, content_type=uploaded_file.type)

        # กำหนดให้ไฟล์เป็น Public URL
        blob.make_public()
        return blob.public_url
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการอัปโหลดรูปภาพ: {e}")
        return None


# --- 4. ฟังก์ชันส่งข้อความ + รูปภาพ ผ่าน LINE Messaging API ---
def send_line_oa_push(message_text, image_urls=[]):
    try:
        line_secrets = st.secrets["line"]
        token = line_secrets["channel_access_token"]
        group_id = line_secrets["group_id"]

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # โครงสร้างข้อความ LINE API (สูงสุด 5 objects ต่อ 1 การส่ง)
        messages = [{"type": "text", "text": message_text}]

        # เพิ่มรูปภาพ (จำกัดไม่เกิน 4 ภาพ เพื่อรวมกับข้อความแล้วไม่เกิน 5)
        for img_url in image_urls[:4]:
            messages.append(
                {
                    "type": "image",
                    "originalContentUrl": img_url,
                    "previewImageUrl": img_url,
                }
            )

        payload = {"to": group_id, "messages": messages}
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)


# --- 5. ฟังก์ชันย่อยสำหรับจัดการข้อมูลใน Firestore ---
def get_daily_reports(date_str):
    doc_ref = db.collection("reports").document(date_str)
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return {"inspectors": "", "cases": []}


def save_daily_reports(date_str, data):
    doc_ref = db.collection("reports").document(date_str)
    doc_ref.set(data)


# --- 6. ส่วน UI หลักของแอปพลิเคชัน ---
st.title("👮‍♂️ ระบบสรุปรายงานประจำวัน งานสอบสวน สภ.ไม้แก่น")

# เลือกวันที่รายงาน
selected_date = st.date_input("🗓️ เลือกวันที่รายงาน", datetime.now().date())
date_str = selected_date.strftime("%Y-%m-%d")

# ดึงข้อมูลของวันที่เลือก
report_data = get_daily_reports(date_str)

# Tabs แบ่งการทำงาน
tab1, tab2 = st.tabs(["📝 บันทึก/แก้ไขข้อมูลประจำวัน", "📤 ส่งรายงานเข้า LINE"])

# ----------------------------------------------------
# TAB 1: บันทึกและจัดการคดี
# ----------------------------------------------------
with tab1:
    st.subheader(f"จัดการข้อมูลประจำวันที่ {date_str}")

    # ส่วนข้อมูลพนักงานสอบสวนเวร
    inspectors_input = st.text_input(
        "พนักงานสอบสวนเวร / รอง สว.(สอบสวน)",
        value=report_data.get("inspectors", ""),
        placeholder="เช่น พ.ต.ต.สมชาย เข็มกลัด พงส.เวร",
    )

    st.markdown("---")
    st.markdown("### รายการคดี / บันทึกประจำวัน")

    cases = report_data.get("cases", [])

    # ฟอร์มเพิ่มคดีใหม่
    with st.expander("➕ เพิ่มรายการคดี / บันทึกประจำวันใหม่", expanded=True):
        with st.form("add_case_form", clear_on_submit=True):
            col_a, col_b = st.columns([1, 2])
            case_no = col_a.text_input("เลขคดี / เลข ปจว.", placeholder="1/2567")
            case_detail = col_b.text_area(
                "รายละเอียดคดี / รายงานเหตุ",
                placeholder="ระบุข้อเท็จจริง คดี หรือเหตุการณ์...",
            )

            submitted = st.form_submit_button("💾 บันทึกรายการ")
            if submitted:
                if case_no and case_detail:
                    cases.append({"no": case_no, "detail": case_detail})
                    report_data["inspectors"] = inspectors_input
                    report_data["cases"] = cases
                    save_daily_reports(date_str, report_data)
                    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")
                    st.rerun()
                else:
                    st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")

    # แสดงรายการคดีที่มีอยู่เดิมพร้อมปุ่มลบ
    if cases:
        st.markdown("#### รายการที่บันทึกแล้ว:")
        for idx, item in enumerate(cases):
            c1, c2, c3 = st.columns([2, 6, 1])
            c1.write(f"**ลำดับ {idx+1}:** {item['no']}")
            c2.write(item["detail"])
            if c3.button("🗑️ ลบ", key=f"del_{idx}"):
                cases.pop(idx)
                report_data["inspectors"] = inspectors_input
                report_data["cases"] = cases
                save_daily_reports(date_str, report_data)
                st.rerun()

    # ปุ่มบันทึกข้อมูลเจ้าหน้าที่เวร
    if st.button("💾 บันทึกชื่อพนักงานสอบสวนเวร"):
        report_data["inspectors"] = inspectors_input
        report_data["cases"] = cases
        save_daily_reports(date_str, report_data)
        st.success("อัปเดตชื่อพนักงานสอบสวนเวรสำเร็จ")

# ----------------------------------------------------
# TAB 2: ตรวจสอบสรุปรายงาน และส่งเข้า LINE
# ----------------------------------------------------
with tab2:
    st.subheader("ตรวจสอบรายงานและส่งออก")

    t2_col1, t2_col2 = st.columns([1, 1])

    # เตรียมข้อความสรุป
    inspectors_str = report_data.get("inspectors", "")
    cases_list = report_data.get("cases", [])

    inspector_text_block = (
        f"พนักงานสอบสวนเวร: {inspectors_str}\n" if inspectors_str else ""
    )

    report_items = []
    for idx, c in enumerate(cases_list, 1):
        report_items.append(f"{idx}. คดี/ปจว. เลขที่ {c['no']} - {c['detail']}")

    no_cases = len(cases_list) == 0

    if no_cases:
        final_report_text = (
            f"สภ.ไม้แก่น\nงานสอบสวน\nเรียนผู้บังคับบัญชา\n"
            f"รายงานสรุปผลการปฏิบัติประจำวันที่ {date_str}\n"
            f"{inspector_text_block}"
            f"ไม่มีประชาชนมาแจ้งความหรือลงบันทึกประจำวันแต่อย่างใด\n"
            f"เหตุการณ์ทั่วไปปกติ\n\nจึงเรียนมาเพื่อโปรดทราบ"
        )
    else:
        joined_items = "\n".join(report_items)
        final_report_text = (
            f"สภ.ไม้แก่น\nงานสอบสวน\nเรียนผู้บังคับบัญชา\n"
            f"รายงานสรุปผลการปฏิบัติประจำวันที่ {date_str}\n"
            f"{inspector_text_block}{joined_items}\n\nจึงเรียนมาเพื่อโปรดทราบ"
        )

    with t2_col1:
        st.markdown("### 📄 พรีวิวข้อความที่จะส่ง")
        st.info(final_report_text)

    with t2_col2:
        with st.container(border=True):
            st.markdown("### 📤 ส่งรายงานเข้ากลุ่ม LINE")

            # แสดงโค้ดข้อความสรุปสำหรับ คัดลอก
            st.code(final_report_text, language="text")

            # --- ส่วนอัปโหลดรูปภาพประกอบรายงาน ---
            st.markdown("#### 🖼️ แนบรูปภาพประกอบรายงาน (สูงสุด 4 ภาพ)")
            uploaded_images = st.file_uploader(
                "เลือกรูปภาพรายงาน",
                type=["png", "jpg", "jpeg"],
                accept_multiple_files=True,
                key="uploader_line_images",
            )

            # พรีวิวรูปภาพก่อนส่ง
            if uploaded_images:
                st.markdown("**พรีวิวภาพที่เลือก:**")
                preview_cols = st.columns(min(len(uploaded_images), 4))
                for idx, img_file in enumerate(uploaded_images[:4]):
                    preview_cols[idx].image(
                        img_file,
                        caption=f"ภาพที่ {idx+1}",
                        use_container_width=True,
                    )

                if len(uploaded_images) > 4:
                    st.warning(
                        "⚠️ LINE API รองรับการส่งภาพพร้อมข้อความสูงสุดครั้งละ 4 ภาพ (ระบบจะส่งเฉพาะ 4 ภาพแรก)"
                    )

            # --- ปุ่มที่ 1: ส่งผ่าน LINE OA Push Message (ส่งข้อความ + รูปภาพ) ---
            if st.button(
                "🚀 ส่งรายงาน + รูปภาพ เข้ากลุ่ม LINE ทันที (LINE OA)",
                key="btn_send_line_oa",
                type="primary",
            ):
                with st.spinner(
                    "กำลังอัปโหลดรูปภาพและส่งรายงานเข้ากลุ่ม LINE..."
                ):
                    image_urls = []

                    # 1. อัปโหลดรูปภาพเข้า Firebase Storage ก่อนส่ง
                    if uploaded_images:
                        for img in uploaded_images[:4]:
                            url = upload_image_to_storage(img)
                            if url:
                                image_urls.append(url)

                    # 2. ยิง API เข้า LINE Messaging Push
                    success, err_msg = send_line_oa_push(
                        final_report_text, image_urls
                    )

                    if success:
                        st.success(
                            "✅ ส่งรายงานพร้อมรูปภาพเข้ากลุ่ม LINE เรียบร้อยแล้ว!"
                        )
                    else:
                        st.error(f"❌ ส่งไม่สำเร็จ: {err_msg}")

            st.markdown("---")

            # --- ปุ่มที่ 2: ปุ่มแชร์ผ่าน LINE Client (ส่งเฉพาะข้อความแบบเลือกห้องแชทเอง) ---
            encoded_text = urllib.parse.quote(final_report_text)
            line_share_url = f"https://line.me/R/share?text={encoded_text}"

            st.markdown(
                f"""
                <a href="{line_share_url}" target="_blank" style="text-decoration: none;">
                    <div style="
                        background-color: #06C755;
                        color: white;
                        text-align: center;
                        padding: 10px;
                        border-radius: 10px;
                        font-weight: bold;
                        font-size: 15px;
                        cursor: pointer;">
                        🟢 เลือกแชท/กลุ่ม เพื่อส่งเฉพาะข้อความ (LINE Share Target Picker)
                    </div>
                </a>
                """,
                unsafe_allow_html=True,
            )
