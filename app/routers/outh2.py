from jose import JWTError, jwt
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordBearer

from ..database import Session, get_db
from ..schemas import TokenData
from ..models import User

from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY = settings.OUTH_SECRET_KEY
ALGORITHM = settings.OUTH_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.OUTH_ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_enconde = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_enconde.update({"exp": expire})

    return jwt.encode(to_enconde, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])

        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        token_data = TokenData(id=user_id)

        return token_data

    except JWTError:
        raise credentials_exception


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    user = db.query(User).filter(User.id == token_data.id).first()

    return user
