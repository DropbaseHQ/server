import json

from openai import OpenAI

from dropbase.schemas.prompt import Prompt
from server.config import config
from server.controllers.page_controller import PageController
from server.helpers.prompt_composer import get_func_prompt, get_ui_prompt


def handle_prompt(request: Prompt):

    if config.get("openai_api_key") is None:
        raise Exception("OpenAI API key not found")

    base_path = f"workspace/{request.app_name}/{request.page_name}/"
    if request.type == "function":
        content = get_func_prompt(base_path, request.prompt)
    elif request.type == "ui":
        content = get_ui_prompt(base_path, request.prompt)

    client = OpenAI(api_key=config["openai_api_key"])
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": content}],
        model="gpt-4o",
    )
    updated_code = chat_completion.choices[0].message.content
    new_props = remove_markdown_formatting(updated_code)
    if request.type == "function":
        return new_props
    if request.type == "ui":
        pageController = PageController(request.app_name, request.page_name)
        pageController.update_page_properties(json.loads(new_props))
        return {"message": "success"}


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

    if cleaned_lines:
        return "\n".join(cleaned_lines)
    else:
        return code_snippet
