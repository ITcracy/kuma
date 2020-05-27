from typing import Any, Dict

import pandas as pd

from .code_generator import PandasCodeGenerator
from .storage import NotebookStorageBackend
from .inspector import Inspector


class KumaSession:
    def __init__(self):
        """
        Represents a session of Kuma, its main responsibility is to maintain
        a jupyter notebook with each cell representing user code.
        """
        self.store = NotebookStorageBackend()

    def code(self, request: Dict[str, Any], save: bool = False, display_rows: int = 5) -> str:
        """
        Generates code from request using PandasCodeGenerator class and
        stores user code in notebook based on 'save' argument.

        Parameters
        ----------
        request: dict
            A request dictionary containing all information related to code generation
            eg: {"mod": "pd", "func": "read_csv", "args": ["data.csv"], "kwargs": {"index_col": "id"}}
        save: bool, default False
            Whether or not to save the result of code execution to a variable
        display_rows: int, default 10
            Number of rows to be displayed in html format

        Returns
        -------
        str, user code along with meta code.

        """
        code_gen = PandasCodeGenerator(request, save, display_rows, ["table", "is-fullwidth"])
        if save:
            user_code = code_gen.user_code()
            self.store.step(code=user_code)
        return code_gen.process()

    @property
    def df_functions(self) -> Dict[str, Dict]:
        """
        Using Inspector class, it returns dictionary of functions with
        its arguments under a Dataframe class.

        Returns
        -------
        dict
        """
        inspector = Inspector(pd.DataFrame)
        return inspector.functions

    @property
    def pd_functions(self) -> Dict[str, Dict]:
        """
        Using Inspector class, it returns dictionary of functions with
        its arguments under pandas module.

        Returns
        -------
        dict
        """
        inspector = Inspector(pd)
        return inspector.functions

    def save(self, file_path: str):
        """
        Saves notebook to given file path

        Parameters
        ----------
        file_path: str
            Relative or absolute path of file
        """
        self.store.save(file_path)
