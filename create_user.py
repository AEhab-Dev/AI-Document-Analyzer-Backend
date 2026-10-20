from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.core.security import hash_password
from app.models.user import User

EMAIL = "james@company.com"
PASSWORD = "secret123"
FULL_NAME = "Admin"

create_db_and_tables()

with Session(engine) as session:
    user = session.exec(select(User).where(User.email == EMAIL)).first()
    if user:
        user.hashed_password = hash_password(PASSWORD)
        print("Password updated:", EMAIL)
    else:
        session.add(User(email=EMAIL, hashed_password=hash_password(PASSWORD), full_name=FULL_NAME))
        print("User created:", EMAIL)
    session.commit()