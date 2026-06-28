from sqlalchemy import Column, String, Integer
from src.utils.db import Base

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    hash_password = Column(String, nullable=False)
    email = Column(String, nullable=False)