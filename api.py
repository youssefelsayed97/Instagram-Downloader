from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import Session_local
from database.crud import get_all_users, get_user_info
from schemas.isntagram import InstagramUserResponse, paginationRespopnse
from utilits.cursor import encode_cursor, decode_cursor

app = FastAPI()

def get_db():
    db = Session_local()
    try:
        yield db
    finally:
        db.close()

@app.get("/users", response_model=paginationRespopnse)
def users(limit: int = 10, cursor: str | None = None, db: Session = Depends(get_db)):
    if limit > 10:
        raise HTTPException(status_code=400, detail=f"limit > 10")

    if cursor is not None:
        cursor = decode_cursor(cursor)

    users, has_next = get_all_users(db, limit, cursor)

    next_cursor = None

    if has_next:
        next_cursor = encode_cursor(users[-1].id)

    return {
        "data": users,
        "next_cursor": next_cursor,
        "has_next": has_next
    }


@app.get("/users/{username}", response_model=InstagramUserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user = get_user_info(db, instagram_username=username)
    if user is None:
        raise HTTPException(status_code=404, detail=f"{username} not found")

    return user

@app.get("/users/id/{user_id}", response_model=InstagramUserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = get_user_info(db, instagram_user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=f"{user_id} not found")

    return user

@app.get("/")
def root():
    return {"message": "insta data api"}