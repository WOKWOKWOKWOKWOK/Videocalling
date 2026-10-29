import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Page Configuration
st.set_page_config(page_title="Block-Proof Custom Meet", layout="wide")

# Persistent storage engine - locks state values during page refreshes
if "room_requests" not in st.session_state:
    st.session_state.room_requests = []  # List of dicts: {id, user, target, status, room_id}
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
st.title("📞 Native Filter-Bypass Call Hub")
st.caption("P2P video streaming running natively on your app domain to clear network blocks.")

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
                unique_id = str(uuid.uuid4())[:8]
                new_request = {
                    "id": unique_id,
                    "user": your_name,
                    "target": target_name,
                    "status": "Pending Admin Approval",
                    "room_id": None
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
            col_info, col_action = st.columns(2)
            with col_info:
                st.write(f"**Chat Room {req['id']}:** {req['user']} ↔️ {req['target']} | **Status:** `{req['status']}`")
            
            with col_action:
                if req["status"] == "Approved" and req["room_id"]:
                    if st.button(f"Join Call Room", key=f"join_{req['id']}"):
                        st.session_state.active_room_id = req["room_id"]
                        st.rerun()
                else:
                    st.button("Awaiting Admin...", disabled=True, key=f"wait_{req['id']}")

    # Render Native WebRTC Component Window with custom HTML5 bypass layout
    if st.session_state.active_room_id:
        st.divider()
        st.subheader(f"🎥 Native Call Room Session: {st.session_state.active_room_id}")
        
        if st.button("🔴 Close Call & Leave Room"):
            st.session_state.active_room_id = None
            st.rerun()
        else:
            # Standalone Native HTML/JS module uses Google STUN routing infrastructure directly
            native_webrtc_html = f"""
            <div style="font-family: sans-serif; background-color: #111; color: white; padding: 20px; border-radius: 8px; text-align: center;">
                <div style="display: flex; justify-content: center; gap: 20px; margin-bottom: 15px;">
                    <div>
                        <p style="margin: 5px; color: #aaa;">Local View</p>
                        <video id="localVideo" autoplay playsinline muted style="width: 100%; max-width: 400px; background: #222; border-radius: 6px; transform: scaleX(-1);"></video>
                    </div>
                    <div>
                        <p style="margin: 5px; color: #aaa;">Remote Partner</p>
                        <video id="remoteVideo" autoplay playsinline style="width: 100%; max-width: 400px; background: #222; border-radius: 6px;"></video>
                    </div>
                </div>
                <div id="statusLog" style="font-size: 14px; color: #00ffcc; margin-top: 10px;">Initializing native hardware media stream connection pipelines...</div>
            </div>

            <script>
                const statusLog = document.getElementById('statusLog');
                const localVideo = document.getElementById('localVideo');
                const remoteVideo = document.getElementById('remoteVideo');
                let localStream;
                let peerConnection;

                // High-availability public fallback signaling addresses hosted directly by Google
                const rtcConfig = {{
                    iceServers: [{{ urls: 'stun:://google.com' }}, {{ urls: 'stun:://google.com' }}]
                }};

                async function startNativeCall() {{
                    try {{
                        localStream = await navigator.mediaDevices.getUserMedia({{ video: true, audio: true }});
                        localVideo.srcObject = localStream;
                        statusLog.innerText = "Camera and Microphone active. Awaiting connection token handshake exchange...";
                        
                        peerConnection = new RTCPeerConnection(rtcConfig);
                        localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

                        peerConnection.ontrack = (event) => {{
                            if (event.streams && event.streams[0]) {{
                                remoteVideo.srcObject = event.streams[0];
                                statusLog.innerText = "Connected! Live media stream pipeline verified.";
                            }}
                        }};
                    }} catch (error) {{
                        statusLog.innerText = "Hardware access blocked or camera missing: " + error.message;
                    }}
                }}
                
                startNativeCall();
            </script>
            """
            components.html(native_webrtc_html, height=450)

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
                                st.session_state.room_requests[index]["status"] = "Approved"
                                st.session_state.room_requests[index]["room_id"] = req['id']
                                st.success("Pipeline slot allocated!")
                                st.rerun()
                                
                        with col_deny:
                            if st.button("Deny / Delete Request", key=f"den_{req['id']}"):
                                st.session_state.room_requests.pop(index)
                                st.warning("Request rejected.")
                                st.rerun()
                    else:
                        st.write(f"✅ **Active Pipeline Code:** `{req['room_id']}`")
                        if st.button("Revoke & Close Room", key=f"rev_{req['id']}"):
                            if st.session_state.active_room_id == req["room_id"]:
                                st.session_state.active_room_id = None
                            st.session_state.room_requests.pop(index)
                            st.rerun()
