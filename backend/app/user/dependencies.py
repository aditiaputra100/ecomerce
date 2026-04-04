from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Annotated
from app.database import get_db
from app.config import settings
from . import models, schemas

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "customer": "View items, order items, and view transaction history.",
        "shopowner": "Have full control over the product catalog, manage the status of incoming orders.",
    }
    )

async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception
        
        scopes: str = payload.get("scopes", "")
        token_scope = scopes.split(" ")
        token_data = schemas.TokenData(username=username, scopes=token_scope)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == token_data.username).first()

    if user is None:
        raise credentials_exception
    print(security_scopes.scopes)
    print(token_data.scopes)
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user

def get_current_active_user(
        current_user: Annotated[models.User, Security(get_current_user)]
) -> models.User:
    if current_user.disable:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    return current_user