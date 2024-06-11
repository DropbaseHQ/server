# generated by datamodel-codegen:
#   filename:  <stdin>
#   timestamp: 2024-06-07T18:34:05+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class Table1ColumnsState(BaseModel):
    order_id: Optional[int] = Field(None, title="Order Id")
    user_id: Optional[int] = Field(None, title="User Id")
    product_name: Optional[str] = Field(None, title="Product Name")
    quantity: Optional[int] = Field(None, title="Quantity")
    total_price: Optional[float] = Field(None, title="Total Price")
    order_date: Optional[str] = Field(None, title="Order Date")


class Table1HeaderState(BaseModel):
    pass


class Table1FooterState(BaseModel):
    pass


class Table1State(BaseModel):
    columns: Table1ColumnsState
    header: Table1HeaderState
    footer: Table1FooterState


class Widget1ComponentsState(BaseModel):
    input1: Optional[str] = Field(None, title="Input1")


class Widget1State(BaseModel):
    components: Widget1ComponentsState


class State(BaseModel):
    table1: Table1State
    widget1: Widget1State


class Table1ColumnUpdate(BaseModel):
    new: Table1ColumnsState
    old: Table1ColumnsState
