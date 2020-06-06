from typing import Any, Dict, List


class PandasCodeGenerator:
    def __init__(
        self,
        request: Dict[str, Any],
        save: bool = False,
        display_rows: int = 5,
        css_classes: List[str] = None,
        variable: str = "df",
    ):
        """
        Converts json request to code

        Parameters
        ----------
        request: dict
            A request dictionary containing all information related to code generation
            eg: {"mod": "pd", "func": "read_csv", "args": ["data.csv"], "kwargs": {"index_col": "id"}}
        save: bool, default False
            Whether or not to save the result of code execution to a variable
        display_rows: int, default 10
            Number of rows to be displayed in html format
        css_classes: list of str, default None
            List of classes to be applied to html table
        variable: str, default "df"
            Variable name to store the result.
        """
        self.request = request
        self.save = save
        self.display_rows = display_rows
        css_classes = " ".join(css_classes)
        self.css_classes = f'"{css_classes}"'
        self.variable = variable if save else "_current_state"

    def validate(self):
        """
        Checks for required keys in request dict

        Returns
        -------
        None
        Raises
        -------
        ValueError if required keys are not found
        """
        if not "func" in self.request:
            raise KeyError("'func' required.")
        if not isinstance(self.request.get("args", []), list):
            raise ValueError("'args' should be a list")
        if not isinstance(self.request.get("kwargs", {}), dict):
            raise ValueError("'kwargs' should be a dict")
        if "" in self.request.get("args", []):
            self.request["args"].remove("")

    def get_args(self) -> str:
        """
        Formats positional arguments from args key in request dict to str

        Returns
        -------
        str
        """
        args = [f'"{x}"' if isinstance(x, str) else f"{x}" for x in self.request.get("args", [])]
        return ", ".join(args)

    def get_kwargs(self) -> str:
        """
        Formats keyword args from kwargs key in request dict to str

        Returns
        -------
        str
        """
        kwargs = [
            f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
            for k, v in self.request.get("kwargs", {}).items()
        ]
        return ", ".join(kwargs)

    def call_args(self) -> str:
        """
        Combines args and kwargs as comma separated str

        Returns
        -------
        str
        """
        args = self.get_args()
        kwargs = self.get_kwargs()
        call_args = ", ".join([x for x in (args, kwargs) if x])
        return call_args

    def obj_or_module(self) -> str:
        """
        Validates mod key from request dict

        Returns
        -------
        None

        Raises
        -------
        ValueError if mod not in pd or df
        """
        mod = self.request.get("mod")
        if not mod:
            raise KeyError("'mod' required")
        if mod not in ["df", "pd"]:
            raise ValueError("Only 'df' of 'pd' mod is allowed")
        return mod

    def user_code(self) -> str:
        """
        Generates user specified code from request dict

        Returns
        -------
        str
        """
        mod = self.obj_or_module()
        func = self.request["func"]
        call_args = self.call_args()
        code = f"{self.variable} = {mod}.{func}({call_args})"
        return code

    def meta_code(self) -> str:
        """
        Generates additional code to display result

        Returns
        -------
            str
        """
        pd_html = (
            f"print({self.variable}.head({self.display_rows}).to_html("
            f"classes={self.css_classes}, show_dimensions=True))"
        )
        series_html = (
            f"print({self.variable}.to_frame().head({self.display_rows}).to_html("
            f"classes={self.css_classes}, show_dimensions=True))"
        )
        code = f"if isinstance({self.variable}, pd.DataFrame):"
        code = f"{code}\n\t{pd_html}"
        code = f"{code}\nelif isinstance({self.variable}, pd.Series):"
        code = f"{code}\n\t{series_html}"
        return code

    def process(self) -> str:
        """
        Combines code generated  by user_code and meta_code functions

        Returns
        -------
        str
        """
        self.validate()
        code = self.user_code()
        meta_code = self.meta_code()
        return f"{code}\n{meta_code}"
