from pathlib import Path
from typing import Any, Dict
import pandas as pd


class TypeMapper:
    def __init__(self, mapping_file: Path):
        self.mapping_file = mapping_file
        self.mapping = self._load_types()

    def _load_types(self) -> Dict[str, Any]:
        df = pd.read_csv(self.mapping_file)
        df = df.set_index("types")
        data = df.to_dict(orient="index")
        return data
