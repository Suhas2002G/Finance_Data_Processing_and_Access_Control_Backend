def success_response(message: str, data: dict = None):
    return {
        "success": True,
        "message": message,
        "data": data or {},
        "error": None
    }


def error_response(message: str, error: str = None):
    return {
        "success": False,
        "message": message,
        "data": {},
        "error": error
    }

