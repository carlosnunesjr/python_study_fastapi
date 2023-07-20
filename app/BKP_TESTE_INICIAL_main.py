from fastapi import FastAPI, status, HTTPException

from datetime import datetime

import psycopg
import json

from uuid import UUID, uuid4
from pydantic import BaseModel, Field

app = FastAPI()


def create_connection():
    try:
        conn = psycopg.connect(
            dbname="python_test",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
        )
        print("Connecting to database is successfully!")

        return conn

    except Exception as error:
        print("Connecting to database failed.")
        print("Error: ", error)

        if conn != None:
            conn.close()


def build_json_from_database(db_list):
    # Define a custom UUID encoder for JSON serialization
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)

    # Convert db_list to a list of dictionaries
    result = []
    for row in db_list:
        result.append(
            {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "published": row[3],
                "created_at": row[4],
            }
        )

    return result


class Post(BaseModel):
    title: str
    content: str
    published: bool = False


class ResponsePost(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    published: bool
    created_at: datetime


posts = []


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/posts")
async def get_posts():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts")

        # Fetch all rows from the result set
        rows = cursor.fetchall()

        json_result = build_json_from_database(rows)

        return json_result

    except Exception as error:
        print("Error in get_posts:", error)
    finally:
        if cursor != None:
            cursor.close()

        if conn != None:
            conn.close()


def parse_single_post_to_json(post) -> ResponsePost:
    return ResponsePost(
        id=post[0],
        title=post[1],
        content=post[2],
        published=post[3],
        created_at=post[4],
    ).dict()


@app.get("/posts/{id}")
async def find_by_id(id: UUID):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = %s", (id,))

        post = cursor.fetchone()

        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")

        return parse_single_post_to_json(post)

    except Exception as error:
        print("Error in get_posts:", error)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error)
    finally:
        if cursor != None:
            cursor.close()

        if conn != None:
            conn.close()


# @app.post("/posts")
# async def create_post(payload: dict = Body(...)):
#    print(payload)
#    return {"teste": "teste"}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        pk_value = str(uuid4())
        cursor.execute(
            """ INSERT INTO POSTS(ID, TITLE, CONTENT, PUBLISHED) VALUES(%s,%s,%s,%s) returning * """,
            (pk_value, post.title, post.content, post.published),
        )

        new_post = cursor.fetchone()

        conn.commit()

        return parse_single_post_to_json(new_post)

    except Exception as error:
        print("Error in create_post:", error)
        conn.rollback()
        raise HTTPException(
            status_code=500, detail="Error inserting post into the database"
        )
    finally:
        if cursor != None:
            cursor.close()

        if conn != None:
            conn.close()


@app.put("/posts/{id}", status_code=status.HTTP_202_ACCEPTED)
async def update_post(id: UUID, params: Post):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(
            """ UPDATE POSTS
            SET TITLE = %s, CONTENT = %s, PUBLISHED = %s
            WHERE id = %s returning * """,
            (params.title, params.content, params.published, id),
        )

        new_post = cursor.fetchone()

        conn.commit()

        if not new_post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post do not exists")

        return parse_single_post_to_json(new_post)

    except Exception as error:
        print("Error in update_post:", error)
        conn.rollback()

        if (
            hasattr(error, "status_code")
            and error.status_code == status.HTTP_404_NOT_FOUND
        ):
            raise error

        raise HTTPException(
            status_code=500, detail=f"Error update post into the database: {error}"
        )
    finally:
        if cursor != None:
            cursor.close()

        if conn != None:
            conn.close()


def find_index_post(id: UUID):
    for index, post in enumerate(posts):
        if post.id == id:
            return index


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: UUID):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        cursor.execute(""" DELETE FROM posts WHERE id = %s returning * """, (id,))

        deleted_post = cursor.fetchone()

        conn.commit()

        if not deleted_post:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Post do not exists")

    except Exception as error:
        print("Error in delete_post:", error)
        conn.rollback()
        if error.status_code == status.HTTP_404_NOT_FOUND:
            raise error

        raise HTTPException(status_code=500, detail="Error deleting post from database")
    finally:
        if cursor != None:
            cursor.close()

        if conn != None:
            conn.close()
