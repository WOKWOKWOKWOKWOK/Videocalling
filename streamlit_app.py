import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Page Configuration
st.set_page_config(page_title="Custom P2P Call Hub", layout="wide")

# Persistent storage engine - keeps rooms alive across page refreshes
if "room_requests" not in st.session_state:
    st.session_state.room_requests = []  # List of dicts: {id, user, target, status, room_url}
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "active_room" not in st.session_state:
    st.session_state.active_room = None

# --- SIDEBAR: AUTHENTICATION ---
with st.sidebar:
    st.title("🔐 Access Control")
    
    if not st.session_state.is_admin:
        st.subheader("Admin Login")
        admin_password = st.text_input("Enter Admin Password", type="password")
        if st.button("Sign In as Admin"):
            if admin_password == "admin123": # Change password here
                st.session_state.is_admin = True
                st.rerun()
            else:
                st.error("Incorrect password!")
    else:
        st.success("👑 Logged in as Admin")
        if st.button("Sign Out"):
            st.session_state.is_admin = False
            st.rerun()

# --- MAIN INTERFACE ---
st.title("📞 Custom Multi-User Call Hub")
st.caption("Real-time peer-to-peer video rooms that bypass standard network blocks.")

tab1, tab2 = st.tabs(["👤 User Workspace", "👑 Admin Dashboard"])

# ==========================================
# TAB 1: USER WORKSPACE
# ==========================================
with tab1:
    st.header("Request a New Call Session")
    
    with st.form("request_form", clear_on_submit=True):
        your_name = st.text_input("Your Name / Alias", placeholder="e.g., Alice")
        target_name = st.text_input("Who do you want to chat with?", placeholder="e.g., Bob")
        submit_request = st.form_submit_button("Submit Room Request")
        
        if submit_request:
            if your_name and target_name:
                unique_id = str(uuid.uuid4())[:8]
                new_request = {
                    "id": unique_id,
                    "user": your_name,
                    "target": target_name,
                    "status": "Pending Admin Approval",
                    "room_url": None
                }
                st.session_state.room_requests.append(new_request)
                st.success(f"Request '{unique_id}' submitted! Wait for Admin approval.")
            else:
                st.error("Please fill out both name fields.")

    st.divider()
    
    st.subheader("Active & Pending Call Rooms")
    if not st.session_state.room_requests:
        st.info("No rooms have been requested yet.")
    else:
        for req in st.session_state.room_requests:
            col_info, col_action = st.columns(2)
            with col_info:
                st.write(f"**Chat Room {req['id']}:** {req['user']} ↔️ {req['target']} | **Status:** `{req['status']}`")
            
            with col_action:
                if req["status"] == "Approved" and req["room_url"]:
                    if st.button(f"Join Call Room ({req['id']})", key=f"join_{req['id']}"):
                        st.session_state.active_room = req["room_url"]
                        st.rerun()
                else:
                    st.button("Awaiting Admin...", disabled=True, key=f"wait_{req['id']}")

    # The actual video calling container
    if st.session_state.active_room:
        st.divider()
        st.subheader("🎥 Live P2P Connection")
        
        if st.button("🔴 Close Call & Leave Room"):
            st.session_state.active_room = None
            st.rerun()
        else:
            # Custom component injecting permissions directly to modern secure domains
            iframe_html = f"""
            <iframe 
                src="{st.session_state.active_room}" 
                allow="camera; microphone; speaker-selection; display-capture; autoplay; fullscreen" 
                style="height: 650px; width: 100%; border: 0px; border-radius: 8px;"
            ></iframe>
            """
            components.html(iframe_html, height=670)

# ==========================================
# TAB 2: ADMIN DASHBOARD
# ==========================================
with tab2:
    if not st.session_state.is_admin:
        st.warning("🔒 Access Denied. Please sign in via the admin login panel on the left sidebar.")
    else:
        st.header("Control Panel: Manage Sessions")
        st.write("Review inbound participant requests and approve real-time rooms.")
        
        if not st.session_state.room_requests:
            st.info("No incoming user requests to process.")
        else:
            for index, req in enumerate(st.session_state.room_requests):
                with st.expander(f"Request ID: {req['id']} ({req['user']} calling {req['target']})"):
                    st.write(f"Current State: `{req['status']}`")
                    
                    if req["status"] == "Pending Admin Approval":
                        col_approve, col_deny = st.columns(2)
                        
                        with col_approve:
                            if st.button("Approve Request", key=f"app_{req['id']}"):
                                # FIXED: Included explicit forward slashes in the path construction
                                unique_room_id = f"stmeet-{req['id']}-{uuid.uuid4().hex[:6]}"
                                st.session_state.room_requests[index]["status"] = "Approved"
                                st.session_state.room_requests[index]["room_url"] = f"https://p2p.mirotalk.com/join/{unique_room_id}"
                                st.success("Room approved!")
                                st.rerun()
                                
                        with col_deny:
                            if st.button("Deny / Delete Request", key=f"den_{req['id']}"):
                                st.session_state.room_requests.pop(index)
                                st.warning("Request rejected.")
                                st.rerun()
                    else:
                        st.write(f"✅ **Active Room Link:** `{req['room_url']}`")
                        if st.button("Revoke & Close Room", key=f"rev_{req['id']}"):
                            if st.session_state.active_room == req["room_url"]:
                                st.session_state.active_room = None
                            st.session_state.room_requests.pop(index)
                            st.rerun()
