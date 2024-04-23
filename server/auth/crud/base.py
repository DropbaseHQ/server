from typing import Any, Dict, Generic, List, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, Session

from ..models import Policy

ModelType = TypeVar("ModelType", bound=declarative_base())

CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType:
        return db.query(self.model).get(id)

    def get_object_by_id_or_404(self, db: Session, id: Any) -> ModelType:
        object = db.query(self.model).get(id)
        if not object:
            raise Exception(self.model.__name__, self.model.__name__)
            # raise ResourceNotFound(self.model.__name__, self.model.__name__)
        return object

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(
        self, db: Session, *, obj_in: CreateSchemaType, auto_commit: bool = True
    ) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        if auto_commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        auto_commit: bool = True
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        if auto_commit:
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def update_by_pk(
        self,
        db: Session,
        *,
        pk: UUID,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
        auto_commit: bool = True
    ):
        """
        Generalized update query only based on model primary key.
        - This removes the need to pass the entire object like with .update(),
          but you are only limited to updating by primary key
        - Pass auto_commit = False if you want to control when this query is commited

        """
        db_obj = self.get_object_by_id_or_404(db, pk)

        return self.update(db, db_obj=db_obj, obj_in=obj_in, auto_commit=auto_commit)

    def remove(self, db: Session, *, id: UUID, auto_commit: bool = True) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.query(Policy).filter(
            or_(Policy.v0 == str(id), Policy.v1 == str(id), Policy.v2 == str(id))
        ).delete()
        if auto_commit:
            db.commit()
        return obj

    def remove_multiple(
        self, db: Session, query: Query, auto_commit: bool = True
    ) -> ModelType:
        object_ids = [obj.id for obj in query.all()]
        query.delete()
        db.query(Policy).filter(
            or_(
                Policy.v0.in_(object_ids),
                Policy.v1.in_(object_ids),
                Policy.v2.in_(object_ids),
            )
        ).delete(synchronize_session=False)
        if auto_commit:
            db.commit()
