from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.user_schemas import UserUpdate, UserChangePassword
from repositories.user_repository import update_user, change_password

router = APIRouter(tags=["User"])

@router.post("/update-profile")
async def update_profile(user: UserUpdate, db: Session = Depends(get_db)):
    return update_user(db, user)

@router.post('/change_password')
async def change_password(user: UserChangePassword, db: Session = Depends(get_db)):
    return change_password(db, user)