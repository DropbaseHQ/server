import json

from anthropic import Anthropic
from openai import OpenAI

from dropbase.schemas.prompt import Prompt
from server.config import server_envs
from server.constants import DEFAULT_MAX_TOKENS, DEFAULT_MODEL, DEFAULT_PROVIDER
from server.controllers.page_controller import PageController
from server.helpers.prompt_composer import determine_what_to_update, get_func_prompt, get_ui_prompt


def handle_prompt(request: Prompt):
    if not server_envs.get("llm"):
        raise Exception("API key for an LLM model is missing")

    # Get the provider and model from the request or use the default
    provider = request.provider or DEFAULT_PROVIDER
    model = request.model or DEFAULT_MODEL

    # init model
    llmModel = LLMModel(provider, model)

    # Get the prompt content
    infer_content_type = determine_what_to_update(request.app_name, request.page_name, request.prompt)
    content_type = llmModel.invoke(infer_content_type)

    # Get the prompt content
    base_path = f"workspace/{request.app_name}/{request.page_name}/"
    if "properties.json" in content_type:
        content = get_ui_prompt(base_path, request.prompt)
    elif "main.py" in content_type:
        content = get_func_prompt(base_path, request.prompt)
    else:
        raise Exception("Please clarify your request")

    updated_code = llmModel.invoke(content)
    # Remove markdown formatting from the updated code
    new_props = _remove_markdown_formatting(updated_code)

    if "main.py" in content_type:
        return new_props
    if "properties.json" in content_type:
        pageController = PageController(request.app_name, request.page_name)
        pageController.update_page_properties(json.loads(new_props))
        return {"message": "success"}


class LLMModel:
    def __init__(self, provider: str, model: str):
        llms = server_envs.get("llm")
        self.provider = provider
        self.model = model

        # api_key and config are required for the provider
        self.api_key = llms.get(provider).get("api_key")
        self.config = llms.get(provider).get("config") or {}

    def invoke(self, content):
        # call the provider's method by name
        method = getattr(self, self.provider)
        return method(content)

    def openai(self, content: str) -> str:
        client = OpenAI(api_key=self.api_key)
        messages = [{"role": "user", "content": content}]
        message = client.chat.completions.create(model=self.model, messages=messages, **self.config)
        return message.choices[0].message.content

    def anthropic(self, content: str) -> str:
        client = Anthropic(api_key=self.api_key)
        messages = [{"role": "user", "content": content}]
        if self.config == {}:
            # anthropic requires a max_tokens parameter
            self.config = {"max_tokens": DEFAULT_MAX_TOKENS}
        message = client.messages.create(model=self.model, messages=messages, **self.config)
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
