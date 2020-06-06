import abc

import nbformat.v4 as notebook
from nbformat import write as write_notebook, read as read_notebook


class FileStorageBackendInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "step")
            and callable(subclass.step)
            and hasattr(subclass, "fetch_step")
            and callable(subclass.fetch_step)
            and hasattr(subclass, "save")
            and callable(subclass.save)
            or NotImplemented
        )

    @abc.abstractmethod
    def step(self, code: str) -> int:
        """
        Save steps into some kind of store
        :param code: Code to store eg. df = pd.read_csv("file.csv")
        :return: Identifier step number
        """
        raise NotImplementedError

    @abc.abstractmethod
    def fetch_steps(self, start: int = None, end: int = None) -> str:
        """
        Get steps in order from store for given uuid
        :param identifier: Step number to identify the store
        :return: Code in string format
        """
        raise NotImplementedError

    @abc.abstractmethod
    def save(self, file_name: str):
        """
        Save file
        :param file_name: File path
        :return: None
        """
        raise NotImplementedError


class NotebookStorageBackend(FileStorageBackendInterface):
    def __init__(self, path_to_notebook: str = None):
        """
        Storage backend using jupyter notebook as store
        """
        if path_to_notebook:
            self.notebook = read_notebook(path_to_notebook, as_version=4)
        else:
            self.notebook = notebook.new_notebook()
            self.notebook["cells"] = []

    def step(self, code: str) -> int:
        """
        Takes user code and writes to a cell of notebook

        Parameters
        ----------
        code: str

        Returns
        -------
        int, index position of code in notebook

        """
        self.notebook["cells"].append(notebook.new_code_cell(code))
        return len(self.notebook["cells"]) - 1

    def fetch_steps(self, start: int = None, end: int = None) -> str:
        """
        Fetches a range of steps based on start and end index.

        Parameters
        ----------
        start: int
        end: int

        Returns
        -------
        str,
        """
        cells = self.notebook["cells"][start:end]
        code = [cell["source"] for cell in cells]
        return "\n".join(code)

    def save(self, file_path: str):
        """
        Saves code to a notebook

        Parameters
        ----------
        file_path: Path to file
        """
        if not file_path.endswith(".ipynb"):
            raise TypeError("Incorrect file extension for python notebook")
        write_notebook(self.notebook, file_path)
