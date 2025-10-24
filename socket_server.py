from utils import validate_accessToken_without_raise
import socketio
from services import sessionmanager
from sqlalchemy import select
from models import Person , Chat , user_belong_to_chat , Message
from typing import Dict 
from datetime import datetime
from services import kc_socketio_cache

# Socket IO server instance 
sio = socketio.AsyncServer(cors_allowed_origins=[],allow_upgrades=True,async_mode='asgi')

# ASGI application ready to be mounted with the FastAPI
socket_app = socketio.ASGIApp(sio)

class SocketIOManager :

    def __init__(self) :
        self.user_counter : int = 0
        self.user_mapper : Dict[str,Dict[str,any]] = dict()

    def add_client(self,cid : str , decoded_data : dict) :
        self.user_mapper[cid] = decoded_data
        self.user_counter += 1

    def get_all_available_clients(self) :
        return set([u["sub"] for u in self.user_mapper.values()])

    def remove_client(self,cid) :
        del self.user_mapper[cid]
        self.user_counter -= 1

    def get_user_count(self) :
        return self.user_counter
    
    def isOnline(self,sid : str) :
        return sid in self.user_mapper
    
    def getUserWithSID(self,sid : str) :
        if sid in self.user_mapper :
            return self.user_mapper[sid]
        else :
            return None

client_manager = SocketIOManager()

@sio.on("connect")
async def connect(sid,env):
    # authentication
    try :
        # extract auth token from the asgi scope
        authToken = [e for e in env['asgi.scope']['headers'] if e[0] == b"authorization"][0][1].decode("utf-8").replace("Bearer","").strip()
    except :
        authToken = "Failed Token"
    userData , err = await validate_accessToken_without_raise(authToken,kc_socketio_cache)
    if err is not None :
        await sio.disconnect(sid)
    else :
        client_manager.add_client(sid,userData)
    await broadcast_user_list()

    
@sio.on("disconnect")
async def disconnect(sid):

    if client_manager.isOnline(sid) :
        client_manager.remove_client(sid)

    await broadcast_user_list()


async def broadcast_user_list():
 
    async with sessionmanager.session() as db:
        result = await db.execute(
            select(Person.uid, Person.preferred_username, Person.given_name, Person.family_name, Person.email)
        )
        user_db_rows = result.fetchall()
        
    all_users = dict()

    for row in user_db_rows:
        uid, username, given_name, family_name, email = row
        display_name = f"{given_name or ''} {family_name or ''}".strip() or username
        all_users[uid] = {
            'uid': uid,
            'username': username,
            'given_name': given_name,
            'family_name': family_name,
            'display_name': display_name,
            'email': email,
            'status': 'offline'  
        }

    online_clients = client_manager.get_all_available_clients()
    
    for user in all_users:
        if(user in online_clients):
            all_users[user]['status'] = 'online'
        

    user_list = {
        'users': list(all_users.values()),
        'total_count': client_manager.get_user_count(),
    }

    await sio.emit("online_users_update", user_list)
    
    
