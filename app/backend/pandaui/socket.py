from fastapi import APIRouter, WebSocket
from fastapi.responses import HTMLResponse
from jupyter_client import KernelClient, KernelManager
from loguru import logger
from starlette.websockets import WebSocketDisconnect

from app.backend.services.kuma.code_generator import PandasCodeGenerator
from app.backend.services.kuma.poc import execute_code

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
            <input type="text" id="modText" autocomplete="off"/>
            <input type="text" id="funcText" autocomplete="off"/>
            <input type="text" id="argText" autocomplete="off"/>
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
                var obj = {"func" : func.value, "mod": mod.value, "args": [arg.value]}
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
    km = KernelManager()
    km.start_kernel()
    c = km.client()
    execute_code("import pandas as pd", c)
    try:
        while True:
            data = await websocket.receive_json()
            code = PandasCodeGenerator(data, save=True, display_rows=15).process()
            df = execute_code(code, c)
            await websocket.send_text(f"{df}")
    except WebSocketDisconnect:
        logger.info(f"Client disconnected")
    finally:
        logger.info("Shuting down Kernel")
        km.shutdown_kernel()
