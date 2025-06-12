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
    <h2>Login</h2>
    <input id="email" placeholder="Enter your email">
    <input id="password" type="password" placeholder="Enter your password">
    <button onclick="login()">Login</button>
    <button onclick="connect()">Connect</button> <!-- <-- This was missing -->

    <h2>Chat</h2>
    <input id="msg" placeholder="Type a message">
    <button onclick="sendMessage()">Send</button>

    <ul id="messages"></ul>

    <script>
      let token = "";
      let socket;

      async function login() {
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const response = await fetch("http://localhost:8000/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: `username=${encodeURIComponent(email)}&password=${encodeURIComponent(password)}`
        });

        const data = await response.json();
        console.log("Received login response:", data);
        token = data.access_token;
        localStorage.setItem("token", token); 
        alert("Login successful! Now click Connect.");
      }

      function connect() {
        const storedToken = localStorage.getItem("token");
        if (!storedToken) {
          alert("Please login first");
          return;
        }

        socket = new WebSocket(`ws://localhost:8000/ws?token=${storedToken}`);

        socket.onmessage = function(event) {
          const messages = document.getElementById("messages");
          const li = document.createElement("li");
          li.textContent = event.data;
          messages.appendChild(li);
        };

        socket.onopen = function () {
          console.log("WebSocket connection opened");
        };

        socket.onclose = function () {
          console.log("WebSocket connection closed");
        };
      }

      function sendMessage() {
        const input = document.getElementById("msg");
        if (socket && socket.readyState === WebSocket.OPEN) {
          socket.send(input.value);
          input.value = "";
        } else {
          alert("WebSocket is not connected");
        }
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
    print(f'username : {type(username)}')
    await websocket.accept()
    
    active_connections[username] = websocket
    print(f"[CONNECTED] {username} connected")
    
    try:
        while True:
            data = await websocket.receive_text()
            print(f"{username} sent: {data}")
            for tempuser,conn in active_connections.items():
                if tempuser != username:
                    await conn.send_text(f'{username}: {data}')
    except WebSocketDisconnect:
        del active_connections[username]
        print(f"[DISCONNECTED] {username} left")
