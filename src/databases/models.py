import enum
from .connect import Base, engine
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Boolean,
    Enum,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship


class Role(enum.Enum):
    admin: str = "admin"
    user: str = "user"


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=False)
    birthday = Column(Date, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="contacts")
    __table_args__ = (
        UniqueConstraint("user_id", "email", name="unique_user_email"),
        UniqueConstraint("user_id", "phone_number", name="unique_user_phone"),
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)
    avatar = Column(String, nullable=True)
    roles = Column("roles", Enum(Role), default=Role.user)

    contacts = relationship(
        "Contact", back_populates="user", cascade="all, delete-orphan"
    )


def init_db():
    Base.metadata.create_all(bind=engine)
