from fastapi import APIRouter

from dropbase.database.sources import get_sources

router = APIRouter(
    prefix="/sources",
    tags=["sources"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_workspace_sources():
    sources = get_sources()

    source_with_type = [{"name": key, "type": value["type"]} for key, value in sources.items()]

    return {"sources": source_with_type}
