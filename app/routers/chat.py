from fastapi import WebSocket,APIRouter,WebSocketDisconnect,status,HTTPException,Depends
from fastapi.responses import HTMLResponse
import JWTtoken,database,models
from sqlalchemy.orm import Session
router = APIRouter(
    tags=['Chat']
)

active_connections: dict[str, WebSocket] = {}

html = """
<!DOCTYPE html>
<html>
  <body>
    <input id="msg" placeholder="Type a message">
    <button onclick="sendMessage()">Send</button>

    <ul id="messages"></ul>

    <script>
      let socket;

      function connect() {
        const username = document.getElementById("username").value;
        socket = new WebSocket(`ws://localhost:8000/ws?token=YOUR_ACCESS_TOKEN`);


        socket.onmessage = function(event) {
          const messages = document.getElementById("messages");
          const li = document.createElement("li");
          li.textContent = event.data;
          messages.appendChild(li);
        };
      }

      function sendMessage() {
        const input = document.getElementById("msg");
        socket.send(input.value);
        input.value = "";
      }
    </script>
  </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)

@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(database.get_db)):
    token = websocket.query_params.get('token')
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    token_data = JWTtoken.verify_token(token,HTTPException(status_code=401, detail="Invalid token")) 
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        await websocket.close()
        return
    
    username = user.username 
    await websocket.accept()
    
   