from typing import Union, Any


DELETE_OK: dict[str, bool] = {"ok": True}
RESPONSE_404: dict[Union[int, str], dict[str, Any]] = {
    404: {
        "description": "Item Not Found Error",
    },
}
