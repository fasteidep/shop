from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uvicorn

app = FastAPI()

Base = declarative_base()

# Модель для игр
class Game(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    genre = Column(String)
    price = Column(Integer)

# Модель для пользователей
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

# Модель для покупок
class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_id = Column(Integer, ForeignKey('games.id'))

engine = create_engine('sqlite:///store.db', echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Добавление нескольких игр в базу данных
game1 = Game(name="The Witcher 3: Wild Hunt", genre="RPG", price=30)
game2 = Game(name="Grand Theft Auto V", genre="Action", price=20)
game3 = Game(name="Overwatch", genre="Shooter", price=25)

# Обработчик для получения списка всех игр
@app.get("/games")
def get_games():
    games = session.query(Game).all()
    return [game.__dict__ for game in games]

# Обработик для фильтрации игр по жанру
@app.get("/games/{genre}")
def get_games_by_genre(genre: str):
    games = session.query(Game).filter(Game.genre == genre).all()
    return [game.__dict__ for game in games]

# Обработчик для удаления игры
@app.delete("/games/{game_id}")
def delete_game(game_id: int):
    game = session.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    session.delete(game)
    session.commit()
    return {"message": "Game deleted successfully"}

# Обработчик для регистрации пользователя
@app.post("/register")
def register_user(username: str, password: str):
    existing_user = session.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    return {"message": "User registered successfully"}

# Обработчик для покупки игры пользователем
@app.post("/purchase/{user_id}/{game_id}")
def purchase_game(user_id: int, game_id: int):
    new_purchase = Purchase(user_id=user_id, game_id=game_id)
    session.add(new_purchase)
    session.commit()
    return {"message": "Game purchased successfully"}

@app.post("/games/add")
def addgame():
    pass

session.add_all([game1, game2, game3])
session.commit()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
