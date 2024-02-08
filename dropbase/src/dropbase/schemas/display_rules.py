from typing import Any, List, Optional

from pydantic import BaseModel


class Rule(BaseModel):
    andor: Optional[str]
    target: str
    target_type: Optional[str]
    operator: str
    value: Any


class ComponentDisplayRules(BaseModel):
    component: str
    rules: List[Rule]


class DisplayRules(BaseModel):
    display_rules: List[ComponentDisplayRules]
