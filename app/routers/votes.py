from fastapi import status, HTTPException, Depends, APIRouter
from uuid import UUID

from ..database import Session, get_db
from .outh2 import get_current_user
from ..schemas import Vote
from .. import models

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: Vote,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post {vote.post_id} does not exist",
            )

        vote_query = db.query(models.Vote).filter(
            models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
        )
        founded_vote = vote_query.first()

        if vote.dir == 1:
            if founded_vote:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"user {current_user.id} has already voted on post {vote.post_id}",
                )
            new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)
            db.add(new_vote)
            db.commit()
            return {"message": "successfully added vote"}
        else:
            if not founded_vote:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vote Post {vote.post_id} does not exist",
                )

            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "successfully deleted vote"}
    except Exception as error:
        print("Error in vote:", error)
        db.rollback()

        if hasattr(error, "status_code") and (
            error.status_code == status.HTTP_409_CONFLICT
            or error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error
        raise HTTPException(
            status_code=500, detail="Error proccessing vote into the database"
        )
