# Standard library imports
import json
from datetime import date, datetime
from typing import Any

# Third-party imports
from fastapi.responses import JSONResponse


class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            default=self.custom_encoder,
            ensure_ascii=False
        ).encode("utf-8")

    @staticmethod
    def custom_encoder(obj):
        if isinstance(obj, (datetime, date)):
            return obj.strftime("%Y-%m-%d")   # <-- keep DB format
        return str(obj)


def standard_json_response(
    response=None,
    status_code=200,
    success=True,
    message="",
    data=None,
    metadata=None,
    error=None
):
    content = {
        "success": success,
        "message": message,
        "data": data,
        "metadata": metadata,
        "error": error
    }
    if response:
        response.status_code = status_code
        response.headers["content-type"] = "application/json"
        return content
    return CustomJSONResponse(
        status_code=status_code,
        content=content
    )
