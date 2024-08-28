from contextlib import contextmanager

from sqlalchemy.orm import Session

from app.apis.user.models import Role, User
from app.config.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)


# Modify get_session to be a proper context manager
@contextmanager
def get_seed_session():
    session = Session(bind=engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def seed_roles(session):
    roles = [
        Role(name="ADMIN", description="Administrator role with full access"),
        Role(name="STAFF", description="Staff user role with limited access"),
    ]
    session.add_all(roles)
    session.commit()


def seed_users(session):
    user = User(
        first_name="Admin",
        email="admin@gmail.com",
        password="admin123",
        mobile_no="1234567890",
        gender="M",
        profile_image_id=None,  # Assuming no profile image for now
    )
    role = session.query(Role).filter(Role.name == "ADMIN").first()
    user.roles.append(role)
    session.add(user)
    session.commit()


if __name__ == "__main__":
    with get_seed_session() as session:
        seed_roles(session)
        seed_users(session)
