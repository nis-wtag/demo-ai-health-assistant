from typing import Any, Generic, TypeVar

from core.database import Base
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaTyep", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: ModelType):
        self.model = model

    def get_count(self, db: Session) -> int:
        """
        Returns the total number of unique doctors in the database.
        """
        return db.query(func.count(self.model.id)).scalar()

    def get(self, db: Session, id: Any) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, obj_id: Any, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        db_obj = db.query(self.model).filter(self.model.id == obj_id).first()
        if not db_obj:
            raise ValueError(f"{self.model.__name__} with id {obj_id} not found")

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        obj_data = jsonable_encoder(db_obj)
        for field, value in update_data.items():
            if field in obj_data and field != "id":
                setattr(db_obj, field, value)

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except Exception as e:
            db.rollback()
            raise e

        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType | None:
        obj = db.query(self.model).get(id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
