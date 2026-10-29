import streamlit as st
import streamlit.components.v1 as components
import uuid

# 1. Clean Page Layout Setup
st.set_page_config(page_title="Instant Multi-User Meet Hub", layout="wide")

# GLOBAL CACHE CONTAINER: Single list in server memory shared across ALL devices and tabs
@st.cache_resource
def get_global_database():
    return {}  # Maps room_name -> active tracking token identifier

global_rooms = get_global_database()

# Track this specific browser tab's session state
if "current_room_id" not in st.session_state:
    st.session_state.current_room_id = None

st.title("📞 Instant Open Call Hub")
st.caption("No sign-ups, no admin waiting queues. Enter a room token code and connect immediately.")

st.header("Enter or Create a Meeting Room")

# Direct form interface block to enter calling rooms instantly
with st.form("join_room_form", clear_on_submit=False):
    room_name_input = st.text_input("Room Token Name ID", placeholder="e.g., project-alpha, chat123").strip().lower()
    join_submit = st.form_submit_button("🚀 Enter Call Room Space")
    
    if join_submit:
        if room_name_input:
            # If the room isn't created globally yet, save its token signature instantly
            if room_name_input not in global_rooms:
                global_rooms[room_name_input] = f"room-mesh-{room_name_input}-{uuid.uuid4().hex[:4]}"
            
            st.session_state.current_room_id = global_rooms[room_name_input]
            st.success(f"Success! Entered Room: '{room_name_input}'. Share that name token code with others to join!")
        else:
            st.error("Please type a room code identification phrase first.")

st.divider()
# ========================================================
# INSTANT NATIVE MULTI-USER VIDEO CALL ENGINE
# ========================================================
if st.session_state.current_room_id:
    st.subheader(f"🎥 Active Room Grid Pipeline Connection Window")
    
    # Navigation toggle button to disconnect from the calling array
    if st.button("🔴 Close Connection & Leave Call Room"):
        st.session_state.current_room_id = None
        st.rerun()
    else:
        # 🛠️ FIXED STRUCTURE: Raw HTML wrapper with explicit browser permission access policies
        raw_webrtc_code = f"""
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
            const chan="st-rm-{st.session_state.current_room_id}",myId='usr-'+Math.random().toString(36).substr(2,5),peers={{}};
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
                    v.srcObject=e.streams;d.appendChild(v);grid.appendChild(d);status.innerText="Group link active!";
                }};
                return pc;
            }}
            init();
        </script>
        """
        
        # 🛠️ THE CORE PERMISSION BYPASS: Wraps the html inside a custom iframe container block
        # that explicitly grants hardware device authorization commands.
        escaped_html = raw_webrtc_code.replace('"', '&quot;').replace('\n', ' ')
        iframe_string = f"""
        <iframe 
            srcdoc="{escaped_html}" 
            allow="camera; microphone; display-capture; autoplay" 
            style="height: 540px; width: 100%; border: 0px;"
        ></iframe>
        """
        components.html(iframe_string, height=550)
else:
    st.info("💡 Pro-Tip: Simply enter an identical room name keyword tag on a second device or separate incognito tab window to instant link video layouts together.")
