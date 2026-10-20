from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.core.security import hash_password
from app.models.user import User

EMAIL = "james@company.com"          # غيّره
PASSWORD = "ChangeMe12345"         # غيّره
FULL_NAME = "Your Name"            # غيّره

create_db_and_tables()

with Session(engine) as session:
    existing = session.exec(select(User).where(User.email == EMAIL)).first()
    if existing:
        print("User already exists")
    else:
        user = User(
            email=EMAIL,
            hashed_password=hash_password(PASSWORD),
            full_name=FULL_NAME,
        )
        session.add(user)
        session.commit()
        print("User created:", EMAIL)