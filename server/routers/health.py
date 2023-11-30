from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"], responses={404: {"description": "Not found"}})


@router.get("/")
def get_worker_info():
    return {"status": "ok", "version": "0.0.2"}
