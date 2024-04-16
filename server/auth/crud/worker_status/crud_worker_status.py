from ..base import CRUDBase
from ...models import WorkerStatus
from ...schemas.worker_status import CreateWorkerStatus, UpdateWorkerStatus


class CRUDWorkerStatus(CRUDBase[WorkerStatus, CreateWorkerStatus, UpdateWorkerStatus]):
    pass


worker_status = CRUDWorkerStatus(WorkerStatus)
