import streamlit as st
import time
import streamlit as st
import time
import requests 
import json 
import pandas as pd # อย่าลืมบรรทัดนี้ ต้องใช้จัดการตารางบัญชีครับ
from streamlit_gsheets import GSheetsConnection

# ... (import อื่นๆ เดิม) ...

# ---------------------------------------------------------
# 0. Session Setup (เพิ่มตัวแปรเช็คสถานะล็อกอิน)
# ---------------------------------------------------------
if 'is_logged_in' not in st.session_state: st.session_state.is_logged_in = False
if 'current_user' not in st.session_state: st.session_state.current_user = None

from datetime import datetime
# (ถ้าพี่มี import อื่นๆ ให้คงไว้เหมือนเดิมครับ)

# --- ฟังก์ชันส่งเข้า Discord ---
def send_discord_notify(webhook_url, message, image_file=None):
    try:
        data = {
            "content": message,
            "username": "Beer Crepe Bot" 
        }
        
        files = None
        if image_file:
            image_file.seek(0)
            files = {
                "file": (image_file.name, image_file.getvalue())
            }

        if files:
             requests.post(webhook_url, data=data, files=files)
        else:
             requests.post(webhook_url, json=data)
             
        return True
    except Exception as e:
        print(f"Discord Error: {e}")
        return False
# ---------------------------------------------------------
# 1. ตั้งค่าหน้าเว็บและ CSS
# ---------------------------------------------------------
st.set_page_config(page_title="Beer Crepe", layout="wide", initial_sidebar_state="expanded")

# Custom CSS

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Prompt', sans-serif;
    }

    .stApp {
        background-color: #f4f4f8;
    }
    
    footer {visibility: hidden;}
    
    /* --- HERO BANNER BUTTON (ปุ่มรูปภาพหน้าหลัก) --- */
    .hero-container button {
        background-image: url("https://images.unsplash.com/photo-1484723091739-30a097e8f929?auto=format&fit=crop&w=1200&q=80");
        background-size: cover;
        background-position: center;
        height: 180px; 
        width: 100%;
        border: none;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        color: transparent; 
        transition: transform 0.2s;
    }
    
    .hero-container button:hover {
        transform: scale(1.02); 
        border: 2px solid #e67e22; 
    }

    .hero-container button:active {
        background-color: transparent; 
    }

    /* --- MENU CARD STYLE (ปรับปรุงใหม่ให้รูปพอดีเป๊ะ) --- */
    .menu-img {
        width: 100%;
        /* 🔴 เปลี่ยนจาก height: 150px เป็น aspect-ratio: 1/1 (จัตุรัส) */
        aspect-ratio: 1 / 1;
        object-fit: cover; /* เอารูปมาวางให้เต็มพื้นที่โดยไม่เสียสัดส่วน */
        border-top-left-radius: 15px;
        border-top-right-radius: 15px;
        margin-bottom: -6px; /* ดึงขอบล่างให้ชิดปุ่ม */
        display: block;
    }

    /* สไตล์ปุ่มกดเลือกเมนู */
    div.stButton > button {
        background-color: #ffffff;
        color: #2c3e50;
        border: 1px solid #ddd;
        border-top: none; 
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
        border-top-left-radius: 0;
        border-top-right-radius: 0;
        padding: 10px;
        width: 100%;
        height: auto;
        min-height: 70px; /* เพิ่มความสูงปุ่มนิดหน่อยให้รับกับรูป */
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: 0.2s;
        text-align: left;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        justify-content: center;
    }
    
    div.stButton > button:hover {
        background-color: #fff8e1; 
        border-color: #ffb74d;
        transform: translateY(-2px);
    }
    
    div.stButton > button p {
        font-size: 16px !important;
        font-weight: 600;
        margin: 0;
        line-height: 1.4;
    }
    
    [data-testid="stSidebar"] button {
        border-radius: 5px !important;
        border: none !important;
        text-align: center !important;
        align-items: center !important;
        box-shadow: none !important;
    }
    # ---------------------------------------------------------
    # 1. ตั้งค่าหน้าเว็บและ CSS
    # ---------------------------------------------------------
    st.set_page_config(
    page_title="Beer Crepe", 
    page_icon="logo.png",  # 🟢 เพิ่มบรรทัดนี้ครับ (ใช้รูปเดียวกับโลโก้ร้าน)
    layout="wide", 
    initial_sidebar_state="expanded"
    )

    /* เปลี่ยนสีตัวหนังสือของ Checkbox และ Form */
    div[data-testid="stCheckbox"] label p {
        color: #2c3e50 !important; 
        font-weight: 500;
        font-size: 16px;
    }
    .stMarkdown h4 { color: #d35400 !important; }
    div[data-testid="stTextInput"] label p {
        color: #2c3e50 !important;
        font-weight: bold;
    }
    
    /* เพิ่ม: เปลี่ยนสี Radio Button (วิธีจ่ายเงิน) ให้เข้มด้วย */
    div[data-testid="stRadio"] label p {
        color: #2c3e50 !important;
        font-weight: 500;
        
    }
    /* สไตล์เพิ่มเติมเพื่อให้ปุ่มโปรโมชั่นติดกับรูปภาพ */
    [data-testid="stVerticalBlock"] > div:has(button[key="promo_btn_fixed"]) {
        gap: 0px;
    }

    /* สั่งให้ปุ่มที่มี Key พิเศษนี้ไม่มีระยะห่างด้านบน */
    /* --- หาบล็อกนี้ แล้วแก้ตัวเลขตามนี้ครับ --- */
    
    /* สั่งให้ปุ่มที่มี Key พิเศษนี้ไม่มีระยะห่างด้านบน */
    div.stButton > button[key="promo_btn_fixed"] {
        /* 🔴 แก้จาก -16px เป็น -22px (ปรับเพิ่มลดได้ถ้ายังไม่สนิท) */
        margin-top: -22px !important; 
        border-top: none !important;
        border-top-left-radius: 0px !important;
        border-top-right-radius: 0px !important;
        /* เพิ่ม z-index เพื่อให้มั่นใจว่าขอบปุ่มจะทับขอบรูป */
        position: relative;
        z-index: 2;
    }
        
    }
    

