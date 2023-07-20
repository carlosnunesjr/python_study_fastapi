from fastapi import status, HTTPException, Depends, APIRouter

from psycopg.errors import UniqueViolation

from uuid import UUID, uuid4

from .. import models, utils
from ..schemas import CreateUser, ResponseUser
from ..database import Session, get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponseUser)
async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    try:
        user_already_exists = (
            db.query(models.User).filter(models.User.email == user.email).first()
        )

        if user_already_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Already exists user with this email: {user.email}",
            )

        hashed_password = utils.hash(user.password)

        user.password = hashed_password

        new_user = models.User(**user.dict())
        new_user.id = uuid4()

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user

    except Exception as error:
        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_400_BAD_REQUEST
        ):
            raise error

        print("Error in create_user:", error)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error inserting user into the database",
        )


@router.get("/{id}", response_model=ResponseUser)
async def get_user_by_id(id: UUID, db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.id == id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id: {id} was not found",
            )

        return user
    except Exception as error:
        print("Error in get_user_by_id:", error)
        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
