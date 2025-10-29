from models.user import User as UserModel
from schemas.user_schema import UserCreate, UserUpdate
from sqlalchemy.orm import Session

from repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel, UserCreate, UserUpdate]):
    def create(
        self, db: Session, email: str, hashed_password: str, full_name: str
    ) -> UserModel:
        user = UserModel(
            email=email, full_name=full_name, hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def get_by_email(self, db: Session, email: str) -> UserModel | None:
        return db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_id(self, db: Session, id: int) -> UserModel | None:
        return db.query(UserModel).filter(UserModel.id == id).first()

    def update_password(
        db: Session, user: UserModel, hashed_new_password: str
    ) -> UserModel:
        user.hashed_password = hashed_new_password
        db.commit()
        db.refresh(user)
        return user


user_repository = UserRepository(UserModel)
