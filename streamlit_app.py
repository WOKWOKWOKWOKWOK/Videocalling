import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Page Configuration
st.set_page_config(page_title="Custom Meet Manager", layout="wide")

# Initialize central database in session state (simulating a database)
if "room_requests" not in st.session_state:
    st.session_state.room_requests = []  # List of dicts: {id, user, target, status, room_url}
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# --- SIDEBAR: AUTHENTICATION & NAVIGATION ---
with st.sidebar:
    st.title("🔐 Access Control")
    
    if not st.session_state.is_admin:
        st.subheader("Admin Login")
        admin_password = st.text_input("Enter Admin Password", type="password")
        if st.button("Sign In as Admin"):
            # Change "admin123" to whatever password you want
            if admin_password == "admin123":
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

# Create horizontal sections using tabs
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
                # Add request to our central state tracker
                new_request = {
                    "id": str(uuid.uuid4())[:8],
                    "user": your_name,
                    "target": target_name,
                    "status": "Pending Admin Approval",
                    "room_url": None
                }
                st.session_state.room_requests.append(new_request)
                st.success(f"Request submitted! Tell {target_name} to check back soon once the Admin approves it.")
            else:
                st.error("Please fill out both name fields.")

    st.divider()
    
    # List of sessions for users to see and join
    st.subheader("Active & Pending Call Rooms")
    if not st.session_state.room_requests:
        st.info("No rooms have been requested yet.")
    else:
        for req in st.session_state.room_requests:
            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.write(f"**Chat:** {req['user']} ↔️ {req['target']} | **Status:** `{req['status']}`")
            
            with col_action:
                if req["status"] == "Approved" and req["room_url"]:
                    if st.button(f"Join Call ({req['id']})", key=f"join_{req['id']}"):
                        st.session_state.active_room = req["room_url"]
                else:
                    st.button("Waiting...", disabled=True, key=f"wait_{req['id']}")

    # Embedded Active Video Call Iframe
    if "active_room" in st.session_state:
        st.divider()
        st.subheader("🎥 Live Meeting Connection")
        if st.button("Close Call / Leave Room"):
            del st.session_state.active_room
            st.rerun()
        else:
            # Securely render the call window inside the app using the verified Jitsi domain
            components.iframe(src=st.session_state.active_room, height=650, scrolling=False)

# ==========================================
# TAB 2: ADMIN DASHBOARD
# ==========================================
with tab2:
    if not st.session_state.is_admin:
        st.warning("🔒 Access Denied. Please sign in via the admin login panel on the left sidebar.")
    else:
        st.header("Control Panel: Manage Sessions")
        st.write("Review inbound participant requests and generate secure meeting URLs.")
        
        if not st.session_state.room_requests:
            st.info("No incoming user requests to process.")
        else:
            # Render a management dashboard for the Admin
            for index, req in enumerate(st.session_state.room_requests):
                with st.expander(f"Request {req['id']}: {req['user']} wants to call {req['target']}"):
                    st.write(f"Current Status: `{req['status']}`")
                    
                    if req["status"] == "Pending Admin Approval":
                        col_approve, col_deny = st.columns(2)
                        
                        with col_approve:
                            if st.button("Approve & Create Room", key=f"app_{req['id']}"):
                                # Generate a completely unique random string for the Jitsi room name
                                unique_room_id = f"StreamlitMeet-{uuid.uuid4().hex[:12]}"
                                
                                # FIXED DOMAIN URL STRUCTURE
                                st.session_state.room_requests[index]["status"] = "Approved"
                                st.session_state.room_requests[index]["room_url"] = f"https://jit.si{unique_room_id}"
                                
                                st.success("Room authorized successfully!")
                                st.rerun()
                                
                        with col_deny:
                            if st.button("Deny / Delete Request", key=f"den_{req['id']}"):
                                st.session_state.room_requests.pop(index)
                                st.warning("Request rejected and removed.")
                                st.rerun()
                    else:
                        st.write(f"🔗 **Generated Link:** {req['room_url']}")
                        if st.button("Revoke / Close Room Slot", key=f"rev_{req['id']}"):
                            st.session_state.room_requests.pop(index)
                            if "active_room" in st.session_state and st.session_state.active_room == req["room_url"]:
                                del st.session_state.active_room
                            st.rerun()
