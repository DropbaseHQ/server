from fastapi import APIRouter

from server.constants import WORKER_VERSION

router = APIRouter(prefix="/health", tags=["health"], responses={404: {"description": "Not found"}})


@router.get("/")
def get_worker_info():
    return {"status": "ok", "version": WORKER_VERSION}
