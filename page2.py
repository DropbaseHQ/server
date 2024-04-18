from pydantic import BaseModel

from dropbase.models.table import PyColumnDefinedProperty, TableDefinedProperty
from dropbase.models.widget import ButtonDefinedProperty, InputDefinedProperty, WidgetDefinedProperty


class PageProperties(BaseModel):
    table1: TableDefinedProperty
    widget1: WidgetDefinedProperty


table1_columns = [
    PyColumnDefinedProperty(name="id", data_type="int64", display_type="integer"),
    PyColumnDefinedProperty(name="name", data_type="object", display_type="text"),
    PyColumnDefinedProperty(name="age", data_type="int64", display_type="integer"),
    PyColumnDefinedProperty(name="created_at", data_type="object", display_type="text"),
]
table1 = TableDefinedProperty(label="Table 1", name="table1", columns=table1_columns)
widget1 = WidgetDefinedProperty(
    label="Widget 1",
    name="widget1",
    components=[
        ButtonDefinedProperty(label="Button 1", name="button1"),
        InputDefinedProperty(label="Input 1", name="input1", data_type="text"),
    ],
)
page = PageProperties(table1=table1, widget1=widget1)
