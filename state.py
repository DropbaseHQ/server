# generated by datamodel-codegen:
#   filename:  <stdin>
#   timestamp: 2024-04-18T04:12:07+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Table1State(BaseModel):
    pass


class Widget1State(BaseModel):
    input1: Optional[str] = Field(None, title="Input1")


class State(BaseModel):
    table1: Table1State
    widget1: Widget1State
