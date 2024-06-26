from fastapi import APIRouter, HTTPException

from dropbase.schemas.page import CreateRenamePageRequest, PageProperties, SaveTableColumns
from dropbase.schemas.prompt import Prompt
from server.constants import DEFAULT_RESPONSES
from server.controllers.page_controller import PageController
from server.controllers.prompt import handle_prompt

router = APIRouter(prefix="/page", tags=["page"], responses=DEFAULT_RESPONSES)


@router.get("/{app_name}/{page_name}/init")
def get_page_init_req(app_name: str, page_name: str):
    try:
        pageController = PageController(app_name, page_name)
        return pageController.get_page(initial=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{app_name}/{page_name}/methods")
def get_page_methods_req(app_name: str, page_name: str):
    try:
        pageController = PageController(app_name, page_name)
        return pageController.get_methods()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{app_name}/{page_name}")
def get_page_req(app_name: str, page_name: str):
    try:
        pageController = PageController(app_name, page_name)
        return pageController.get_page()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
def create_page_req(request: CreateRenamePageRequest):
    try:
        pageController = PageController(request.app_name, request.page_name)
        pageController.create_page(request.page_label)
        return {"message": f"Page {request.page_name} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/")
def update_page_req(request: PageProperties):
    try:
        pageController = PageController(request.app_name, request.page_name)
        pageController.update_page_properties(request.properties)
        return {"message": f"Page {request.page_name} updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rename/")
def rename_page_req(request: CreateRenamePageRequest):
    try:
        pageController = PageController(request.app_name, request.page_name)
        pageController.rename_page(request.page_label)
        return {"message": f"Page {request.page_name} renamed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{app_name}/{page_name}")
def delete_page_req(app_name: str, page_name: str):
    try:
        pageController = PageController(app_name, page_name)
        pageController.delete_page()
        return {"message": f"Page {page_name} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save_table_columns/")
def save_table_columns_req(request: SaveTableColumns):
    try:
        pageController = PageController(request.app_name, request.page_name)
        pageController.save_table_columns(request.table_name, request.columns)
        return {"message": f"Table {request.table_name} columns saved successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# gpt promps
@router.post("/prompt/")
def ui_prompt_request(request: Prompt):
    try:
        return handle_prompt(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
