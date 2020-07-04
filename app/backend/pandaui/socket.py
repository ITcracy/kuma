from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
from loguru import logger
from starlette.websockets import WebSocketDisconnect

from app.backend.core.config import app_config
from app.backend.services.kuma.main import KumaSession
from app.backend.services.kuma.executor import JupyterExecutor

router = APIRouter()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma@0.8.2/css/bulma.min.css">
        <script defer src="https://use.fontawesome.com/releases/v5.3.1/js/all.js"></script>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="modText" autocomplete="on" placeholder="Module or Var"/>
            <input type="text" id="funcText" autocomplete="on" placeholder="Function"/>
            <input type="text" id="argText" autocomplete="on" placeholder="args"/>
            <input type="checkbox" id="save" name="save" value="save">
            <button>Send</button>
        </form>
        <div id='messages'>
        </div>
        <script>
            var ws = new WebSocket("ws://localhost:8000/api/pandaui/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('div')
                message.innerHTML += event.data
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var mod = document.getElementById("modText")
                var func = document.getElementById("funcText")
                var arg = document.getElementById("argText")
                var kwargs = document.getElementById("kwargText")
                var save = document.getElementById("save")
                var obj = {"func" : func.value, "mod": mod.value, "args": [arg.value], "save": save.checked}
                ws.send(JSON.stringify(obj))
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session = KumaSession()
    executor = await JupyterExecutor.new()
    try:
        while True:
            data = await websocket.receive_json()
            save = data["save"]
            code = session.code(data, save=save, display_rows=10)
            result = await executor.execute(code)
            await websocket.send_text(f"{result}")
    except WebSocketDisconnect:
        logger.info("Client disconnected")
    finally:
        logger.info("Shutting down Kernel")
        await executor.shutdown()
        session.save(f"{app_config.DATA_DIR}/untitled.ipynb")
