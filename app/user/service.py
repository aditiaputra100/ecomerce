from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.exceptions import DuplicateEntryError
from . import models, utils

def create_user(username: str, email: str, password: str, disable: bool, db: Session) -> models.User:
    hashed_password = utils.get_password_hash(password)

    new_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        disable=disable
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

    except IntegrityError as err:
        db.rollback()
        raise DuplicateEntryError(name=err.orig.args)

    return new_user

def get_user_by_username(username: str, db: Session) -> models.User | None:
    user = db.query(models.User).where(models.User.username == username).first()

    return user