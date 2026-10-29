import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Clear Page Environment Configuration Setup
st.set_page_config(page_title="Standalone Custom Meet Workspace", layout="wide")

# Safe server-side memory block shared across ALL connected tabs and users seamlessly
@st.cache_resource
def get_global_database():
    return []  # A single persistent repository array tracking all active calling rooms

global_db = get_global_database()

# Track authentication status for this unique browser window
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "active_room_id" not in st.session_state:
    st.session_state.active_room_id = None

# --- SIDEBAR: AUTHENTICATION LOCK ---
with st.sidebar:
    st.title("🔐 Access Control")
    
    if not st.session_state.is_admin:
        st.subheader("Admin Login")
        admin_password = st.text_input("Enter Admin Password", type="password")
        if st.button("Sign In as Admin"):
            if admin_password == "admin123":  # Default supervisor keypass
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
st.title("📞 Native Independent Call Hub")
st.caption("Self-contained video grids executing natively within your application sandbox containers.")

# Map out separate workspaces
tab1, tab2 = st.tabs(["👤 User Workspace", "👑 Admin Dashboard"])
# ==========================================
# TAB 1: USER WORKSPACE
# ==========================================
with tab1:
    st.header("Request a New Call Session")
    
    # Form for requesting a room
    with st.form("request_form", clear_on_submit=True):
        your_name = st.text_input("Your Name / Alias", placeholder="e.g., Alice")
        target_name = st.text_input("Who do you want to chat with? (Groups allowed)", placeholder="e.g., Bob, Charlie")
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
                global_db.append(new_request)
                st.success(f"Request '{unique_id}' submitted globally! Tell your partners to open this site.")
            else:
                st.error("Please fill out both entry fields.")

    st.divider()
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

    # ========================================================
    # NATIVE MULTI-USER VIDEO ENGINE (NO EXTERNAL IFRAME WEBSITES)
    # ========================================================
    if st.session_state.active_room_id:
        st.divider()
        st.subheader(f"🎥 Active Multi-User Session ID: {st.session_state.active_room_id}")
        
        if st.button("🔴 Close Call & Leave Room"):
            st.session_state.active_room_id = None
            st.rerun()
        else:
            native_video_room_html = f"""
            <div style="font-family:sans-serif;background:#141414;color:white;padding:20px;border-radius:12px;text-align:center;">
                <div id="vGrid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:15px;margin-bottom:15px;">
                    <div>
                        <p style="margin:5px;color:#00ffcc;font-weight:bold;">My Webcam</p>
                        <video id="myStream" autoplay playsinline muted style="width:100%;max-height:220px;background:#222;border-radius:8px;transform:scaleX(-1);"></video>
                    </div>
                </div>
                <div id="status" style="font-size:13px;color:#ffcc00;padding:6px 12px;background:#222;border-radius:6px;display:inline-block;">Initializing browser-native WebRTC mesh...</div>
            </div>
            <script src="https://pubnub.com"></script>
            <script>
                const grid=document.getElementById('vGrid'),status=document.getElementById('status'),myVid=document.getElementById('myStream');
                const chan="st-rm-{st.session_state.active_room_id}",myId='usr-'+Math.random().toString(36).substr(2,5),peers={{}};
                let stream;
                const cfg={{iceServers:[{{urls:"stun:://google.com"}},{{urls:"stun:://google.com"}}]}};
                const pubnub=new PubNub({{publishKey:'pub-c-497b9da5-f2d4-473d-88ec-a3424172f3ca',subscribeKey:'sub-c-134bd918-97e3-11eb-ad76-62024806aeb7',uuid:myId}});
                async function init() {{
                    try{{
                        stream=await navigator.mediaDevices.getUserMedia({{video:true,audio:true}});
                        myVid.srcObject=stream;status.innerText="Webcam connected. Connecting to signaling network...";
                        pubnub.addListener({{message:async(p)=>{{
                            if(p.publisher===myId)return;
                            const m=p.message;
                            if(m.join) {{
                                const pc=makePC(p.publisher);
                                const offer=await pc.createOffer();await pc.setLocalDescription(offer);
                                pubnub.publish({{channel:chan,message:{{offer:offer,to:p.publisher}}}});
                            }}else if(m.to===myId && m.offer){{
                                const pc=makePC(p.publisher);await pc.setRemoteDescription(new RTCSessionDescription(m.offer));
                                const ans=await pc.createAnswer();await pc.setLocalDescription(ans);
                                pubnub.publish({{channel:chan,message:{{answer:ans,to:p.publisher}}}});
                            }}else if(m.to===myId && m.answer){{
                                if(peers[p.publisher])await peers[p.publisher].setRemoteDescription(new RTCSessionDescription(m.answer));
                            }}else if(m.to===myId && m.candidate){{
                                if(peers[p.publisher])await peers[p.publisher].addIceCandidate(new RTCIceCandidate(m.candidate));
                            }}
                        }}}});
                        pubnub.subscribe({{channels:[chan]}});
                        setTimeout(()=>{{pubnub.publish({{channel:chan,message:{{join:true}}}});status.innerText="Room active. Waiting for others...";}},1000);
                    }}catch(e){{status.innerText="Hardware block: "+e.message;}}
                }}
                function makePC(uid){{
                    if(peers[uid])return peers[uid];
                    const pc=new RTCPeerConnection(cfg);peers[uid]=pc;
                    stream.getTracks().forEach(t=>pc.addTrack(t,stream));
                    pc.onicecandidate=(e)=>{{if(e.candidate)pubnub.publish({{channel:chan,message:{{candidate:e.candidate,to:uid}}}});}};
                    pc.ontrack=(e)=>{{
                        if(document.getElementById('v-'+uid))return;
                        const d=document.createElement('div');d.innerHTML=`<p style="margin:5px;color:#00ffcc;font-weight:bold;">Partner</p>`;
                        const v=document.createElement('video');v.id='v-'+uid;v.autoplay=true;v.playsInline=true;
                        v.style.width="100%";v.style.maxHeight="220px";v.style.background="#222";v.style.borderRadius="8px";
                        v.srcObject=e.streams[0];d.appendChild(v);grid.appendChild(d);status.innerText="Group link active!";
                    }};
                    return pc;
                }}
                init();
            </script>
            """
            components.html(native_video_room_html, height=520)
