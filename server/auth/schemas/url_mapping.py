# DELETE ME
from typing import Optional

from pydantic import BaseModel


class BaseURLMapping(BaseModel):
    id: str
    name: Optional[str]
    client_url: Optional[str]
    worker_url: Optional[str]
    lsp_url: Optional[str]
    date: str


class ReadURLMapping(BaseURLMapping):
    pass


class CreateURLMapping(BaseModel):
    workspace_id: str
    name: Optional[str]
    client_url: Optional[str]
    worker_url: Optional[str]
    lsp_url: Optional[str]


class UpdateURLMapping(BaseModel):
    name: Optional[str]
    client_url: Optional[str]
    worker_url: Optional[str]
    lsp_url: Optional[str]


class DeleteURLMapping(BaseModel):
    id: str
