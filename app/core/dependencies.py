from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from app.core.database import get_session
from app.models.user import User


def get_current_user(
    session: Session = Depends(get_session),
) -> User:
    user = session.exec(select(User)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No user found in database. Make sure seed.py ran on startup.",
        )

    return user