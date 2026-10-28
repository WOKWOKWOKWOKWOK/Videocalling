import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Page Configuration
st.set_page_config(page_title="Custom Meet Manager", layout="wide")

# Persistent storage engine - locks state values during page refreshes
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
            if admin_password == "admin123": # Default password
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
st.title("📞 Streamlit Custom Call Hub")
st.caption("Request, manage, and join video calling sessions securely.")

# Create main navigation tabs
tab1, tab2 = st.tabs(["👤 User Workspace", "👑 Admin Dashboard"])

# ==========================================
# TAB 1: USER WORKSPACE
# ==========================================
with tab1:
    st.header("Request a New Call Session")
    
    # Form for requesting a room
    with st.form("request_form", clear_on_submit=True):
        your_name = st.text_input("Your Name / Alias", placeholder="e.g., Alice")
        target_name = st.text_input("Who do you want to chat with?", placeholder="e.g., Bob")
        submit_request = st.form_submit_button("Submit Room Request")
        
        if submit_request:
            if your_name and target_name:
                # Generate unique ID and link details securely
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
    
    # List of sessions for users to see and join
    st.subheader("Active & Pending Call Rooms")
    if not st.session_state.room_requests:
        st.info("No rooms have been requested yet.")
    else:
        for req in st.session_state.room_requests:
            # FIXED: Explicitly defined column count and layout weights
            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.write(f"**Chat Room {req['id']}:** {req['user']} ↔️ {req['target']} | **Status:** `{req['status']}`")
            
            with col_action:
                if req["status"] == "Approved" and req["room_url"]:
                    if st.button(f"Join Call Room", key=f"join_{req['id']}"):
                        st.session_state.active_room = req["room_url"]
                        st.rerun()
                else:
                    st.button("Awaiting Admin...", disabled=True, key=f"wait_{req['id']}")

    # Render Video Component with Camera/Mic Permissions explicitly declared
    if st.session_state.active_room:
        st.divider()
        st.subheader("🎥 Live Meeting Connection")
        
        if st.button("🔴 Close Call & Leave Room"):
            st.session_state.active_room = None
            st.rerun()
        else:
            # The allow string bypasses browser feature policy blocks on the iframe container
            iframe_html = f"""
            <iframe 
                src="{st.session_state.active_room}" 
                allow="camera; microphone; display-capture; autoplay; clipboard-write" 
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
        st.write("Review inbound participant requests and assign meeting locations.")
        
        if not st.session_state.room_requests:
            st.info("No incoming user requests to process.")
        else:
            # Render active dashboard cards for the logged-in supervisor
            for index, req in enumerate(st.session_state.room_requests):
                with st.expander(f"Request ID: {req['id']} ({req['user']} calling {req['target']})"):
                    st.write(f"Current State: `{req['status']}`")
                    
                    if req["status"] == "Pending Admin Approval":
                        # Let the admin paste or assign a specific room string 
                        suggested_room_name = f"room-{req['id']}"
                        room_input = st.text_input("Assign Whereby Room Name/URL", value=f"https://whereby.com{suggested_room_name}", key=f"input_{req['id']}")
                        
                        col_approve, col_deny = st.columns(2)
                        
                        with col_approve:
                            if st.button("Approve Request", key=f"app_{req['id']}"):
                                st.session_state.room_requests[index]["status"] = "Approved"
                                st.session_state.room_requests[index]["room_url"] = room_input
                                st.success("Room approved!")
                                st.rerun()
                                
                        with col_deny:
                            if st.button("Deny / Delete Request", key=f"den_{req['id']}"):
                                st.session_state.room_requests.pop(index)
                                st.warning("Request rejected.")
                                st.rerun()
                    else:
                        st.write(f"🔗 **Live Server Link:** {req['room_url']}")
                        if st.button("Revoke & Close Room", key=f"rev_{req['id']}"):
                            if st.session_state.active_room == req["room_url"]:
                                st.session_state.active_room = None
                            st.session_state.room_requests.pop(index)
                            st.rerun()
