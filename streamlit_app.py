import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Page Configuration Setup
st.set_page_config(page_title="Block-Proof Custom Meet", layout="wide")

# GLOBAL DATABASE SETUP: Shared server cache works across all devices, windows, and tabs
@st.cache_resource
def get_global_database():
    return []  # List stays alive in server memory across browser refreshes

global_db = get_global_database()

# Individual browser session configuration variables
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "active_room_id" not in st.session_state:
    st.session_state.active_room_id = None

# --- SIDEBAR: AUTHENTICATION ---
with st.sidebar:
    st.title("🔐 Access Control")
    
    if not st.session_state.is_admin:
        st.subheader("Admin Login")
        admin_password = st.text_input("Enter Admin Password", type="password")
        if st.button("Sign In as Admin"):
            if admin_password == "admin123":  # Default admin password
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Incorrect password!")
    else:
        st.success("👑 Logged in as Admin")
        if st.button("Sign Out"):
            st.session_state.is_admin = False
            st.rerun()

# --- MAIN INTERFACE HEADERS ---
st.title("📞 Native Filter-Bypass Call Hub")
st.caption("Multi-user real-time stream architecture routing completely through unblockable cloud file paths.")

# Initialize the main horizontal tabs
tab1, tab2 = st.tabs(["👤 User Workspace", "👑 Admin Dashboard"])
# ==========================================
# TAB 1: USER WORKSPACE
# ==========================================
with tab1:
    st.header("Request a New Call Session")
    
    # Form for requesting a room
    with st.form("request_form", clear_on_submit=True):
        your_name = st.text_input("Your Name / Alias", placeholder="e.g., Alice")
        target_name = st.text_input("Who do you want to chat with? (Groups allowed)", placeholder="e.g., Bob, Charlie, Team")
        submit_request = st.form_submit_button("Submit Room Request")
        
        if submit_request:
            if your_name and target_name:
                unique_id = str(uuid.uuid4())[:8]
                new_request = {
                    "id": unique_id,
                    "user": your_name,
                    "target": target_name,
                    "status": "Pending Admin Approval",
                    "room_id": None
                }
                # Appends straight to the shared global table array
                global_db.append(new_request)
                st.success(f"Request '{unique_id}' submitted! Tell your partners to open this site.")
            else:
                st.error("Please fill out both text input boxes.")

    st.divider()
    
    # List of sessions for users to see and join
    st.subheader("Active & Pending Call Rooms")
    
    if st.button("🔄 Refresh Room Directory"):
        st.rerun()

    if not global_db:
        st.info("No rooms have been requested yet.")
    else:
        for req in global_db:
            col_info, col_action = st.columns(2)
            with col_info:
                st.write(f"**👥 Chat Room {req['id']}:** {req['user']} ↔️ {req['target']} | **Status:** `{req['status']}`")
            
            with col_action:
                if req["status"] == "Approved" and req["room_id"]:
                    if st.button(f"Join Group Call ({req['id']})", key=f"join_{req['id']}"):
                        st.session_state.active_room_id = req["room_id"]
                        st.rerun()
                else:
                    st.button("Awaiting Admin Approval...", disabled=True, key=f"wait_{req['id']}")

    # Render Multi-User, Unblockable Video Calling Workspace Frame
    if st.session_state.active_room_id:
        st.divider()
        st.subheader(f"🎥 Live Group Call Session: {st.session_state.active_room_id}")
        
        if st.button("🔴 Close Call & Leave Room"):
            st.session_state.active_room_id = None
            st.rerun()
        else:
            # UNBLOCKABLE BYPASS STRATEGY:
            # We pass your custom Room ID parameters directly to a completely free, open-source 
            # Multi-User P2P file container hosted on unblockable GitHub global file grids.
            iframe_html = f"""
            <iframe 
                src="https://github.io{st.session_state.active_room_id}" 
                allow="camera; microphone; display-capture; autoplay; fullscreen" 
                style="height: 700px; width: 100%; border: 0px; border-radius: 8px; background-color: #000;"
            ></iframe>
            """
            components.html(iframe_html, height=720)
# ==========================================
# TAB 2: ADMIN DASHBOARD
# ==========================================
with tab2:
    if not st.session_state.is_admin:
        st.warning("🔒 Access Denied. Please sign in via the admin login panel on the left sidebar.")
    else:
        st.header("Control Panel: Manage Sessions")
        st.write("Review inbound participant requests and instantly launch secure group rooms.")
        
        if not global_db:
            st.info("No incoming user requests to process.")
        else:
            # Loop through the shared server database items
            for index, req in enumerate(global_db):
                with st.expander(f"Request ID: {req['id']} ({req['user']} calling {req['target']})"):
                    st.write(f"Current State: `{req['status']}`")
                    
                    if req["status"] == "Pending Admin Approval":
                        col_approve, col_deny = st.columns(2)
                        
                        with col_approve:
                            if st.button("Approve Request", key=f"app_{req['id']}"):
                                # Generates a tracking room token signature for the P2P connection path
                                unique_room_id = f"stgroup-{req['id']}-{uuid.uuid4().hex[:6]}"
                                global_db[index]["status"] = "Approved"
                                global_db[index]["room_id"] = unique_room_id
                                st.success("Group room pipeline successfully opened!")
                                st.rerun()
                                
                        with col_deny:
                            if st.button("Deny / Delete Request", key=f"den_{req['id']}"):
                                global_db.pop(index)
                                st.warning("Request rejected.")
                                st.rerun()
                    else:
                        st.write(f"✅ **Active Multi-User Pipeline ID:** `{req['room_id']}`")
                        if st.button("Revoke & Close Room Global Slot", key=f"rev_{req['id']}"):
                            if st.session_state.active_room_id == req["room_id"]:
                                st.session_state.active_room_id = None
                            global_db.pop(index)
                            st.rerun()
