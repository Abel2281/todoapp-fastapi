from fastapi import WebSocket,APIRouter,WebSocketDisconnect
from fastapi.responses import HTMLResponse

router = APIRouter(
    tags=['Chat']
)

active_connections: dict[str, WebSocket] = {}

html = """
<!DOCTYPE html>
<html>
  <body>
    <input id="username" placeholder="Enter your name">
    <button onclick="connect()">Connect</button><br><br>
    
    <input id="msg" placeholder="Type a message">
    <button onclick="sendMessage()">Send</button>

    <ul id="messages"></ul>

    <script>
      let socket;

      function connect() {
        const username = document.getElementById("username").value;
        socket = new WebSocket(`ws://localhost:8000/ws/${username}`);

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

@router.websocket('/ws/{username}')
async def websocket_endpoint(websocket: WebSocket, username:str):
    await websocket.accept()
    active_connections[username] = websocket
    try:
        while True:
            data = await websocket.receive_text()
            for user,connection in active_connections.items():
                if connection != websocket:
                    await connection.send_text(f'username is {data}')
    except WebSocketDisconnect:
        del active_connections[username]

