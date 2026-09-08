from datetime import datetime
import io
import json
import time
import urllib.parse
import cloudinary
import cloudinary.api
import cloudinary.uploader
from google.cloud import firestore
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

# ** ดึง LIFF ID จาก Secrets **
LIFF_ID = st.secrets.get("line", {}).get("liff_id", "2011360956-IXDp4ofU")

# --- 2. ส่ง Meta Tags สำหรับ LINE ---
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
    """
)

# --- 3. เชื่อมต่อ Cloudinary & Firestore ---
cloudinary.config(
    cloud_name=st.secrets["cloudinary"]["cloud_name"],
    api_key=st.secrets["cloudinary"]["api_key"],
    api_secret=st.secrets["cloudinary"]["api_secret"],
    secure=True,
)


@st.cache_resource
def get_firestore_client():
    cred_dict = dict(st.secrets["firebase"])
    if "private_key" in cred_dict:
        cred_dict["private_key"] = (
            cred_dict["private_key"].replace("\\n", "\n").strip()
        )

    creds = service_account.Credentials.from_service_account_info(cred_dict)
    db = firestore.Client(credentials=creds, project=cred_dict["project_id"])
    return db


db = get_firestore_client()


# --- 4. ฟังก์ชันบันทึกและดึงข้อมูลรายงานรายวัน (Daily Reports Database) ---
@st.cache_data(ttl=10)
def load_daily_report(date_key):
    """ดึงข้อมูลรายงานประจำวันที่บันทึกไว้ใน Firestore"""
    try:
        doc = db.collection("daily_reports").document(date_key).get()
        if doc.exists:
            return doc.to_dict()
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลรายงานประจำวันได้: {e}")
    return None


def save_daily_report(date_key, report_data):
    """บันทึกข้อมูลรายงานประจำลง Firestore"""
    try:
        report_data["updated_at"] = datetime.now()
        db.collection("daily_reports").document(date_key).set(
            report_data, merge=True
        )
        load_daily_report.clear()
        return True
    except Exception as e:
        st.error(f"❌ บันทึกข้อมูลรายงานไม่สำเร็จ: {e}")
        return False


# --- 5. ฟังก์ชันฝากรูปและคลังรูปภาพ ---
def upload_images_to_cloudinary(uploaded_files, folder_name="police_reports"):
    uploaded_urls = []
    for file in uploaded_files:
        try:
            response = cloudinary.uploader.upload(
                file, folder=folder_name, resource_type="image"
            )
            uploaded_urls.append(response.get("secure_url"))
        except Exception as e:
            st.error(f"❌ เกิดข้อผิดพลาดกับไฟล์ {file.name}: {e}")
    return uploaded_urls


@st.cache_data(ttl=60)
def get_cloudinary_images(folder_name="police_reports"):
    try:
        result = cloudinary.api.resources(
            type="upload", prefix=folder_name, max_results=100
        )
        images = []
        for resource in result.get("resources", []):
            images.append({
                "public_id": resource["public_id"],
                "url": resource["secure_url"],
                "created_at": resource["created_at"],
            })
        return images
    except Exception as e:
        st.error(f"❌ ไม่สามารถดึงข้อมูลคลังรูปภาพได้: {e}")
        return []


# --- 6. ฟังก์ชันส่งข้อความและรูปภาพ LINE OA (Push API) ---
def send_line_oa_push(message_text):
    try:
        line_secrets = st.secrets["line"]
        token = line_secrets["channel_access_token"]
        group_id = line_secrets["group_id"]

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        payload = {
            "to": group_id,
            "messages": [{"type": "text", "text": message_text}],
        }
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        return res.status_code == 200, res.text
    except Exception as e:
        return False, str(e)


def send_line_oa_images(image_urls):
    try:
        line_secrets = st.secrets["line"]
        token = line_secrets["channel_access_token"]
        group_id = line_secrets["group_id"]

        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        def chunk_list(lst, n=5):
            return [lst[i : i + n] for i in range(0, len(lst), n)]

        batches = chunk_list(image_urls, 5)
        success_count = 0

        for batch in batches:
            messages = [
                {
                    "type": "image",
                    "originalContentUrl": img_url,
                    "previewImageUrl": img_url,
                }
                for img_url in batch
            ]
            payload = {"to": group_id, "messages": messages}
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                success_count += len(batch)
            else:
                return False, f"HTTP {res.status_code}: {res.text}"

        return True, f"ส่งรูปภาพสำเร็จทั้งหมด {success_count} รูป"
    except Exception as e:
        return False, str(e)


# --- 7. Component ปุ่มส่งรูปภาพ ---
def render_liff_send_button(image_urls, key_suffix=""):
    if not image_urls:
        return

    def chunk_list(lst, n=5):
        return [lst[i : i + n] for i in range(0, len(lst), n)]

    batches = chunk_list(image_urls, 5)
    total_images = len(image_urls)
    total_batches = len(batches)

    st.markdown(
        f"#### 📤 การส่งรูปภาพทั้งหมด {total_images} รูป (แบ่งเป็น {total_batches} ชุด)"
    )

    if st.button(
        f"🚀 ส่งรูปภาพ {total_images} รูป เข้ากลุ่ม LINE ทันที (ผ่าน LINE OA)",
        key=f"{key_suffix}_btn_push_imgs",
        use_container_width=True,
    ):
        with st.spinner("📸 กำลังส่งรูปภาพเข้ากลุ่ม LINE..."):
            ok, msg = send_line_oa_images(image_urls)
            if ok:
                st.success(f"✅ {msg}")
            else:
                st.error(f"❌ ส่งรูปภาพไม่สำเร็จ: {msg}")

    st.markdown("**หรือเลือกส่งผ่านแอป LINE (LIFF):**")

    for idx, batch in enumerate(batches):
        start_idx = idx * 5 + 1
        end_idx = start_idx + len(batch) - 1

        encoded_urls = urllib.parse.quote(json.dumps(batch))
        target_liff_url = f"https://liff.line.me/{LIFF_ID}?imgs={encoded_urls}"

        st.link_button(
            f"🟢 ชุดที่ {idx+1}/{total_batches}: ส่งรูปที่ {start_idx} - {end_idx} ผ่าน LIFF",
            target_liff_url,
            use_container_width=True,
        )


def render_image_gallery_section(key_prefix="gallery"):
    st.markdown("### 🖼️ เลือกรูปภาพจากคลังเพื่อส่งเข้า LINE")

    with st.expander("📤 อัปโหลดรูปภาพใหม่เข้าคลังถาวร", expanded=False):
        uploaded_photos = st.file_uploader(
            "📂 เลือกรูปภาพ (เลือกพร้อมกันได้หลายรูป)",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key=f"{key_prefix}_uploader",
        )
        if uploaded_photos:
            if st.button(
                "📤 เริ่มอัปโหลดเข้าคลัง",
                key=f"{key_prefix}_btn_upload",
                use_container_width=True,
            ):
                with st.spinner("⏳ กำลังอัปโหลดรูปภาพ..."):
                    urls = upload_images_to_cloudinary(uploaded_photos)
                    if urls:
                        st.success(
                            f"✅ อัปโหลดรูปภาพสำเร็จจำนวน {len(urls)} รูป!"
                        )
                        get_cloudinary_images.clear()
                        time.sleep(1)
                        st.rerun()

    col_title, col_ref = st.columns([4, 1])
    with col_ref:
        if st.button("🔄 รีเฟรชรูป", key=f"{key_prefix}_refresh"):
            get_cloudinary_images.clear()
            st.rerun()

    images_list = get_cloudinary_images()
    if not images_list:
        st.info("ยังไม่มีรูปภาพในคลัง")
    else:
        st.markdown(
            """
            <style>
                .thumb-container img {
                    height: 110px !important;
                    object-fit: cover !important;
                    border-radius: 8px !important;
                    border: 1px solid #cbd5e1 !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        cols = st.columns(6)
        selected_urls = []

        for idx, img in enumerate(images_list):
            with cols[idx % 6]:
                st.markdown(
                    '<div class="thumb-container">', unsafe_allow_html=True
                )
                st.image(img["url"], use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                is_selected = st.checkbox(
                    f"☑️ รูปที่ {idx+1}", key=f"{key_prefix}_check_{idx}"
                )
                if is_selected:
                    selected_urls.append(img["url"])

        if selected_urls:
            st.markdown("---")
            st.markdown(
                f"**📌 เลือกไว้ทั้งหมดจำนวน {len(selected_urls)} รูป**"
            )
            render_liff_send_button(selected_urls, key_suffix=key_prefix)


# --- 8. จัดแต่ง CSS หน้าตาเว็บ ---
st.markdown(
    """
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

        .main-title { text-align: center; color: #0c2340; font-weight: bold; margin-bottom: 0; }
        .main-subtitle { text-align: center; color: #666666; font-size: 0.95rem; margin-bottom: 25px; }
        @media (prefers-color-scheme: dark) {
            .main-title { color: #ffffff; }
            .main-subtitle { color: #94a3b8; }
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<h2 class="main-title">👮‍♂️ ระบบรายงาน Line Group</h2>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="main-subtitle">งานสอบสวน สภ.ไม้แก่น (ระบบฐานข้อมูล NoSQL Cloud)</p>',
    unsafe_allow_html=True,
)


# --- 9. โหลดข้อมูลตำรวจและคลังภารกิจ ---
def get_rank_priority(rank_str):
    ranks_priority = {
        "พล.ต.อ.": 1,
        "พล.ต.ท.": 2,
        "พล.ต.ต.": 3,
        "พ.ต.อ.": 4,
        "พ.ต.ท.": 5,
        "พ.ต.ต.": 6,
        "ร.ต.อ.": 7,
        "ร.ต.ท.": 8,
        "ร.ต.ต.": 9,
        "ด.ต.": 10,
        "จ.ส.ต.": 11,
        "ส.ต.อ.": 12,
        "ส.ต.ท.": 13,
        "ส.ต.ต.": 14,
    }
    return ranks_priority.get(rank_str.strip(), 99)


@st.cache_data(ttl=300)
def load_personnel():
    docs = db.collection("personnel").stream()
    personnel = []
    for doc in docs:
        p_data = doc.to_dict()
        p_data["id"] = doc.id
        personnel.append(p_data)

    if not personnel:
        default_p = [
            {
                "rank": "พ.ต.ท.",
                "name": "ปฐมพงศ์ ศีรษะพล",
                "position": "สว.(สอบสวน) สภ.ไม้แก่น",
            },
            {
                "rank": "ร.ต.อ.",
                "name": "สมเจต ทองแผ่น",
                "position": "รอง สว.(สอบสวน) สภ.นาประดู่ ปรก.สภ.ไม้แก่น",
            },
            {
                "rank": "ร.ต.อ.",
                "name": "ตุลกร สุริยวงศ์",
                "position": "รอง สว.(สอบสวน) สภ.ไม้แก่น",
            },
            {
                "rank": "ด.ต.",
                "name": "ประสาน ปรงแก้ว",
                "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน",
            },
            {
                "rank": "จ.ส.ต.",
                "name": "อาลีฟ มะเก๊ะ",
                "position": "ผบ.หมู่(ป.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน",
            },
            {
                "rank": "ส.ต.ท.",
                "name": "ธนกฤต คงบุญช่วย",
                "position": "ผบ.หมู่(ผช.พงส.)สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน",
            },
            {
                "rank": "ส.ต.ต.",
                "name": "สุริยา บุญชูดวง",
                "position": "ผบ.หมู่(นปพ.) สภ.ไม้แก่น ปฏิบัติหน้าที่ งานสอบสวน",
            },
        ]
        for p in default_p:
            db.collection("personnel").add(p)

        docs = db.collection("personnel").stream()
        personnel = []
        for doc in docs:
            p_data = doc.to_dict()
            p_data["id"] = doc.id
            personnel.append(p_data)

    personnel.sort(key=lambda x: get_rank_priority(x["rank"]))
    return personnel


@st.cache_data(ttl=300)
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
            (
                "ได้รับมอบหมายจากพนักงานสอบสวน ยื่นคำร้องฝากขังต่อ ครั้งที่ 2,3"
                " และ 4 ต่อศาลจังหวัดปัตตานี"
            ),
            (
                "ได้ส่งสำนวนการสอบสวนคดียาเสพติด จำนวน 1 เรื่อง"
                " ที่พนักงานสอบสวนทำการสอบสวนเสร็จสิ้นแล้ว"
                " ไปยังพนักงานอัยการจังหวัดปัตตานี"
            ),
            (
                "ได้นำยาเสพติดของกลางในคดีอาญา ส่งตรวจพิสูจน์"
                " กลุ่มงานตรวจพิสูจน์ยาเสพติด พิสูจน์หลักฐานจังหวัดปัตตานี"
            ),
        ]
        for t in default_tasks:
            db.collection("tasks").add({"task_detail": t})

        docs = db.collection("tasks").stream()
        tasks = []
        for doc in docs:
            t_data = doc.to_dict()
            t_data["id"] = doc.id
            tasks.append(t_data)
    return tasks


personnel_list = load_personnel()
tasks_data = load_tasks()

officer_options = {}
for p in personnel_list:
    key_name = f"{p['rank']}{p['name']} ({p['position']})"
    officer_options[key_name] = p

allowed_inspector_ranks = [
    "พล.ต.อ.",
    "พล.ต.ท.",
    "พล.ต.ต.",
    "พ.ต.อ.",
    "พ.ต.ท.",
    "พ.ต.ต.",
    "ร.ต.อ.",
    "ร.ต.ท.",
    "ร.ต.ต.",
]
inspector_options = {}
for p in personnel_list:
    is_rank_ok = p["rank"].strip() in allowed_inspector_ranks
    is_not_deputy = "รอง ผกก" not in p["position"]
    if is_rank_ok and is_not_deputy:
        key_name = f"{p['rank']}{p['name']} ({p['position']})"
        inspector_options[key_name] = p

raw_tasks_list = [t["task_detail"] for t in tasks_data]

# --- 10. ระบบเลือกวันที่และดึงข้อมูลรายงานย้อนหลัง ---
st.markdown("##### 📅 เลือกวันที่สำหรับการรายงาน / ดูประวัติ")
date_input = st.date_input("เลือกวันที่", datetime.now(), key="global_date_input")
date_key = date_input.strftime("%Y-%m-%d")

months_th = [
    "ม.ค.",
    "ก.พ.",
    "มี.ค.",
    "เม.ย.",
    "พ.ค.",
    "มิ.ย.",
    "ก.ค.",
    "ส.ค.",
    "ก.ย.",
    "ต.ค.",
    "พ.ย.",
    "ธ.ค.",
]
year_th = str(date_input.year + 543)[2:]
date_str = f"{date_input.day} {months_th[date_input.month-1]}{year_th}"

# โหลดข้อมูลรายงานที่เคยบันทึกไว้ใน Firestore ตามวันที่เลือก
saved_report_data = load_daily_report(date_key)

if saved_report_data:
    st.success(
        f"📂 **พบประวัติข้อมูลรายงานประจำวันที่ {date_str} ในฐานข้อมูล**"
        f" (อัปเดตล่าสุด:"
        f" {saved_report_data.get('updated_at', datetime.now()).strftime('%H:%M น.')})"
    )
else:
    st.info(
        f"ℹ️ **ยังไม่มีข้อมูลบันทึกรายงานประจำวันที่ {date_str}**"
        " (สามารถพิมพ์ป้อนข้อมูล และกดปุ่มบันทึกได้ด้านล่าง)"
    )

st.markdown("---")

# --- 11. หน้าสร้าง/แสดงรายงาน LINE ---
tab1, tab2 = st.tabs([
    "📝 1. รายงานสรุปผลการปฏิบัติประจำวัน (แยกคน/เวลา/ภารกิจ)",
    "👮‍♂️ 2. รายงานรูปแบบเดิม (เดี่ยว/พร้อมพวก)",
])

with tab1:
    t2_col1, t2_col2 = st.columns([1.2, 1])

    with t2_col1:
        with st.container(border=True):
            st.markdown("### 🔍 เลือกร้อยเวรสอบสวนประจำวัน")

            saved_inspector = (
                saved_report_data.get("selected_inspector", "")
                if saved_report_data
                else ""
            )
            inspector_default_idx = 0
            if saved_inspector in list(inspector_options.keys()):
                inspector_default_idx = (
                    list(inspector_options.keys()).index(saved_inspector) + 1
                )

            selected_inspector = st.selectbox(
                "👮‍♂️ เลือกรายชื่อร้อยเวรสอบสวนปฏิบัติหน้าที่วันนี้",
                options=[""] + list(inspector_options.keys()),
                index=inspector_default_idx,
                key="t2_inspector_select",
            )

            inspector_text_block = ""
            if selected_inspector != "":
                ins_obj = inspector_options[selected_inspector]
                inspector_text_block = (
                    f"{ins_obj['rank']}{ins_obj['name']}\n{ins_obj['position']}\nปฏิบัติหน้าที่ร้อยเวรสอบสวน\n"
                )

            st.markdown("### 📝 รายการภารกิจผู้ปฏิบัติงาน")
            saved_nocases = (
                saved_report_data.get("no_cases", False)
                if saved_report_data
                else False
            )
            no_cases = st.checkbox(
                "❌ วันนี้ไม่มีประชาชนมาแจ้งความหรือลงบันทึกประจำวัน (เหตุการณ์ปกติ)",
                value=saved_nocases,
                key="t2_no_cases",
            )

            report_items_t2 = []

            if not no_cases:
                num_tasks_t2 = st.number_input(
                    "จำนวนภารกิจที่ต้องการสรุป (เรื่อง)",
                    min_value=1,
                    max_value=10,
                    value=1,
                    step=1,
                    key="t2_num_tasks",
                )

                for i in range(int(num_tasks_t2)):
                    st.markdown(f"**📍 รายการภารกิจที่ {i+1}**")

                    selected_officer_t2 = st.selectbox(
                        f"👮‍♂️ ผู้ปฏิบัติหลัก คนที่ {i+1}",
                        list(officer_options.keys()),
                        key=f"t2_off_{i}",
                    )
                    officer_t2 = officer_options[selected_officer_t2]

                    with_team_t2 = st.checkbox(
                        "➕ มีผู้ปฏิบัติร่วมในภารกิจนี้",
                        value=False,
                        key=f"t2_with_team_{i}",
                    )
                    team_member_lines_t2 = ""
                    has_team_names_t2 = False

                    if with_team_t2:
                        num_team_t2 = st.number_input(
                            f"จำนวนผู้ปฏิบัติร่วม (ภารกิจที่ {i+1})",
                            min_value=1,
                            max_value=10,
                            value=1,
                            step=1,
                            key="t2_num_team_idx_" + str(i),
                        )
                        for j in range(int(num_team_t2)):
                            team_select_t2 = st.selectbox(
                                f"👤 เลือกผู้ปฏิบัติร่วมคนที่ {j+1} (ภารกิจที่ {i+1})",
                                ["-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --"]
                                + list(officer_options.keys()),
                                key=f"t2_team_member_{i}_{j}",
                            )
                            if team_select_t2 != "-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --":
                                member_t2 = officer_options[team_select_t2]
                                team_member_lines_t2 += (
                                    f"\n{member_t2['rank']}{member_t2['name']}\n{member_t2['position']}"
                                )
                                has_team_names_t2 = True

                    suffix_t2 = ""
                    if with_team_t2:
                        suffix_t2 = " พร้อมด้วย" if has_team_names_t2 else " พร้อมพวก"

                    time_input_t2 = st.text_input(
                        f"⏰ เวลาภารกิจที่ {i+1} (น.)",
                        value="08.30",
                        key=f"t2_time_{i}",
                    )

                    st.markdown(
                        "🔍 **ค้นหาภารกิจจากคลัง หรือพิมพ์เรื่องใหม่ลงไปได้เลย**"
                    )

                    task_detail_t2 = st.selectbox(
                        f"พิมพ์ค้นหา หรือเลือกภารกิจที่ {i+1}",
                        options=[""] + raw_tasks_list,
                        key=f"t2_mixed_select_{i}",
                    )

                    is_custom = st.checkbox(
                        "✍️ พิมพ์เรื่องใหม่ (กรณีไม่มีในตัวเลือกด้านบน)",
                        value=False,
                        key=f"t2_custom_check_{i}",
                    )

                    if is_custom:
                        task_detail_t2 = st.text_input(
                            f"✏️ พิมพ์รายละเอียดภารกิจใหม่ที่ {i+1}",
                            value="",
                            key=f"t2_custom_write_{i}",
                        )

                        if task_detail_t2.strip():
                            if st.button(
                                "💾 บันทึกภารกิจนี้เข้าคลังถาวร", key=f"inline_save_btn_{i}"
                            ):
                                new_text = task_detail_t2.strip()
                                if new_text not in raw_tasks_list:
                                    db.collection("tasks").add({"task_detail": new_text})
                                    load_tasks.clear()
                                    st.toast(
                                        "🎉 บันทึกภารกิจเรื่องใหม่เข้าคลังสำเร็จ!", icon="💾"
                                    )
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.warning(
                                        "⚠️ ภารกิจนี้มีอยู่ในระบบคลังเดิมอยู่แล้ว"
                                    )

                    if task_detail_t2:
                        item_text = (
                            f"{i+1}. เวลา {time_input_t2}"
                            f" น.\n{officer_t2['rank']}{officer_t2['name']}\n{officer_t2['position']}{suffix_t2}{team_member_lines_t2}\n{task_detail_t2}"
                        )
                        report_items_t2.append(item_text)

                    st.divider()

    with t2_col2:
        with st.container(border=True):
            st.markdown("### 📋 ข้อความสรุปรวม Line")

            # ถ้ามีข้อมูลที่เคยบันทึกไว้ และข้อความสร้างใหม่ว่าง ให้ดึงข้อความเก่ามาโชว์
            if no_cases:
                final_text_t2 = (
                    f"สภ.ไม้แก่น \nงานสอบสวน\nเรียนผู้บังคับบัญชา\nรายงานสรุปผลการปฏิบัติประจำวันที่"
                    f" {date_str}\n{inspector_text_block}ไม่มีประชาชนมาแจ้งความหรือลงบันทึกประจำวันแต่อย่างใด\nเหตุการณ์ทั่วไปปกติ\n\nจึงเรียนมาเพื่อโปรดทราบ"
                )
            else:
                joined_items_t2 = "\n".join(report_items_t2)
                final_text_t2 = (
                    f"สภ.ไม้แก่น \nงานสอบสวน\nเรียนผู้บังคับบัญชา\nรายงานสรุปผลการปฏิบัติประจำวันที่"
                    f" {date_str}\n{inspector_text_block}{joined_items_t2}\n\nจึงเรียนมาเพื่อโปรดทราบ"
                )

            if saved_report_data and "report_text_tab1" in saved_report_data and not report_items_t2 and not no_cases:
                final_text_t2 = saved_report_data["report_text_tab1"]

            st.code(final_text_t2, language="text")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("💾 บันทึกข้อมูลลงฐานข้อมูล", key="btn_save_db_t1"):
                    data_to_save = {
                        "date_key": date_key,
                        "date_str": date_str,
                        "selected_inspector": selected_inspector,
                        "no_cases": no_cases,
                        "report_text_tab1": final_text_t2,
                    }
                    if save_daily_report(date_key, data_to_save):
                        st.toast(
                            f"✅ บันทึกรายงานประจำวันที่ {date_str} ลงฐานข้อมูลเรียบร้อยแล้ว!",
                            icon="💾",
                        )
                        time.sleep(1)
                        st.rerun()

            with col_btn2:
                if st.button(
                    "🚀 ส่ง LINE + บันทึกข้อมูล", key="btn_send_line_t1"
                ):
                    with st.spinner("กำลังส่งรายงานเข้ากลุ่ม LINE..."):
                        success, err_msg = send_line_oa_push(final_text_t2)
                        if success:
                            data_to_save = {
                                "date_key": date_key,
                                "date_str": date_str,
                                "selected_inspector": selected_inspector,
                                "no_cases": no_cases,
                                "report_text_tab1": final_text_t2,
                            }
                            save_daily_report(date_key, data_to_save)
                            st.success(
                                "✅ ส่งรายงานเข้ากลุ่ม LINE และบันทึกลงฐานข้อมูลเรียบร้อย!"
                            )
                        else:
                            st.error(f"❌ ส่งข้อความไม่สำเร็จ: {err_msg}")

    st.markdown("---")
    render_image_gallery_section(key_prefix="tab1_gallery")

with tab2:
    main_col1, main_col2, main_col3 = st.columns([1, 1, 1.1])

    with main_col1:
        with st.container(border=True):
            st.markdown("### ⏱️ เวลาภารกิจ")
            current_time_str = datetime.now().strftime("%H.%M")
            time_str = st.text_input(
                "⏰ กรอกเวลา (น.)", value=current_time_str, key="t1_time_str"
            )

            st.markdown("### 👤 เจ้าหน้าที่ผู้ปฏิบัติงาน")
            main_officer_select = st.selectbox(
                "👮‍♂️ เลือกผู้ปฏิบัติหลัก (คนแรก)",
                list(officer_options.keys()),
                key="t1_main_officer",
            )
            main_officer = officer_options[main_officer_select]

            with_team = st.checkbox(
                "➕ มีผู้ปฏิบัติร่วม (พร้อมพวก/พร้อมด้วย)",
                value=False,
                key="t1_with_team",
            )
            team_member_lines = ""
            has_team_names = False

            if with_team:
                num_team = st.number_input(
                    "จำนวนผู้ปฏิบัติร่วม (คน)",
                    min_value=1,
                    max_value=10,
                    value=1,
                    step=1,
                    key="t1_num_team",
                )
                for i in range(int(num_team)):
                    team_select = st.selectbox(
                        f"👤 เลือกผู้ปฏิบัติร่วมคนที่ {i+1}",
                        ["-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --"]
                        + list(officer_options.keys()),
                        key=f"t1_team_{i}",
                    )
                    if team_select != "-- ไม่ระบุชื่อ (ใช้พร้อมพวก) --":
                        member = officer_options[team_select]
                        team_member_lines += (
                            f"\n{member['rank']}{member['name']}\n{member['position']}"
                        )
                        has_team_names = True

            suffix = ""
            if with_team:
                suffix = " พร้อมด้วย" if has_team_names else " พร้อมพวก"

    with main_col2:
        with st.container(border=True):
            st.markdown("### 📝 รายละเอียดภารกิจ")
            num_tasks = st.number_input(
                "📌 จำนวนภารกิจที่ต้องการรายงาน (เรื่อง)",
                min_value=1,
                max_value=5,
                value=1,
                step=1,
                key="t1_num_tasks",
            )

            all_task_details = []
            for idx in range(int(num_tasks)):
                st.markdown(f"**📍 ภารกิจเรื่องที่ {idx+1}**")
                selected_task = st.selectbox(
                    f"เลือกหรือค้นหาข้อความภารกิจที่ {idx+1}",
                    [""] + raw_tasks_list,
                    key=f"t1_select_{idx}",
                )
                if selected_task:
                    processed_task = selected_task
                    if processed_task.startswith("ได้นำ"):
                        processed_task = processed_task.replace("ได้นำ", "นำ", 1)
                    all_task_details.append(processed_task)

            final_tasks_text = ""
            valid_tasks = [task for task in all_task_details if task]

            if len(valid_tasks) == 1:
                final_tasks_text = valid_tasks[0]
            elif len(valid_tasks) > 1:
                final_tasks_text = "\n".join([f"- {task}" for task in valid_tasks])

    with main_col3:
        with st.container(border=True):
            st.markdown("### 📋 ข้อความรายงานสำหรับส่ง Line")

            report_text = (
                f"สภ.ไม้แก่น \nงานสอบสวน\nเรียน ผู้บังคับบัญชา\nเมื่อ {date_str} เวลาประมาณ {time_str} น.\n"
                f"{main_officer['rank']}{main_officer['name']}\n{main_officer['position']}{suffix}{team_member_lines}\n"
                f"{final_tasks_text}\nจึงเรียนมาเพื่อโปรดทราบ"
            )

            if saved_report_data and "report_text_tab2" in saved_report_data and not valid_tasks:
                report_text = saved_report_data["report_text_tab2"]

            st.code(report_text, language="text")

            col_btn3, col_btn4 = st.columns(2)
            with col_btn3:
                if st.button("💾 บันทึกข้อมูลลงฐานข้อมูล", key="btn_save_db_t2"):
                    data_to_save = {
                        "date_key": date_key,
                        "date_str": date_str,
                        "report_text_tab2": report_text,
                    }
                    if save_daily_report(date_key, data_to_save):
                        st.toast(
                            f"✅ บันทึกรายงานประจำวันที่ {date_str} ลงฐานข้อมูลเรียบร้อยแล้ว!",
                            icon="💾",
                        )
                        time.sleep(1)
                        st.rerun()

            with col_btn4:
                if st.button(
                    "🚀 ส่ง LINE + บันทึกข้อมูล", key="btn_send_line_t2"
                ):
                    with st.spinner("กำลังส่งรายงานเข้ากลุ่ม LINE..."):
                        success, err_msg = send_line_oa_push(report_text)
                        if success:
                            data_to_save = {
                                "date_key": date_key,
                                "date_str": date_str,
                                "report_text_tab2": report_text,
                            }
                            save_daily_report(date_key, data_to_save)
                            st.success(
                                "✅ ส่งรายงานเข้ากลุ่ม LINE และบันทึกลงฐานข้อมูลเรียบร้อย!"
                            )
                        else:
                            st.error(f"❌ ส่งข้อความไม่สำเร็จ: {err_msg}")

    st.markdown("---")
    render_image_gallery_section(key_prefix="tab2_gallery")
