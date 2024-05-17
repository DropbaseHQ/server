from fastapi import APIRouter

from dropbase.schemas.page import CreatePageRequest, PageProperties, SaveTableColumns

# prompt related
from dropbase.schemas.prompt import FuncPrompt, UIPrompt
from server.controllers.page_controller import PageController
from server.controllers.prompt import handle_func_prompt, handle_ui_prompt

def_responses = {404: {"description": "Not found"}}

router = APIRouter(prefix="/page", tags=["page"], responses=def_responses)


@router.get("/{app_name}/{page_name}/init")
def get_page_init_req(app_name: str, page_name: str):
    pageController = PageController(app_name, page_name)
    return pageController.get_page(initial=True)


@router.get("/{app_name}/{page_name}/methods")
def get_page_methods_req(app_name: str, page_name: str):
    pageController = PageController(app_name, page_name)
    return pageController.get_methods()


@router.get("/{app_name}/{page_name}")
def get_page_req(app_name: str, page_name: str):
    pageController = PageController(app_name, page_name)
    return pageController.get_page()


@router.post("/")
def create_page_req(request: CreatePageRequest):
    pageController = PageController(request.app_name, request.page_name)
    pageController.create_page(request.page_label)
    return {"message": "success"}


@router.put("/")
def update_page_req(request: PageProperties):
    pageController = PageController(request.app_name, request.page_name)
    pageController.update_page_properties(request.properties)
    return {"message": "success"}


@router.put("/rename/")
def rename_page_req(request: CreatePageRequest):
    pageController = PageController(request.app_name, request.page_name)
    pageController.update_page_to_app_properties(request.page_label)
    return {"message": "success"}


@router.delete("/{app_name}/{page_name}")
def delete_page_req(app_name: str, page_name: str):
    pageController = PageController(app_name, page_name)
    pageController.delete_page()
    return {"message": "success"}


@router.post("/save_table_columns/")
def save_table_columns_req(request: SaveTableColumns):
    pageController = PageController(request.app_name, request.page_name)
    pageController.save_table_columns(request.table_name, request.columns)
    return {"message": "success"}


# gpt promps
@router.post("/prompt/ui/")
def ui_prompt_request(request: UIPrompt):
    return handle_ui_prompt(request)


@router.post("/prompt/function/")
def func_prompt_request(request: FuncPrompt):
    return handle_func_prompt(request)
