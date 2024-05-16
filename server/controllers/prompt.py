from openai import OpenAI

from dropbase.schemas.prompt import Prompt
from server.config import config


def handle_prompt(request: Prompt):

    if config.get("openai_api_key") is None:
        raise Exception("OpenAI API key not found")

    base_path = f"workspace/{request.app_name}/{request.page_name}/"

    # read files
    with open(base_path + "scripts/main.py", "r") as file:
        main_str = file.read()
    with open(base_path + "state.py", "r") as file:
        state_str = file.read()
    with open(base_path + "context.py", "r") as file:
        context_str = file.read()

    content = f"""given state.py:
'''python
{state_str}
'''
and context.py:
'''python
{context_str}
'''
implement the method {request.method} in main.py:
'''python
{main_str}
'''
following the user's command: {request.prompt}.
Only return the code for a new main.py file, nothing else.

{clarifications}
"""

    client = OpenAI(api_key=config["openai_api_key"])
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model="gpt-4o",
    )
    # return main.py code
    updated_code = chat_completion.choices[0].message.content
    return remove_markdown_formatting(updated_code)


clarifications = """
NOTE:
- table state contains the selected row for a specific table; each of the values in the state object is a column
- context state contains all the inputs currently entered by a user in various Dropbase UI/client components
- context contains information used by the Dropbase UI to display components/data as well as component or column visibility and messages
- the data attribute in context contains data to be displayed in a table component in the Dropbase UI/client
- use "to_dtable()" to format a dataframe into a format that can be displayed by the Dropbase UI/client; data sent to Dropbase tables MUST be formatted correctly
- tables can have one header and/or one footer. headers and footers can have various components, including text, input, select dropdowns, buttons, and boolean toggles
- header and footer methods should be defined inside the corresponding table class
- to display a modal, set a model widget's visibility to True
- use page context exclusively for passing/displaying messages to the user. this is the preferred way to show user messages
- import any python sdk needed to perform the task, but don't modify or delete existing import statements
- by default, Dropbase UI/client sends dates as a string in Unix epoch
"""


def remove_markdown_formatting(code_snippet):
    lines = code_snippet.splitlines()
    cleaned_lines = []
    inside_code_block = False

    for line in lines:
        # Toggle the inside_code_block flag when triple backticks are found
        if line.startswith("```"):
            inside_code_block = not inside_code_block
        elif inside_code_block:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