@sio.on('create_chat')
async def create_chat(sid, chat_data):
    """
    chat_data ควรมีโครงสร้างดังนี้:
    {
        "chat_name": "ชื่อแชท",
        "is_groupchat": True/False,
        "member_ids": ["user_id1", "user_id2", ...]  # รายชื่อ user IDs ที่จะเข้าร่วมแชท
    }
    """
    chat_name = chat_data.get("chat_name", "Unnamed Chat")
    is_groupchat = chat_data.get("is_groupchat", False)
    member_ids = chat_data.get("member_ids", [])

    if not client_manager.isOnline(sid) :
        await sio.emit("chat_creation_error", {"message": "User not authenticated"}, room=sid)
        return
    
    creator = client_manager.getUserWithSID(sid)
    creator_id = creator["sub"]
    
    if creator_id not in member_ids:
        member_ids.append(creator_id)  # ให้แน่ใจว่า creator อยู่ในแชทด้วย
    
    try:
        async with sessionmanager.session() as db:
            if not is_groupchat:
                # Check if DM already exists between these users
                user_groupchat = await db.execute(
                    select(user_belong_to_chat.cid)
                    .join(Chat, Chat.cid == user_belong_to_chat.cid)
                    .where(
                        user_belong_to_chat.uid == creator_id,
                        Chat.is_groupchat == False  # Fixed: should be False, not creator_id
                    )
                )
                user_groupchat_result = user_groupchat.scalars().all()

                if user_groupchat_result:
                    existing_user_dm = await db.execute(
                        select(user_belong_to_chat.uid)
                        .where(user_belong_to_chat.cid.in_(user_groupchat_result))
                        .where(user_belong_to_chat.uid != creator_id)
                    )
                    existing_dms = existing_user_dm.scalars().all()
                    partner_ids = [uid for uid in member_ids if uid != creator_id]
                    if partner_ids[0] in existing_dms:
                        await sio.emit("handle_1_dm_exists", {"message": "Direct message already exists between these users."}, room=sid)
                        return

            # สร้างแชทใหม่
            new_chat = Chat(name=chat_name, is_groupchat=is_groupchat)
            print("new_chat:", new_chat)
            db.add(new_chat)
            await db.flush()  # เพื่อให้ได้ chat ID
            
            # เก็บค่าที่ต้องการใช้ก่อนออกจาก session
            chat_id = new_chat.cid
            chat_name_final = new_chat.name
            is_groupchat_final = new_chat.is_groupchat
            
            # เพิ่มสมาชิกในแชท
            for member_id in member_ids:
                user_b2c = user_belong_to_chat(uid=member_id, cid=chat_id)
                db.add(user_b2c)
            
            await db.commit()
        
        # print(f"✅ Chat '{chat_name_final}' created with ID {chat_id}")
        await sio.emit("chat_created", {
            "cid": chat_id,
            "name": chat_name_final,
            "is_groupchat": is_groupchat_final,
            "member_ids": member_ids
        }, room=str(chat_id))
        
    except Exception as e:
        print(f"❌ Error creating chat: {e}")
        await sio.emit("chat_creation_error", {"message": f"Error: {str(e)}"}, room=sid)

@sio.on('join_chat')
async def join_chat(sid, cid):
    await sio.enter_room(sid, cid)
    print(f"User {sid} joined chat room {cid}")
    await sio.emit("user_joined", {"user_id": sid}, room=cid)

@sio.on('leave_chat')
async def leave_chat(sid, cid):
    await sio.leave_room(sid, cid)
    print(f"User {sid} left chat room {cid}")
    await sio.emit("user_left", {"user_id": sid}, room=cid)

@sio.on('msg')
async def client_side_receive_msg(sid, msg):
    print("Msg receive from " +str(sid) +"and msg is : ",str(msg))
    await sio.emit("send_msg", str(msg))
    
@sio.on("send_message")
async def send_message(sid, data):
    """
        Expected data format:
        {
            "cid": "chat_id",
            "message": "Hello!"
        }
    """
    creator = client_manager.getUserWithSID(sid)
    creator_id = creator["sub"]

    chat_id = data["cid"]
    message = str(data["message"])
    print(f"Private message from {creator_id} -> {chat_id}: {message}")

    # Create a proper Message model instance
    new_message = Message(
        s_id=creator_id,
        data=message,
        cid=chat_id,
    )
    try:
        async with sessionmanager.session() as db:
            db.add(new_message)
            await db.flush()
            timestamp = new_message.timestamp.isoformat()
            await db.commit()
        await sio.emit("receive_msg", {
                "s_id": creator_id,
                "s_name" : creator["preferred_username"],
                "message": message,
                "timestamp": timestamp,
                "cid": chat_id
            }, room=chat_id)
    except Exception as e:
        print(f"❌ Error saving message: {e}")
        await sio.emit("message_error", {"message": f"Error: {str(e)}"}, room=sid)
        return