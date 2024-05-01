from fastapi import status, HTTPException, Depends, Response, APIRouter
from database import get_db
from typing import List, Optional
from sqlalchemy.orm import Session
import schemas, models, oauth2

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ResponsePost)
def create_post(post: schemas.Post, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # sql = """INSERT INTO posts (title, content, is_published) VALUES (%s, %s, %s) RETURNING *"""
    # values = (post.title, post.content, post.is_published)
    # cursor.execute(sql, values)
    # conn.commit()
    # new_post = cursor.fetchone()
    new_post = models.Post(user_id=current_user.id, **post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/", response_model=List[schemas.ResponsePost])
def get_posts(db: Session = Depends(get_db),
            search: Optional[str] = "", limit: int = 10, skip: int = 0):
    # sql = """SELECT * FROM posts"""
    # cursor.execute(sql)
    # data = cursor.fetchall()
    data = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return data

@router.get("/{post_id}", response_model=schemas.ResponsePost)
def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    # sql = """SELECT * FROM posts WHERE id = %s"""
    # cursor.execute(sql, (str(post_id),))
    # data = cursor.fetchone()
    data = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} was not found")
    return data

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_by_id(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # sql = """DELETE FROM posts WHERE id = %s RETURNING *"""
    # cursor.execute(sql, (str(post_id),))
    # conn.commit()
    # deleted_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} was not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{post_id}", response_model=schemas.ResponsePost)
def update_post(post_id: int, post: schemas.Post, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # sql = """UPDATE posts SET title = %s, content = %s, is_published = %s WHERE id = %s RETURNING *;"""
    # values = (post.title, post.content, post.is_published, post_id, )
    # cursor.execute(sql, values)
    # conn.commit()
    # updated_post = cursor.fetchone()
    post_query = db.query(models.Post).filter(models.Post.id == post_id)
    first_post = post_query.first()
    if first_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} was not found")
    if first_post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()