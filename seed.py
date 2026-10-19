import sys
from sqlmodel import Session, select
from app.core.database import engine, create_db_and_tables
from app.core.security import hash_password
from app.models.user import User


def seed_user(email: str, password: str, full_name: str):
    create_db_and_tables()

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            print(f"User already exists: {email}")
            return

        user = User(
            email=email,
            hashed_password=hash_password(password),
            full_name=full_name,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"Created user: {user.email} (id: {user.id})")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python seed.py <email> <password> <full_name>")
        print('Example: python seed.py james@company.com secret123 "James Carter"')
        sys.exit(1)

    seed_user(
        email=sys.argv[1],
        password=sys.argv[2],
        full_name=sys.argv[3],
    )