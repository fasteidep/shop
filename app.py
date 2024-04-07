from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from datetime import datetime
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List

# Создание экземпляра FastAPI
app = FastAPI()

# Подключение к базе данных с помощью SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./games.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель для игры
class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    genre = Column(String, index=True)
    price = Column(Integer)

# Модель для пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, unique=True)
    hashed_password = Column(String)

# Модель для покупки
class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    game_id = Column(Integer, ForeignKey("games.id"))
    purchased_at = Column(DateTime, default=datetime.utcnow)

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

# Криптографический контекст для хранения и проверки паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Получение экземпляра базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Обработчик для получения списка всех игр
@app.get("/games/", response_model=List[Game])
def get_games(db: Session = Depends(get_db)):
    games = db.query(Game).all()
    return games

# Обработчик для фильтрации игр по жанру
@app.get("/games/filter/")
def filter_games(genre: str, db: Session = Depends(get_db)):
    games = db.query(Game).filter(Game.genre == genre).all()
    return games

# Обработчик для удаления игры
@app.delete("/games/{game_id}")
def delete_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()

    if game:
        db.delete(game)
        db.commit()
        return {"message": "Game deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