</style>
""", unsafe_allow_html=True)
# ==========================================
# 🟢 ฟังก์ชันหน้า Admin (ปรับสีใหม่ตามสั่ง 🎨)
# ==========================================
def admin_page():
    # --- 1. CSS พิเศษสำหรับเปลี่ยนสี Tabs ---
    st.markdown("""
    <style>
        /* เปลี่ยนขนาดและสีตัวหนังสือใน Tab ปกติ */
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.1rem;
            color: #555555; /* สีเทาเข้ม */
        }
        
        /* เปลี่ยนสี Tab ตอนที่ถูกกดเลือก (Active) */
        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
            color: #d35400 !important; /* สีส้ม */
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. ส่วนหัวข้อและชื่อผู้ใช้งาน ---
    st.markdown(f"<h1 style='color:#d35400; margin-bottom:0px;'>👮‍♂️ ระบบหลังบ้าน (Staff Only)</h1>", unsafe_allow_html=True)
    
    # ปรับสีบรรทัด "ผู้ใช้งาน" (Admin เป็นสีส้ม)
    st.markdown(f"""
    <div style='background-color: #fff8e1; padding: 8px 15px; border-radius: 8px; border: 1px solid #ffe0b2; display: inline-block; margin-bottom: 20px;'>
        <span style='color:#555; font-size:1rem;'>👤 ผู้ใช้งาน: </span>
        <b style='color:#d35400; font-size:1.1rem;'>{st.session_state.current_user}</b>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["💰 บัญชีรายรับ-รายจ่าย", "🧾 ประวัติออเดอร์ (Real-time)"])
    
    # --- TAB 1: บัญชี (Accounting) ---
    with tab1:
        st.markdown("<h3 style='color:#2c3e50;'>📝 บันทึกรายการใหม่</h3>", unsafe_allow_html=True)
        
        with st.form("accounting_form"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<b style='color:#d35400;'>ประเภทรายการ</b>", unsafe_allow_html=True)
                acc_type = st.selectbox("เลือกประเภท", ["รายรับ (Income)", "รายจ่าย (Expense)"], label_visibility="collapsed")
            with col2:
                st.markdown("<b style='color:#d35400;'>จำนวนเงิน (บาท)</b>", unsafe_allow_html=True)
                amount = st.number_input("ระบุเงิน", min_value=0.0, step=1.0, label_visibility="collapsed")
            
            st.markdown("<b style='color:#d35400;'>รายละเอียด (Commit Message) *จำเป็น</b>", unsafe_allow_html=True)
            reason = st.text_input("เหตุผล", placeholder="เช่น ซื้อแป้งเพิ่ม, ลูกค้าให้ทิป", label_visibility="collapsed")
            
            st.write("") 
            submit_acc = st.form_submit_button("💾 บันทึกรายการ (Commit)", type="primary", use_container_width=True)
            
            if submit_acc:
                if not reason:
                    st.error("❌ กรุณาระบุรายละเอียด (Commit Message) ด้วยครับ")
                else:
                    try:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        new_data = pd.DataFrame([{
                            "Timestamp": timestamp,
                            "Type": acc_type,
                            "Amount": amount,
                            "Reason": reason,
                            "User": st.session_state.current_user
                        }])
                        
                        try:
                            existing = conn.read(worksheet="Accounting", ttl=0)
                            updated = pd.concat([existing, new_data], ignore_index=True)
                        except:
                            updated = new_data
                            
                        conn.update(worksheet="Accounting", data=updated)
                        st.success("✅ บันทึกเรียบร้อย!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"บันทึกไม่สำเร็จ: {e}")

        st.markdown("---")
        st.markdown("<h3 style='color:#2c3e50;'>📊 รายการล่าสุด</h3>", unsafe_allow_html=True)
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            df_acc = conn.read(worksheet="Accounting", ttl=0)
            st.dataframe(df_acc.tail(10), use_container_width=True)
        except:
            st.info("ยังไม่มีข้อมูลบัญชี")
            
    # --- TAB 2: ดูออเดอร์ (Order History) ---
    with tab2:
        c_head1, c_head2 = st.columns([3, 1])
        with c_head1:
            st.markdown("<h3 style='color:#2c3e50;'>🧾 ออเดอร์ที่ลูกค้าสั่งเข้ามา</h3>", unsafe_allow_html=True)
        with c_head2:
            if st.button("🔄 รีเฟรช", use_container_width=True, key="refresh_admin_orders"): 
                 st.rerun()
        
        try:
            conn = st.connection("gsheets", type=GSheetsConnection)
            
            # 👇👇 จุดสำคัญที่แก้: ระบุ worksheet="Order" 👇👇
            df_orders = conn.read(worksheet="Order", ttl=0)
            # 👆👆 ------------------------------------- 👆👆

            # เช็คว่ามีข้อมูลไหม
            if df_orders.empty:
                st.info("ยังไม่มีออเดอร์เข้ามาครับ")
            else:
                # แสดงตารางรวม
                st.dataframe(df_orders, use_container_width=True)
            
                st.write("---")
                st.markdown("<b style='color:#d35400;'>รายการล่าสุด (Card View):</b>", unsafe_allow_html=True)
                
                # วนลูปแสดงการ์ด (กลับลำดับเอาล่าสุดขึ้นก่อน)
                for index, row in df_orders.tail(5).iloc[::-1].iterrows(): 
                    st.markdown(f"""
                    <div style="
                        background-color: white; padding: 15px; border-radius: 10px; margin-bottom: 10px;
                        border-left: 5px solid #e67e22; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    ">
                        <div style="font-weight:bold; color:#2c3e50; font-size:1.1em;">
                            🛒 {row.get('Items', '-')}
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-top:5px; color:#555;">
                            <span>🕒 {row.get('Timestamp', '-')}</span>
                            <span style="font-weight:bold; color:#c0392b;">฿{row.get('Total', '0')}</span>
                        </div>
                        <div style="font-size:0.9em; color:#7f8c8d;">
                            💳 {row.get('Payment', '-')} | 📝 {row.get('Note', '-')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"อ่านข้อมูลไม่ได้: {e}")
            st.info("💡 คำแนะนำ: ลองเช็คว่าใน Google Sheet ชื่อแท็บข้างล่างเขียนว่า 'Order' (ตัว O ใหญ่) ตรงกันเป๊ะหรือไม่")

# ---------------------------------------------------------
# 2. ข้อมูล (Mock Data)
# ---------------------------------------------------------
if 'cart' not in st.session_state: st.session_state.cart = []
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'selected_item' not in st.session_state: st.session_state.selected_item = None

# ใช้รูปจาก Discord ตามที่คุณส่งมา
menu_items = [
    {"id": 1, "name": "เครปหมูหยองพริกเผา", "price": 45, "category": "Best Seller", "img": "https://cdn.discordapp.com/attachments/1459850014221275370/1459855622479675423/2.png?ex=6964cbff&is=69637a7f&hm=7ee449a72d2ffbd20c6bf44c7d6551a8adc3190f2c5fcf6c35adce782fccfc04&", "desc": "แป้งกรอบ ไส้แน่น ขายดีอันดับ 1"},
    {"id": 2, "name": "เครปนูเทลล่ากล้วย", "price": 55, "category": "Best Seller", "img": "https://cdn.discordapp.com/attachments/1459850014221275370/1459855622777344183/3.png?ex=6964cbff&is=69637a7f&hm=93e8f380c2dc4d737cd74f7b619417b7eddd9e5f66bd18972ff99912b7eec15f&", "desc": "หอมหวาน นูเทลล่าเยิ้มๆ"},
    {"id": 3, "name": "โตเกียวไส้กรอก", "price": 10, "category": "Tokyo", "img": "https://media.discordapp.net/attachments/1459850014221275370/1459850317591216280/118596952_2760734344183607_7073561490463837982_n.jpg?ex=6964c70e&is=6963758e&hm=a3784cc4690a4638f3deb22d84ad8553079f8be18191ec3f4ed583bc95a1dec6&=&format=webp", "desc": "ไส้กรอกไก่รมควัน แป้งนุ่ม"},
    {"id": 4, "name": "ชาไทยเย็น", "price": 35, "category": "Drinks", "img": "https://cdn.discordapp.com/attachments/1376544131970764942/1459411460152234017/Menu.png?ex=69632e56&is=6961dcd6&hm=83ef34ee0c1584cb104560c469eb1f824701eb55477688f4844b2b0835d06478&", "desc": "เข้มข้น หวานมัน"},
    {"id": 5, "name": "เครปแฮมชีส", "price": 50, "category": "Japanese Crepe", "img": "https://cdn.discordapp.com/attachments/1376544131970764942/1459411460152234017/Menu.png?ex=69632e56&is=6961dcd6&hm=83ef34ee0c1584cb104560c469eb1f824701eb55477688f4844b2b0835d06478&", "desc": "ชีสยืดๆ แฮมแผ่นโต"},
    {"id": 6, "name": "โกโก้เย็น", "price": 30, "category": "Drinks", "img": "https://cdn.discordapp.com/attachments/1376544131970764942/1459411460152234017/Menu.png?ex=69632e56&is=6961dcd6&hm=83ef34ee0c1584cb104560c469eb1f824701eb55477688f4844b2b0835d06478&", "desc": "เข้มข้น ไม่หวานมาก"},
]

promo_item = {
    "id": 99, 
    "name": "🔥 โปรโมชั่น: คู่หูฟินเวอร์", 
    "price": 89, 
    "category": "Promotion", 
    "img": "https://cdn.discordapp.com/attachments/1376544131970764942/1459414752068374661/-4.png?ex=69633167&is=6961dfe7&hm=134ed176cf485a3e4f823368bd58f14890b73f4bf15a6a504c04ac56e669c1b5&", 
    "desc": "เครปนูเทลล่า + ชาไทยเย็น ในราคาพิเศษ! (กดสั่งเลย)"
}

# ---------------------------------------------------------
# 3. Logic Functions
# ---------------------------------------------------------
def navigate_to(page_name, item=None):
    st.session_state.page = page_name
    if item:
        st.session_state.selected_item = item
    st.rerun()

def add_to_cart(item, addons, total_price):
    st.session_state.cart.append({"name": item['name'], "addons": addons, "price": total_price})
    st.toast(f"✅ เพิ่ม {item['name']} แล้ว", icon="🥞")
    time.sleep(0.5)
    navigate_to('home')

# ---------------------------------------------------------
# 4. Sidebar (โลโก้ + เมนู + ตะกร้า + Login)
# ---------------------------------------------------------
with st.sidebar:
    # 1. โลโก้
    c_side1, c_side2, c_side3 = st.columns([0.5, 3, 0.5])
    with c_side2:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.header("Family Crepe") # กันเหนียวถ้ารูปไม่ขึ้น
    st.write("")

    # 2. ปุ่มเมนูหลัก (เอาส่วนนี้กลับมาแล้วครับ ✅)
    if st.button("🏠 หน้าแรก", use_container_width=True): navigate_to('home')
    
    st.markdown("### 🍽️ หมวดหมู่เมนู")
    # กดแล้วจะกรองเมนู (ในเวอร์ชั่นหน้า พี่อาจต้องเขียน Logic กรองเพิ่ม แต่ตอนนี้ใส่ปุ่มไว้ก่อน)
    st.button("🔥 ขายดีที่สุด", use_container_width=True)
    st.button("🥤 เครื่องดื่ม", use_container_width=True)
    st.button("🥞 เครปญี่ปุ่น", use_container_width=True)
    st.button("🌭 โตเกียว", use_container_width=True)
    
    st.markdown("---")
    
    # 3. ปุ่มตะกร้า
    if st.button(f"🛒 ตะกร้า ({len(st.session_state.cart)})", type="primary", use_container_width=True):
        navigate_to('cart')

    st.markdown("---")
    
    # 4. ส่วนล็อกอินพนักงาน (เหมือนเดิม)
    if not st.session_state.is_logged_in:
        with st.expander("🔐 พนักงาน Login"):
            user_id = st.text_input("ID", key="login_id")
            user_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("เข้าสู่ระบบ"):
                if user_id == "admin" and user_pass == "1234":
                    st.session_state.is_logged_in = True
                    st.session_state.current_user = user_id
                    st.toast("ยินดีต้อนรับครับหัวหน้า! 😎")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("รหัสผิดครับ!")
    else:
        st.success(f"👤 : {st.session_state.current_user}")
        if st.button("⚙️ จัดการร้าน (Admin)", type="primary", use_container_width=True):
            navigate_to('admin')
            
        if st.button("ออกจากระบบ", use_container_width=True):
            st.session_state.is_logged_in = False
            st.session_state.current_user = None
            navigate_to('home')

# ---------------------------------------------------------
# 5. Page Content
# ---------------------------------------------------------

if st.session_state.page == 'home':
    col_h1, col_h2, col_h3 = st.columns([1, 6, 1])
    with col_h2:
        st.markdown("<h3 style='text-align: center; color:#d35400; margin:0;'>🥞 Beer Crepe Menu</h3>", unsafe_allow_html=True)
    with col_h3:
        if st.button(f"🛒{len(st.session_state.cart)}"):
            navigate_to('cart')

   # วางโค้ดนี้แทนที่อันเดิมได้เลย
    # --- 🟢 ส่วนสไลด์โชว์ (Slideshow) แบบ CSS ---
    
    # 1. กำหนดลิงก์รูปภาพที่จะให้เลื่อน (ใส่กี่รูปก็ได้ แต่ต้องแก้ CSS ตามจำนวน)
    # ในที่นี้ผมใส่ให้ 3 รูป (เบอร์เกอร์, เครป, เครื่องดื่ม)
    images = [
        "https://cdn.discordapp.com/attachments/1376544131970764942/1459414752068374661/-4.png?ex=696482e7&is=69633167&hm=9c8d87e56c375adfba2039c42a187ba9f558e4ddd053dddc8da1f0833ea0eb81& ", # รูป 1 (Burger)
        "https://media.discordapp.net/attachments/1459850014221275370/1459854223180304396/-5.png?ex=6964cab1&is=69637931&hm=ce40dd258cff5cc5781b319ab981db0c60902b4e4008d912e7543edf5c1a0a26&=&format=webp&quality=lossless&width=1062&height=531", # รูป 2 (Crepe - รูปเดิม)
        "https://cdn.discordapp.com/attachments/1459850014221275370/1459854315324969091/-6.png?ex=6964cac7&is=69637947&hm=f8d3dbe03b2221d16ecbec842eb0f328d190cfe1f555861baa528a405db52038&", # รูป 3 (Drink)
    ]
    
    # 2. สร้าง HTML/CSS สำหรับ Animation
    # หลักการ: เอา 3 รูปมาต่อกันแนวนอน แล้วสั่งให้เลื่อนซ้ายทีละจังหวะ
    slideshow_html = f"""
    <style>
        .slider-frame {{
            overflow: hidden;
            width: 100%;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
            margin-bottom: -10px; /* ดึงขอบล่างให้ชิดปุ่ม */
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }}
        
        .slide-images {{
            display: flex;
            width: 300%; /* 300% เพราะมี 3 รูป (ถ้ารูปเพิ่ม ต้องแก้ตรงนี้) */
            animation: slide_animation 12s infinite ease-in-out;
        }}
        
        .img-container {{
            width: 100%;
        }}
        
        .img-container img {{
            width: 100%;
            aspect-ratio: 16 / 7; /* กำหนดสัดส่วนรูปให้เท่ากัน (กว้าง/สูง) */
            object-fit: cover;
            display: block;
        }}

        /* คีย์เฟรมสั่งให้เลื่อน */
        @keyframes slide_animation {{
            0% {{ margin-left: 0%; }}
            30% {{ margin-left: 0%; }}       /* รูปที่ 1 ค้างไว้ */
            33% {{ margin-left: -100%; }}    /* เลื่อนไปรูป 2 */
            63% {{ margin-left: -100%; }}    /* รูปที่ 2 ค้างไว้ */
            66% {{ margin-left: -200%; }}    /* เลื่อนไปรูป 3 */
            96% {{ margin-left: -200%; }}    /* รูปที่ 3 ค้างไว้ */
            100% {{ margin-left: 0%; }}      /* กลับมาเริ่มใหม่ */
        }}
    </style>
    
    <div class="slider-frame">
        <div class="slide-images">
            <div class="img-container"><img src="{images[0]}"></div>
            <div class="img-container"><img src="{images[1]}"></div>
            <div class="img-container"><img src="{images[2]}"></div>
        </div>
    </div>
    """
    
    st.markdown(slideshow_html, unsafe_allow_html=True)

    # 3. ปุ่มกด (อันเดิม)
    # หมายเหตุ: อาจต้องปรับ margin-top ใน CSS ด้านบนสุดเล็กน้อยถ้ามันทับกันมากไป
    if st.button("🔥 สั่งโปรโมชั่น: คู่หูฟินเวอร์ (89฿) คลิกเลย!", type="primary", use_container_width=True, key="promo_btn_fixed"):
        navigate_to('detail', promo_item)

    def draw_menu_grid(title, items_list):
        st.markdown(f"#### {title}")
        cols = st.columns(2)
        for i, item in enumerate(items_list):
            with cols[i % 2]:
                # แสดงรูปโดยใช้ aspect-ratio 1:1
                st.markdown(f'<img src="{item["img"]}" class="menu-img">', unsafe_allow_html=True)
                btn_label = f"{item['name']}\n฿{item['price']}"
                if st.button(btn_label, key=f"btn_{item['id']}", use_container_width=True):
                    navigate_to('detail', item)
    
    best_sellers = [m for m in menu_items if m['category'] == "Best Seller"]
    draw_menu_grid("🔥 เมนูแนะนำ", best_sellers)
    
    drinks = [m for m in menu_items if m['category'] == "Drinks"]
    draw_menu_grid("🥤 เครื่องดื่ม", drinks)
    
    crepes = [m for m in menu_items if m['category'] == "Japanese Crepe"]
    draw_menu_grid("🥞 เครปญี่ปุ่น", crepes)
    
    tokyo = [m for m in menu_items if m['category'] == "Tokyo"]
    draw_menu_grid("🌭 โตเกียว", tokyo)
    
    st.write("")

# ==========================================
# PAGE: DETAIL
# ==========================================
elif st.session_state.page == 'detail':
    item = st.session_state.selected_item
    
    if st.button("⬅️ ย้อนกลับ"):
        navigate_to('home')

    st.image(item['img'], use_container_width=True)
    
    st.markdown(f"""
    <div style="background:white; padding:15px; border-radius:15px; margin-top:-10px; margin-bottom:15px; border:1px solid #eee;">
        <h3 style="margin:0; color:#2c3e50;">{item['name']}</h3>
        <p style="color:#7f8c8d; font-size:0.9em;">{item['desc']}</p>
        <h2 style="color:#e67e22; margin:0;">฿{item['price']}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("order_form"):
        st.markdown("#### 🛠️ เลือกท็อปปิ้ง (Toppings)")
        
        c1, c2 = st.columns(2)
        with c1:
            add_whip = st.checkbox("วิปครีม (+10฿)")
            add_foy = st.checkbox("ฝอยทอง (+10฿)")
        with c2:
            add_choc = st.checkbox("ซอสช็อก (+5฿)")
            add_cheese = st.checkbox("ชีส (+15฿)")
            
        st.markdown("#### 📝 โน้ต (ถ้ามี)")
        note = st.text_input("ระบุรายละเอียด", placeholder="เช่น ไม่กรอบ, หวานน้อย")
        
        submitted = st.form_submit_button("🛒 ใส่ตะกร้าเลย", type="primary", use_container_width=True)
        
        if submitted:
            final_price = item['price']
            addons_list = []
            if add_whip: final_price += 10; addons_list.append("วิปครีม")
            if add_foy: final_price += 10; addons_list.append("ฝอยทอง")
            if add_choc: final_price += 5; addons_list.append("ซอสช็อก")
            if add_cheese: final_price += 15; addons_list.append("ชีส")
            if note: addons_list.append(f"Note: {note}")
            
            add_to_cart(item, addons_list, final_price)

# ==========================================
# PAGE: CART (หน้าตะกร้า) - แก้ไขแล้ว ✅
# ==========================================
elif st.session_state.page == 'cart':
    col_c1, col_c2 = st.columns([1,5])
    with col_c1:
        if st.button("⬅️"): navigate_to('home')
    with col_c2:
        st.markdown("<h3 style='color:#333; margin:0;'>🛒 ตะกร้าสินค้า</h3>", unsafe_allow_html=True)

    if not st.session_state.cart:
        st.info("ยังไม่มีสินค้า")
    else:
        total = 0
        items_summary = [] 
        
        # วนลูปแสดงสินค้าในตะกร้า
        for x in st.session_state.cart:
            st.markdown(f"""
            <div style="background-color: white; border-radius: 10px; padding: 15px; margin-bottom: 10px; border: 1px solid #eee; color: #2c3e50;">
                <div style="font-weight: bold; font-size: 1.1em; display: flex; justify-content: space-between;">
                    <span>{x['name']}</span>
                    <span style="color: #e67e22;">฿{x['price']}</span>
                </div>
                <div style="color: #555; font-size: 0.9em; margin-top: 5px;">
                    {', '.join(x['addons']) if x['addons'] else '-'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            total += x['price']
            
            # เตรียมข้อความสำหรับ Discord
            addons_txt = f" ({', '.join(x['addons'])})" if x['addons'] else ""
            items_summary.append(f"• {x['name']}{addons_txt}")
        
        st.markdown(f"<h3 style='color:#333;'>รวมทั้งสิ้น: <span style='color:#e67e22'>{total} บาท</span></h3>", unsafe_allow_html=True)
        st.markdown("---")
        
        # ส่วนเลือกวิธีจ่ายเงิน
        st.markdown("<div style='color:#333; font-weight:bold; margin-bottom:5px;'>วิธีจ่ายเงิน</div>", unsafe_allow_html=True)
        payment_method = st.radio("วิธีจ่ายเงิน", ["โอน/สแกน", "เงินสด"], label_visibility="collapsed", key="payment_radio_discord")
        
        uploaded_slip = None

        if payment_method == "โอน/สแกน":
            st.markdown(f"""
            <div style="background-color: #ffebee; border: 1px solid #ffcdd2; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
                <p style="margin: 0; color: #c62828; font-weight: bold; font-size: 1.1em;">
                    📱 ยอดที่ต้องโอน: <span style="font-size: 1.4em;">{total} บาท</span>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            my_promptpay = "0812345678" # ⚠️ อย่าลืมแก้เบอร์พี่ตรงนี้นะครับ
            qr_url = f"https://promptpay.io/{my_promptpay}/{total}.png"
            st.image(qr_url, caption="สแกนจ่ายได้เลย", width=250)
            
            st.markdown("#### 📤 แนบสลิปโอนเงิน")
            uploaded_slip = st.file_uploader("อัปโหลดรูปสลิป", type=['png', 'jpg', 'jpeg'])

        # --- ปุ่มยืนยัน (วางทับปุ่มเดิมได้เลย) ---
        if st.button("ยืนยันการสั่งซื้อ", type="primary", use_container_width=True):
            
            # 1. เช็คก่อนว่าถ้าเลือกโอน แต่ไม่แนบสลิป ต้องแจ้งเตือน
            if payment_method == "โอน/สแกน" and uploaded_slip is None:
                st.error("❌ กรุณาแนบสลิปก่อนครับ")
            
            else:
                # เริ่มกระบวนการบันทึก (ใส่ Spinner หมุนๆ ให้ดูดี)
                with st.spinner('กำลังส่งออเดอร์...'):
                    
                    try:
                        # [A] สร้างข้อมูลออเดอร์เตรียมไว้
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        items_str = ", ".join([f"{item['name']}" for item in st.session_state.cart])
                        
                        # สร้าง DataFrame ของออเดอร์ใหม่
                        new_order = pd.DataFrame([{
                            "Timestamp": timestamp,
                            "Items": items_str,
                            "Total": total,
                            "Payment": payment_method,
                            "Note": "สั่งผ่านเว็บ"
                        }])

                        # [B] บันทึกลง Google Sheets (แก้ Logic ตรงนี้ครับ ✅)
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        
                        try:
                            # 1. ลองอ่านข้อมูลเก่าออกมาก่อน
                            existing_data = conn.read(worksheet="Order", ttl=0)
                            # 2. เอาของเก่า + ของใหม่ มารวมกัน
                            updated_data = pd.concat([existing_data, new_order], ignore_index=True)
                            # 3. บันทึกทับลงไป (Update) แทนการสร้างใหม่ (Create)
                            conn.update(worksheet="Order", data=updated_data)
                        except Exception:
                            # กรณีฉุกเฉิน: ถ้ายังไม่มีหน้า Order จริงๆ ค่อยสร้างใหม่
                            conn.create(worksheet="Order", data=new_order)
                        
                        # [C] ส่งเข้า Discord
                        DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1459843581895512096/ES0jZW806_2BhiJUWCA19tKGu_yONBCdwxiNvpGcrhno9MzfYxxTud4eoNNcvC5ubyso"
                        
                        msg = f"**📣 ออเดอร์ใหม่มาแล้ว!**\n"
                        msg += "--------------------------------\n"
                        msg += "\n".join(items_summary)
                        msg += "\n--------------------------------\n"
                        msg += f"💰 **ยอดรวม: {total} บาท**\n"
                        msg += f"💳 **วิธีจ่าย:** {payment_method}"
                        if payment_method == "เงินสด":
                            msg += "\n⚠️ *โปรดเก็บเงินหน้างาน*"
                        
                        send_discord_notify(DISCORD_WEBHOOK_URL, msg, uploaded_slip)
                        
                        # [D] ล้างค่าและแจ้งเตือนสำเร็จ
                        st.session_state.cart = [] # ล้างตะกร้า
                        st.cache_data.clear()      # ล้าง Cache
                        
                        st.balloons()
                        st.success("✅ สั่งเรียบร้อย! ข้อมูลส่งเข้าครัวแล้ว")
                        
                        # [E] หน่วงเวลาและรีเฟรชหน้า
                        time.sleep(2)
                        navigate_to('home')
                        
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {e}")

# ==========================================
# PAGE: ADMIN (หน้าหลังบ้าน)
# ==========================================
elif st.session_state.page == 'admin':
    # เช็คความปลอดภัย: ถ้าไม่ได้ล็อกอิน ห้ามเข้าหน้านี้!
    if not st.session_state.is_logged_in:
        st.warning("กรุณาล็อกอินก่อนครับ")
        if st.button("กลับหน้าแรก"): navigate_to('home')
    else:
        admin_page() # เรียกใช้ฟังก์ชันที่เราสร้างไว้ข้อ 2
        
