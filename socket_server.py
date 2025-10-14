import uvicorn
import socketio
from datetime import datetime
import requests
import jwt
import sys
import os

# เพิ่ม path เพื่อใช้ config
sys.path.append(os.getcwd())
from jwt import PyJWKClient
import config

#Socket io (sio) create a Socket.IO server
sio=socketio.AsyncServer(cors_allowed_origins=[],allow_upgrades=True,async_mode='asgi')
#wrap with ASGI application
socket_app = socketio.ASGIApp(sio)

user_count=0

unique_users = {}

@sio.on("connect")
async def connect(sid,env):
    print("New Client Connected to This id :"+" "+str(sid))
    

    # online_users[sid] = {
    #     'sid': sid,
    #     'connected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #     'user_name': f'{sid[:8]}',  # ชื่อชั่วคราว
    #     'status': 'online'
    # }

    print(f"จำนวนผู้ใช้ออนไลน์: {user_count} คน")

    # ส่งข้อความให้ส่ง token มา
    await sio.emit("sent_token", {"message": "Please send your token"}, room=sid)
    print("Sent sent_token to " + str(sid))
    await broadcast_user_list()

@sio.on("disconnect")
async def disconnect(sid):
    print("Client Disconnected: " + " " + str(sid))
    flag = 0
    
    if sid in unique_users:
        # user_info = online_users[sid]
        # keycloak_id = user_info.get('keycloak_id')
    
        # ลบ session
        name = unique_users[sid].get('username', f'ผู้ใช้_{sid[:8]}')
        del unique_users[sid]
        
        print(f"User {sid} disconnected and removed from unique users")
    for user in unique_users.values():
        if user.get('username') == name:
            flag = 1
            break

    if flag == 0:
        global user_count
        user_count -= 1

    await broadcast_user_list()

@sio.on('authenticate')  # event ใหม่สำหรับรับ token
async def authenticate(sid, token_data):
    """รับ token จาก client และอัพเดตข้อมูล user"""
    print(f"📨 Received authenticate from {sid}: {str(token_data)[:50]}...")
    # รับ token
    access_token = None
    if isinstance(token_data, dict):
        access_token = token_data.get('token')
    elif isinstance(token_data, str):
        access_token = token_data
    
    if not access_token:
        await sio.emit("auth_error", {"message": "No token provided"}, room=sid)
        return

    print(f"Processing token: {access_token[:50]}...")
    
    try:
        # ตรวจสอบ token format ก่อน
        if not access_token or len(access_token.split('.')) != 3:
            print("❌ Invalid token format")
            await sio.emit("auth_error", {"message": "Invalid token format"}, room=sid)
            return
        
        url = config.KC_CERT_URL
        optional_custom_headers = {"User-agent": "yott-backend-agent"}
        jwks_client = PyJWKClient(url, headers=optional_custom_headers)
            
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
                access_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=config.KC_CLIENT_AUD,
                options={"verify_exp": True},
            )
            
        print(f"✅ Token decoded successfully for: {data.get('preferred_username')}")
        
        # ดึงข้อมูลจาก token
        keycloak_id = data.get('sub')
        username = data.get('preferred_username', 'unknown')
        given_name = data.get('given_name', '')
        family_name = data.get('family_name', '')
        display_name = f"{given_name} {family_name}".strip() or username
        email = data.get('email', '')
        
        # ตรวจสอบว่าเป็น user ใหม่หรือไม่
        # is_new_user = username not in unique_users
        is_new_user = True
        for user in unique_users.values():
            if user.get('username') == username:
                is_new_user = False
                break
        
        
        if is_new_user:
            unique_users[sid] = {
                'keycloak_id': keycloak_id,
                'username': username,
                'display_name': display_name,
                'email': email
            }

            global user_count
            user_count += 1
            print(f"🆕 New unique user: {username}")
        elif sid in unique_users:
            print(f"🔄 User {username} reconnected with same SID")
        else:
            unique_users[sid] = {
                'keycloak_id': keycloak_id,
                'username': username,
                'display_name': display_name,
                'email': email
            }
            print(f"🔄 Existing user reconnected: {username}")
        

    except jwt.ExpiredSignatureError:
        print("❌ Token has expired")
        await sio.emit("auth_error", {"message": "Token has expired"})
        return
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token: {e}")
        await sio.emit("auth_error", {"message": f"Invalid token: {str(e)}"})
        return
    except Exception as e:
        print(f"❌ Error decoding token: {e}")
        await sio.emit("auth_error", {"message": f"Error: {str(e)}"})
        return

    await broadcast_user_list()

# @sio.on('disconnect_request')
# async def disconnect_request(sid):
#     await sio.disconnect(sid)   


# @sio.on('msg')
# async def client_side_receive_msg(sid, msg):
#     # user_info = online_users.get(sid, {})
#     user_name = user_info.get('user_name', f'ผู้ใช้_{sid[:8]}')
#     timestamp = datetime.now().strftime('%H:%M:%S')
    
#     print("Msg receive from " +str(sid) +"and msg is : ",str(msg))
#     await sio.emit("send_msg", {
#         'user_name': user_name,
#         'message': str(msg),
#         'timestamp': timestamp,
#         'user_id': sid[:8]
#     })
    
async def broadcast_user_list():
    """ส่งรายชื่อผู้ใช้ออนไลน์ให้ทุกคนแบบ real-time"""
    user_list = {
        'users': list(unique_users.values()),
        'total_count': user_count,
    }
    await sio.emit("online_users_update", user_list)


if __name__=="__main__":
    uvicorn.run("Soket_io:app", host="0.0.0.0", port=7777, lifespan="on", reload=True)
