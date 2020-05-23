from typing import Any, Dict

import pandas as pd

from .code_generator import PandasCodeGenerator
from .storage import NotebookStorageBackend
from .inspector import Inspector


class KumaSession:
    def __init__(self):
        self.store = NotebookStorageBackend()

    def code(self, request: Dict[str, Any], save: bool = False, display_rows: int = 5):
        code_gen = PandasCodeGenerator(request, save, display_rows, ["table", "is-fullwidth"])
        if save:
            user_code = code_gen.user_code()
            self.store.step(code=user_code)
        return code_gen.process()

    @property
    def df_functions(self) -> Dict[str, Dict]:
        inspector = Inspector(pd.DataFrame)
        return inspector.functions

    @property
    def pd_functions(self) -> Dict[str, Dict]:
        inspector = Inspector(pd)
        return inspector.functions

    def save(self, file_path: str):
        self.store.save(file_path)
