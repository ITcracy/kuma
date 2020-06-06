import inspect
import orjson
from typing import Any, Callable, Dict

from docstring_parser import parse
from loguru import logger


class Inspector:
    def __init__(self, obj: Any, save: bool = False):
        """
        Inspects objects/class and returns related functions etc.

        Parameters
        ----------
        obj: Any object or class
        """
        self.obj = obj
        self._functions = None
        self.unique_types = set()

    @property
    def functions(self) -> Dict[str, Dict]:
        """
        Extracts all functions/methods in a module, class or object
        along with argument list and default values

        Returns
        -------
        Dict, a dictionary with keys as function name and values as dict with
        keys as argument name and value as default value or type
        """
        if not self._functions:
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
                member[0]: self.get_default_args(member[1])
                for member in members
                if Inspector.is_public(member[0])
            }
            self._functions = result
        return self._functions

    @staticmethod
    def is_public(obj: str) -> bool:
        """
        Filter function to get only public functions

        Parameters
        ----------
        obj: str, name of function

        Returns
        -------
        bool
        """
        return True if not obj.startswith("_") else False

    def get_default_args(self, func: Callable) -> Dict:
        """
        Extracts arguments and its default values from a function

        Parameters
        ----------
        func: Callable

        Returns
        -------
        Dict
        """
        if not callable(func):
            raise TypeError(f"{func} is not a callable object")
        signature = inspect.signature(func)
        doc = inspect.getdoc(func)
        parsed_doc = parse(doc)
        parameter_types = {
            param.arg_name: param.type_name.split(", default")[0] if param.type_name else None
            for param in parsed_doc.params
        }
        self.unique_types = self.unique_types.union(set(parameter_types.values()))
        args = {
            k: {
                "type_name": parameter_types.get(k),
                "default": v.kind.name if v.default is inspect.Parameter.empty else v.default,
            }
            for k, v in signature.parameters.items()
        }
        try:
            orjson.dumps(args)
            return args
        except:
            logger.warning(f"Ignoring {func}\n{args} as it is not json compatible")
