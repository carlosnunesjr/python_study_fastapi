from fastapi import status, HTTPException, Depends, APIRouter

from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import func

from . import outh2
from .. import models
from ..schemas import CreatePost, ResponsePost, ResponsePostVote2
from ..database import Session, get_db

router = APIRouter(prefix="/posts", tags=["Posts"])

from fastapi.encoders import jsonable_encoder


# @router.get("/")
# @router.get("/", response_model=List[ResponsePostVote])
@router.get("/semsucesso")
async def get_posts(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    try:
        posts = (
            db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
            .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
            .group_by(models.Post.id)
            .filter(models.Post.title.contains(search))
            .limit(limit)
            .offset(skip)
            .all()
        )

        posts = list(map(lambda x: x._mapping, posts))

        for post in posts:
            print(">>>>>>>>>", jsonable_encoder(post.Post))

        return jsonable_encoder(posts)

    except Exception as error:
        print("Error in get_posts:", error)


@router.get("/", response_model=List[ResponsePostVote2])
def get_posts_votes(
    db: Session = Depends(get_db),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    posts = (
        db.query(models.Post)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )

    posts_with_votes = []
    for post in posts:
        votes_query = (
            db.query(models.Vote).filter(models.Vote.post_id == post.id).count()
        )
        posts_with_votes.append(
            {**post.__dict__, "owner": post.owner, "votes": votes_query}
        )

    return posts_with_votes


@router.get("/{id}", response_model=ResponsePostVote2)
async def find_by_id(id: UUID, db: Session = Depends(get_db)):
    try:
        post = db.query(models.Post).filter(models.Post.id == id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} was not found",
            )

        votes_query = (
            db.query(models.Vote).filter(models.Vote.post_id == post.id).count()
        )

        post = {**post.__dict__, "owner": post.owner, "votes": votes_query}

        return post
    except Exception as error:
        print("Error in get_posts:", error)
        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error

        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ResponsePost)
async def create_post(
    post: CreatePost,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(outh2.get_current_user),
):
    try:
        new_post = models.Post(owner_id=current_user.id, **post.dict())
        new_post.id = uuid4()

        db.add(new_post)
        db.commit()
        db.refresh(new_post)

        return new_post

    except Exception as error:
        print("Error in create_post:", error)
        db.rollback()
        raise HTTPException(
            status_code=500, detail="Error inserting post into the database"
        )


@router.put("/{id}", status_code=status.HTTP_202_ACCEPTED, response_model=ResponsePost)
async def update_post(
    id: UUID,
    params: CreatePost,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(outh2.get_current_user),
):
    try:
        post_query = db.query(models.Post).filter(models.Post.id == id)

        post = post_query.first()

        if post == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} was not found",
            )

        if post.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action",
            )

        post_query.update(params.dict(), synchronize_session=False)

        db.commit()

        return post_query.first()

    except Exception as error:
        print("Error in update_post:", error)
        db.rollback()

        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error

        raise HTTPException(
            status_code=500, detail=f"Error update post into the database: {error}"
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(outh2.get_current_user),
):
    try:
        post_query = db.query(models.Post).filter(models.Post.id == id)

        post = post_query.first()

        if post == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {id} was not found",
            )

        if post.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action",
            )

        post_query.delete(synchronize_session=False)
        db.commit()

    except Exception as error:
        print("Error in delete_post:", error)
        db.rollback()
        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error

        raise HTTPException(status_code=500, detail="Error deleting post from database")
