from typing import Optional

from pydantic import BaseModel


class Onboarding(BaseModel):
    email: str
    first_name: str
    last_name: str
    use_case: str
    company: Optional[str]
    notes: Optional[str]
