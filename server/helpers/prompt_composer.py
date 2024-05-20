from server.controllers.sources import get_env_vars, get_source_name_type


def get_ui_prompt(base_path: str, user_prompt: str):
    with open(base_path + "properties.json", "r") as file:
        props = file.read()
    return f"""Follow the user prompt to modify properties.json file

properties.json:
{props}

Useful notes:
- Tables and widgets are the highest level objects
- Add as many tables or widgets as specified in the user prompt; uniquely name each
- Table, widget and component names MUST be lowercase and alphanumeric; however, their labels can be any string that's human readable
- Tables have columns of various types
- Each table can have at most one header and one footer
- Headers and footers can contain components such as inputs, buttons, selects/dropdowns, boolean/toggles, and text displays
- Widgets contains components such as inputs, buttons, selects/dropdowns, boolean/toggles, and text displays
- Action columns, row actions, button columns are used interchangeably
- Each table, widget, component, and column properties MUST be validated against the following python models:
{component_models}

User prompt:
{user_prompt}.

Only return json. nothing else. no markdown format
If a user needs to rename or update components, modify their label, not their name, unless user insists.
"""


def get_func_prompt(base_path: str, user_prompt: str):
    # read files
    with open(base_path + "scripts/main.py", "r") as file:
        main_str = file.read()
    with open(base_path + "state.py", "r") as file:
        state_str = file.read()
    with open(base_path + "context.py", "r") as file:
        context_str = file.read()

    sources = get_source_name_type()
    sources_list = "\n".join([f"{s['name']}: {s['type']}" for s in sources])

    env_vars = get_env_vars()
    env_vars_str = ", ".join(env_vars)

    return f"""Given state.py:
'''python
{state_str}
'''
and context.py:
'''python
{context_str}
'''

follow the user prompt to update this main.py:
'''python
{main_str}
'''

these are the database names available along with their types:
name: type
{sources_list}

to query a database, use a connect object from the database module. example:
```python
from dropbase.database.connect import connect
db = connect("database_name")
table_data = db.query("select * from table_name")
# MUST convert the data to a pandas dataframe before assigning it to the context with the to_dtable() method
table_df = df(table_data)
context.table1.data = table_df.to_dtable()
```
or to execute a query
```python
db.execute("insert into table_name values (1, 'name')")
```

these are the environment variables available, which include api keys:
{env_vars_str}
to use them, declare them in main.py using os.getenv() 

Useful notes:
- To query data or interact with data sources, default to using the available databases or env variables
- Tables have methods for get, add, update, delete, and on row change; only update the methods that correspond to what the user asks for
- Inputs have a method for on submit, booleans for on toggle, buttons for on click, select dropdowns for on select
- Table state contains the selected row for a specific table; each of the values in the state object is a column
- Context state contains all the inputs currently entered by a user in various Dropbase UI/client components
- Context contains information used by the Dropbase UI to display components/data as well as component or column visibility and messages
- The data attribute in context contains data to be displayed in a table component in the Dropbase UI/client
- To pass/display data to any table, first compose a pandas dataframe and then format it with to_dtable() before assigning it to the table's data attribute in its context; assume to_dtable() already exists
- Any data sent to Dropbase tables MUST be formatted correctly by calling "to_dtable()"
- Column names in tables should not have spaces: only underscores, lowercase, and alphanumeric are allowed
- Tables can have one header and/or one footer. Headers and footers can have various components, including text, input, select dropdowns, buttons, and boolean toggles
- Header and footer methods should be defined inside the corresponding table class
- To display a modal, set a model widget's visibility to True
- Use page context exclusively for passing/displaying messages to the user. this is the preferred way to show user messages
- Import any python sdk needed to perform the task, but don't modify or delete existing import statements
- By default, Dropbase UI/client sends dates as a string in Unix epoch

User prompt:
{user_prompt}.

ONLY return the code for a new main.py file, nothing else.
ONLY make code changes to in the corresponding class methods that matches the user prompt
"""


component_models = """color_options = Literal["red", "blue", "green", "yellow", "gray", "orange", "purple"]

class Boolean(BaseModel):
    component_type: Literal["boolean"]
    name: str
    label: str
    default: Optional[Any] = False
    display_rules: Optional[List[dict]]
    data_type: Literal["boolean"] = "boolean"

class Button(BaseModel):
    component_type: Literal["button"]
    name: str
    label: str
    color: Optional[color_options]
    display_rules: Optional[List[dict]]


class Input(BaseModel):
    component_type: Literal["input"]
    name: str
    label: str
    data_type: Literal["text", "integer", "float", "datetime", "date", "time"] = "text"
    placeholder: Optional[str]
    default: Optional[Any]
    multiline: Optional[bool] = False
    display_rules: Optional[List[dict]]

class SelectOptions(BaseModel):
    name: str
    value: Any

class Select(BaseModel):
    component_type: Literal["select"]
    name: str
    label: str
    data_type: Literal["string", "integer", "float", "boolean", "string_array"] = "string"
    options: Optional[List[SelectOptions]]
    default: Optional[Any]
    multiple: Optional[bool] = False
    display_rules: Optional[List[dict]]

class Text(BaseModel):
    component_type: Literal["text"]
    name: str
    text: str
    color: Optional[color_options]
    display_rules: Optional[List[Dict]]


comopnents_options = Union[Button, Input, Select, Text, Boolean]

class Widget(BaseModel):
    block_type: Literal["widget"]
    name: str
    label: str
    description: Optional[str]
    type: Literal["base", "modal", "inline"] = "base"
    in_menu: bool = True
    components: List[comopnents_options]

class BaseColumn(BaseModel):
    name: str
    data_type: Optional[str]
    display_type: Optional[Literal["text","integer","float","boolean","datetime","date","time","currency","select","array"]]
    configurations: Optional[Union[dict]]

class ButtonColumn(BaseModel):
    column_type: Literal["button_column"] = "button_column"
    name: str
    label: str
    color: Optional[color_options]
    hidden: bool = False

class PyColumn(BaseColumn):
    column_type: Literal["python"] = "python"
    hidden: bool = False
    editable: bool = False

class PgColumn(BaseColumn):
    column_type: Literal["postgres"] = "postgres"
    schema_name: str = None
    table_name: str = None
    column_name: str = None
    primary_key: bool = False
    foreign_key: bool = False
    default: str = None
    nullable: bool = False
    unique: bool = False
    hidden: bool = False
    editable: bool = False

columns_options = Union[ PgColumn, PyColumn, ButtonColumn]
class Table(BaseModel):
    block_type: Literal["table"]
    name: str
    label: str
    description: Optional[str]
    w: Optional[int] = 4
    h: Optional[int] = 1
    x: Optional[int] = 0
    y: Optional[int] = 0
    columns: List[columns_options]
    header: List[comopnents_options]
    footer: List[comopnents_options]"""
