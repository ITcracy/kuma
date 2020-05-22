import orjson
from queue import Empty

from jupyter_client import KernelManager, KernelClient

from app.backend.services.kuma.code_generator import PandasCodeGenerator


def execute_code(code: str, client: KernelClient):
    msg_id = client.execute(code, user_expressions={"str": "bytes"})
    state = "busy"
    data = {}
    while state != "idle" and client.is_alive():
        try:
            msg = client.get_iopub_msg(msg_id, timeout=1)
            # print(msg)
            if not "content" in msg:
                continue
            content = msg["content"]
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


if __name__ == "__main__":
    km = KernelManager()
    km.start_kernel()
    print(km.is_alive())
    try:
        c = km.client()

        execute_code("import pandas as pd", c)
        form = {"func": "read_csv", "args": ["tests/testdata/titanic.csv"], "mod": "pd"}
        code = PandasCodeGenerator(form, save=True).process()
        print(code)
        df = execute_code(code, c)
        print(df)
    except KeyboardInterrupt:
        pass
    finally:
        km.shutdown_kernel()
        print(km.is_alive())
