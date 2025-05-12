from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    username = Column(String)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)
    total_stars = Column(Float, default=0.0)
    
    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username}, stars={self.total_stars})>"

# Создаем подключение к базе данных
engine = create_engine('sqlite:///db/casino.db')
Base.metadata.create_all(engine)

# Создаем сессию
Session = sessionmaker(bind=engine)

def get_or_create_user(user_id: int, username: str) -> User:
    session = Session()
    user = session.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        user = User(user_id=user_id, username=username)
        session.add(user)
        session.commit()
    
    session.close()
    return user

def update_user_stats(user_id: int, stars_won: float, won: bool):
    session = Session()
    user = session.query(User).filter(User.user_id == user_id).first()
    
    if user:
        user.total_stars += stars_won
        if won:
            user.total_wins += 1
        else:
            user.total_losses += 1
        session.commit()
    
    session.close()

def add_stars_to_user(user_id: int, amount: float = 100.0):
    session = Session()
    user = session.query(User).filter(User.user_id == user_id).first()
    
    if user:
        user.total_stars += amount
        session.commit()
    
    session.close() 