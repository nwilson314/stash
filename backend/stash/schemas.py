from typing import Union, Any

from pydantic import BaseModel


DELETE_OK: dict[str, bool] = {"ok": True}
RESPONSE_404: dict[Union[int, str], dict[str, Any]] = {
    404: {
        "description": "Item Not Found Error",
    },
}

class LinkCreate(BaseModel):
    url: str
    note: str = None
