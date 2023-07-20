from fastapi import status, HTTPException, Depends, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm


from ..database import Session, get_db
from ..schemas import Token
from ..models import User
from ..utils import verif
from .outh2 import create_access_token

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(
    user_credentials: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.email == user_credentials.username).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials",
            )

        if not verif(user_credentials.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid credentials",
            )

        access_token = create_access_token(data={"user_id": str(user.id)})

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as error:
        print("Error in user_credentials:", error)
        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
