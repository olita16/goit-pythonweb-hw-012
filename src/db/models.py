from sqlalchemy import Column, Integer, String, Date, Boolean, Enum, ForeignKey, UniqueConstraint

from sqlalchemy.orm import relationship
from .connect import Base, engine
from enum import Enum as PyEnum


class Role(PyEnum):
    admin = "admin"
    moderator = "moderator"
    user = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    roles = Column(Enum(Role), default=Role.user)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    confirmed = Column(Boolean, default=False)
    avatar = Column(String(255), nullable=True)

    contacts = relationship(
        "Contact", back_populates="user", cascade="all, delete-orphan"
    )


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    birthday = Column(Date, nullable=False)
    additional_info = Column(String(255), nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="contacts")
    __table_args__ = (
        UniqueConstraint("user_id", "email", name="unique_user_email"),
        UniqueConstraint("user_id", "phone_number", name="unique_user_phone"),
    )

def init_db():
    Base.metadata.create_all(bind=engine)
