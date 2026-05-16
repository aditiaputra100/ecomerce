from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.exceptions import DuplicateEntryError
from . import models, utils


@dataclass(frozen=True)
class SessionIssueResult:
    access_token: str
    refresh_token: str
    user: models.User
    session: models.RefreshSession

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

        raise DuplicateEntryError(name=str(err.orig))

    return new_user

def get_user_by_username(username: str, db: Session) -> models.User | None:
    user = db.query(models.User).where(models.User.username == username).first()

    return user


def authenticate_user(username: str, password: str, db: Session) -> models.User:
    user = get_user_by_username(username, db)
    if not user or not utils.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def compute_scopes_for_user(user: models.User) -> list[str]:
    scopes = ["me", "customer"]
    if user.has_shop:
        scopes.append("shopowner")
    return scopes


def _build_access_token(user: models.User) -> str:
    scopes = compute_scopes_for_user(user)
    return utils.create_access_token(data={"sub": user.username, "scopes": " ".join(scopes)})


def _create_refresh_session(user: models.User, db: Session) -> tuple[models.RefreshSession, str]:
    refresh_token = utils.create_refresh_token()
    token_hash = utils.hash_refresh_token(refresh_token)
    session = models.RefreshSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=utils.refresh_token_expires_at(),
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session, refresh_token


def issue_session(user: models.User, db: Session) -> SessionIssueResult:
    session, refresh_token = _create_refresh_session(user, db)

    return SessionIssueResult(
        access_token=_build_access_token(user),
        refresh_token=refresh_token,
        user=user,
        session=session,
    )


def get_active_refresh_session(refresh_token: str, db: Session) -> models.RefreshSession | None:
    token_hash = utils.hash_refresh_token(refresh_token)

    now = datetime.now(timezone.utc)
    return (
        db.query(models.RefreshSession)
        .filter(models.RefreshSession.token_hash == token_hash)
        .filter(models.RefreshSession.revoked_at.is_(None))
        .filter(models.RefreshSession.expires_at > now)
        .first()
    )


def rotate_session(refresh_token: str, db: Session) -> SessionIssueResult:
    session = get_active_refresh_session(refresh_token, db)
    
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    new_refresh_token = utils.create_refresh_token()
    session.token_hash = utils.hash_refresh_token(new_refresh_token)
    session.expires_at = utils.refresh_token_expires_at()

    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionIssueResult(
        access_token=_build_access_token(session.user),
        refresh_token=new_refresh_token,
        user=session.user,
        session=session,
    )


def revoke_session(refresh_token: str, db: Session) -> bool:
    session = get_active_refresh_session(refresh_token, db)

    if not session:
        return False

    session.revoked_at = datetime.now(timezone.utc)

    db.add(session)
    db.commit()

    return True
