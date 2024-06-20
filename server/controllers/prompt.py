import json

import anthropic
from openai import OpenAI

from dropbase.schemas.prompt import Prompt
from server.config import server_envs
from server.controllers.page_controller import PageController
from server.helpers.prompt_composer import get_func_prompt, get_ui_prompt


def handle_prompt(request: Prompt):
    if not server_envs.get("llm"):
        raise Exception("API key for an LLM model is missing")

    # Get the prompt content
    base_path = f"workspace/{request.app_name}/{request.page_name}/"
    if request.type == "function":
        content = get_func_prompt(base_path, request.prompt)
    elif request.type == "ui":
        content = get_ui_prompt(base_path, request.prompt)
    # Invoke the model with the prompt
    llmModel = LLMModel()
    updated_code = llmModel.invoke(content)
    # Remove markdown formatting from the updated code
    new_props = _remove_markdown_formatting(updated_code)

    if request.type == "function":
        return new_props
    if request.type == "ui":
        pageController = PageController(request.app_name, request.page_name)
        pageController.update_page_properties(json.loads(new_props))
        return {"message": "success"}


class LLMModel:
    def __init__(self):

        default_models = {"openai": "gpt-4o", "anthropic": "claude-3-5-sonnet-20240620"}
        llms = server_envs.get("llm")
        self.provider_name = next(iter(llms))
        self.provider = llms.get(self.provider_name)
        self.api_key = self.provider.get("api_key")
        self.model = self.provider.get("model") or default_models.get(self.provider_name)
        self.max_tokens = self.provider.get("max_tokens") or 4096

    def invoke(self, content):
        method = getattr(self, self.provider_name)
        return method(content)

    def openai(self, content: str) -> str:
        client = OpenAI(api_key=self.api_key)
        messages = [{"role": "user", "content": content}]
        message = client.chat.completions.create(
            model=self.model, max_tokens=self.max_tokens, messages=messages
        )
        return message.choices[0].message.content

    def anthropic(self, content: str) -> str:
        client = anthropic.Anthropic(api_key=self.api_key)
        messages = [{"role": "user", "content": content}]
        message = client.messages.create(model=self.model, max_tokens=self.max_tokens, messages=messages)
        return message.content[0].text


def _remove_markdown_formatting(code_snippet):
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
