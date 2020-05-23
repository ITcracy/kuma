from queue import Empty

from jupyter_client.manager import start_new_async_kernel
from loguru import logger


class JupyterExecutor:
    @classmethod
    async def new(cls):
        self = JupyterExecutor()
        await self.start()
        await self._startup_code()
        return self

    async def start(self):
        self.manager, self.client = await start_new_async_kernel()

    async def _startup_code(self):
        code_str = "import pandas as pd"
        await self.execute(code_str)

    async def execute(self, code: str) -> str:
        msg_id = self.client.execute(code)
        state = "busy"
        data = {}
        while state != "idle" and await self.client.is_alive():
            try:
                msg = await self.client.get_iopub_msg(timeout=1)
                if not "content" in msg:
                    continue
                content = msg["content"]
                if msg["msg_type"] == "error":
                    logger.opt(exception=True).error("\n".join(content["traceback"]))
                if "data" in content:
                    data = content["data"]
                elif "text" in content:
                    data = content["text"]
                if "execution_state" in content:
                    state = content["execution_state"]
            except Empty:
                pass
        if "text/plain" in data:
            data = data["text/plain"]
        return data

    async def shutdown(self):
        await self.manager.shutdown_kernel()
        self.client.stop_channels()
