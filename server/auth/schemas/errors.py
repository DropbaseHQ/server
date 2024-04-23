from typing import Literal

from pydantic import BaseModel


class LanguageErrorResponse(BaseModel):
    status: Literal["success", "error"]
    type: Literal["sql", "python"]
    """Whether the error is in the SQL or Python code."""
    message: str
    """A high-level, short error message."""
    details: str | None
    """A more detailed error message, usually including a backtrace."""
