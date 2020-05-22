import inspect
import orjson
from typing import Any, Callable, Dict

from loguru import logger


class Inspector:
    def __init__(self, obj: Any, save: bool = False):
        self.obj = obj
        self.save = save

    @property
    def functions(self) -> Dict[str, Dict]:
        try:
            members = inspect.getmembers(self.obj, inspect.isfunction)
        except NotImplementedError as ni:
            logger.warning(
                "Not supported due to below error\n"
                f"{ni}\n"
                f"Trying to extract from class of obj i.e. from {self.obj.__class__}"
            )
            members = inspect.getmembers(self.obj.__class__, inspect.isfunction)
        result = {
            member[0]: Inspector.get_default_args(member[1])
            for member in members
            if Inspector.is_public(member[0])
        }
        return result

    @staticmethod
    def is_public(obj: str):
        return True if not obj.startswith("_") else False

    @staticmethod
    def get_default_args(func: Callable) -> Dict:
        if not callable(func):
            raise TypeError(f"{func} is not a callable object")
        signature = inspect.signature(func)
        args = {}
        for k, v in signature.parameters.items():
            if v.default is inspect.Parameter.empty:
                args[k] = v.kind.name
            else:
                args[k] = v.default
        try:
            orjson.dumps(args)
            return args
        except:
            logger.warning(f"Ignoring {args} as it is not json compatible")
