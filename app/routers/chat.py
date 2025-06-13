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
  <style>
    body {
      background-color: #f3f4f6;
      font-family: sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      margin: 0;
    }

    .container {
      background: #fff;
      padding: 24px;
      border-radius: 16px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
      width: 100%;
      max-width: 400px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    h2 {
      margin-bottom: 16px;
      color: #1f2937;
    }

    input {
      width: 90%;
      padding: 10px 12px;
      margin-bottom: 12px;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      font-size: 14px;
    }

    button {
      padding: 10px;
      font-size: 14px;
      font-weight: bold;
      border: none;
      border-radius: 8px;
      cursor: pointer;
    }

    .btn-primary {
      background-color: #3b82f6;
      color: white;
      margin-right: 8px;
    }

    .btn-secondary {
      background-color: #6b7280;
      color: white;
    }

    .btn-send {
      background-color: #10b981;
      color: white;
      margin-left: 8px;
    }

    .btn-primary:hover {
      background-color: #2563eb; 
    }

    .btn-secondary:hover {
      background-color: #4b5563; 
    }

    .btn-send:hover {
      background-color: #059669; 
    }

    .chat-input {
      display: flex;
      align-items: center;
    }

    #messages {
      list-style-type: none;
      padding-left: 0;
      max-height: 150px;
      overflow-y: auto;
      margin-top: 12px;
    }

    #messages li {
      background: #f9fafb;
      padding: 8px;
      margin-bottom: 6px;
      border-radius: 6px;
      font-size: 14px;
    }
  </style>
  <body>
    <div class="container">
    <h2>Login</h2>
    <input id="email" placeholder="Enter your email" />
    <input id="password" type="password" placeholder="Enter your password" />
    <div style="display: flex; justify-content: space-between; margin-bottom: 24px;">
      <button class="btn-primary" onclick="login()">Login</button>
      <button class="btn-secondary" onclick="connect()">Connect</button>
    </div>

    <h2>Chat</h2>
    <div class="chat-input">
      <input id="msg" placeholder="Type a message" />
      <button class="btn-send" onclick="sendMessage()">Send</button>
    </div>

    <ul id="messages"></ul>
  </div>

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
