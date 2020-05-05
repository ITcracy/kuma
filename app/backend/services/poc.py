import inspect
from typing import Callable, List, Mapping, Union

import pandas as pd


def json_to_pandas(form: dict, mod=pd):
    func = getattr(mod, form["func"])
    return func(*form.get("args", []), **form.get("kwargs", {}))


def get_code(form: dict, mod):
    if not isinstance(mod, str):
        try:
            mod = mod.__name__
            if mod == "pandas":
                mod = "pd"
        except AttributeError:
            mod = "df"
    args = [f'"{x}"' if isinstance(x, str) else f"{x}" for x in form.get("args", [])]
    args = ", ".join(args)
    kwargs = ", ".join([f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}" for k, v in form.get("kwargs", {}).items()])
    call_args = ", ".join([x for x in (args, kwargs) if x])
    code = f"{mod}.{form['func']}({call_args})"
    print(code)
    return code


def get_default_args(func: Callable) -> Mapping:
    if not callable(func):
        raise TypeError(f"{func} is not a callable object")
    signature = inspect.signature(func)
    args = {}
    for k, v in signature.parameters.items():
        if v.default is inspect.Parameter.empty:
            args[k] = v.kind.name
        else:
            args[k] = v.default
    return args


def run_code(code: Union[str, List[str]]):
    return eval(code)


def execute(form: dict, mod):
    code = get_code(form, mod)
    res = run_code(code)
    print(res)
    return res


if __name__ == "__main__":
    form = {
        "func": "read_csv",
        "args": ["tests/testdata/titanic.csv"],
    }
    df = execute(form, pd)
    form = {"func": "describe"}
    execute(form, df)
