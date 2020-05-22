from typing import Any, Dict


class PandasCodeGenerator:
    def __init__(self, request: Dict[str, Any], save: bool = False, display_rows: int = 5):
        """
        Converts json request to code

        :param request: Dict
        """
        self.request = request
        self.save = save
        self.display_rows = display_rows

    def validate(self):
        if not "func" in self.request:
            raise KeyError("'func' required.")
        if not isinstance(self.request.get("args", []), list):
            raise ValueError("'args' should be a list")
        if not isinstance(self.request.get("kwargs", {}), dict):
            raise ValueError("'kwargs' should be a dict")
        if "" in self.request.get("args", []):
            self.request["args"].remove("")

    def get_args(self) -> str:
        args = [f'"{x}"' if isinstance(x, str) else f"{x}" for x in self.request.get("args", [])]
        return ", ".join(args)

    def get_kwargs(self) -> str:
        kwargs = [
            f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
            for k, v in self.request.get("kwargs", {}).items()
        ]
        return ", ".join(kwargs)

    def call_args(self) -> str:
        args = self.get_args()
        kwargs = self.get_kwargs()
        call_args = ", ".join([x for x in (args, kwargs) if x])
        return call_args

    def obj_or_module(self) -> str:
        mod = self.request.get("mod")
        if not mod:
            raise KeyError("'mod' required")
        if mod not in ["df", "pd"]:
            raise ValueError("Only 'df' of 'pd' mod is allowed")
        return mod

    def full_code(self) -> str:
        mod = self.obj_or_module()
        func = self.request["func"]
        call_args = self.call_args()
        code = f"{mod}.{func}({call_args})"
        if self.save:
            code = self.post_code(code, "df")
        else:
            code = self.post_code(code, "current_state")
        return code

    def post_code(self, code: str, var: str) -> str:
        code = f"{var} = {code}"
        css_classes = '"table is-fullwidth is-hoverable"'
        pd_html = f"print({var}.head({self.display_rows}).to_html(classes={css_classes}, show_dimensions=True))"
        series_html = f"print({var}.to_frame().head({self.display_rows}).to_html(classes={css_classes}, show_dimensions=True))"
        code = f"{code}\nif isinstance({var}, pd.DataFrame):"
        code = f"{code}\n\t{pd_html}"
        code = f"{code}\nelif isinstance({var}, pd.Series):"
        code = f"{code}\n\t{series_html}"
        return code

    def process(self) -> str:
        self.validate()
        return self.full_code()
