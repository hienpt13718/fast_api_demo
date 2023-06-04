from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, Integer, String

app = FastAPI()

#SqlAlchemy Setup
SQLALCHEMY_DATABASE_URL = 'sqlite+pysqlite:///./db.sqlite3:'
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DBUser(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String(50))
    lastName = Column(String(50))
    age = Column(Integer)
    email = Column(String(50))

Base.metadata.create_all(bind=engine)

class User(BaseModel):
    firstName: str
    lastName: str
    age: int
    email: str

    class Config:
        orm_mode = True

# Methods for interacting with the database
def get_user(db: Session, user_id: int):
    return db.query(DBUser).where(DBUser.id == user_id).first()

def get_users(db: Session):
    return db.query(DBUser).all()

def create_user(db: Session, user: User):
    db_user = DBUser(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.post('/users/', response_model=User)
def create_user_api(user: User, db: Session = Depends(get_db)):
    db_user = create_user(db, user)
    return db_user

@app.get('/users/', response_model=List[User])
def get_users_api(db: Session = Depends(get_db)):
    return get_users(db)

@app.get('/users/{user_id}')
def get_user_by_id_api(user_id: int, db: Session = Depends(get_db)):
    return get_user(db, user_id)

@app.get('/')
async def root():
    return {'message': 'Hello world!'}