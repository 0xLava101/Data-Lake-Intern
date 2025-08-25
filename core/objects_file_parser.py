# core/objects_file_parser.py

from pydantic import BaseModel , field_validator
from pathlib import Path
import json

from utils.logger import Logger

logger = Logger().set_logger()

class Objects_JsonFile(BaseModel): 
    limit : int | None
    categories : dict[str , list[str]]

    @classmethod
    def from_file(cls, path: str):
        text = Path(path).read_text(encoding="utf-8")
        try:
            return cls.model_validate_json(text)
        except Exception:
            return cls.model_validate(json.loads(text))
        
    @field_validator("categories")
    def check_non_empty_lists(cls, v):
        for key, items in v.items():
            if not items:  
                raise ValueError(f"Category '{key}' must not be empty")
        return v