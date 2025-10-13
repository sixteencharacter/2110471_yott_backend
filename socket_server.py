from icecream import datetime
import uvicorn
import socketio
from services import sessionmanager
from sqlalchemy import select
from models import Person, Chat, Message
#Socket io (sio) create a Socket.IO server
sio=socketio.AsyncServer(cors_allowed_origins=[],allow_upgrades=True,async_mode='asgi')
#wrap with ASGI application
socket_app = socketio.ASGIApp(sio)

@sio.on("connect")
async def connect(sid, env):
    print("New Client Connected to This id :"+" "+str(sid))
    await sio.emit("send_msg", "Hello from Server")

@sio.on("disconnect")
async def disconnect(sid):
    print("Client Disconnected: "+" "+str(sid))
if __name__=="__main__":
    uvicorn.run("Soket_io:app", host="0.0.0.0", port=7777, lifespan="on", reload=True)

@sio.on('msg')
async def client_side_receive_msg(sid, msg):
    print("Msg receive from " +str(sid) +"and msg is : ",str(msg))
    await sio.emit("send_msg", str(msg))
    
@sio.on("Direct_Msg")
async def direct_msg(sid, data):
    """
        Expected data format:
        {
            "sender_id": "user123",
            "chat_id": "chat01",
            "message": "Hello!"
        }
    """
    sender_id = data["sender_id"]
    chat_id = data["chat_id"]
    message = data["message"]
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"Private message from {sender_id} -> {chat_id}: {message}")

    # Find receiver if online user finish we will implement
    # if receiver_id in online_users:
    #     receiver_sid = online_users[receiver_id]
    #     sio.emit("private_message", {
    #         "sender_id": sender_id,
    #         "message": message,
    #         "timestamp": eventlet.green.time.time()
    #     }, to=receiver_sid)
    # else:
    #     print(f"User {receiver_id} is offline")
    #     # Optionally save message in DB for later delivery
    # Create a proper Message model instance
    new_message = Message(
        sender_id=sender_id,
        chat_id=chat_id,
        content=message
    )
    
    async with sessionmanager.session() as db:
        db.add(new_message)
        await db.commit()
        
        # Get receiver ID 
        result = await db.execute(select(Person.uid).where(Person.id == chat_id).where(Person.id != sender_id))
        receiver_id = result.scalar_one_or_none()

    if not receiver_id:
        # Handle case where receiver is not found
        print(f"Receiver not found for chat_id: {chat_id}")
        return

    await sio.emit("Direct_Msg", {
            "sender_id": sender_id,
            "message": message,
            "timestamp": timestamp
        }, to=receiver_id)
