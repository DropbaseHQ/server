from fastapi import HTTPException


def raise_http_exception(status_code: int, message: str):
    raise HTTPException(status_code=status_code, detail=message)
