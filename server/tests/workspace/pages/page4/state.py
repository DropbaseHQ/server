# generated by datamodel-codegen:
#   filename:  <stdin>
#   timestamp: 2024-06-11T20:32:26+00:00

from __future__ import annotations

from pydantic import BaseModel


class Table1ColumnsState(BaseModel):
    pass


class Table1HeaderState(BaseModel):
    pass


class Table1FooterState(BaseModel):
    pass


class Table1State(BaseModel):
    columns: Table1ColumnsState
    header: Table1HeaderState
    footer: Table1FooterState


class Widget1ComponentsState(BaseModel):
    pass


class Widget1State(BaseModel):
    components: Widget1ComponentsState


class State(BaseModel):
    table1: Table1State
    widget1: Widget1State


class Table1ColumnUpdate(BaseModel):
    new: Table1ColumnsState
    old: Table1ColumnsState
