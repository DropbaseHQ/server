from pydantic import BaseModel


class WorkerStatusBase(BaseModel):
    token: str
    version: str


class CreateWorkerStatus(WorkerStatusBase):
    pass


class UpdateWorkerStatus(WorkerStatusBase):
    pass
