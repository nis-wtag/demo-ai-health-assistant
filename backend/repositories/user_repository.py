from models.user import User as UserModel
from sqlalchemy.orm import Session


class UserRepository:
    @staticmethod
    def create(
        db: Session, email: str, hashed_password: str, full_name: str
    ) -> UserModel:
        user = UserModel(
            email=email, full_name=full_name, hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_email(db: Session, email: str) -> UserModel | None:
        return db.query(UserModel).filter(UserModel.email == email).first()

    @staticmethod
    def get_by_id(db: Session, id: int) -> UserModel | None:
        return db.query(UserModel).filter(UserModel.id == id).first()

    @staticmethod
    def update_password(
        db: Session, user: UserModel, hashed_new_password: str
    ) -> UserModel:
        user.hashed_password = hashed_new_password
        db.commit()
        db.refresh(user)
        return user
