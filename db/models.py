from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
import random
import string
from datetime import datetime
import logging
import os
from sqlalchemy import inspect
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


Base = declarative_base()

engine = create_engine(DATABASE_URL)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer)
    stars = Column(Float, default=100.0)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    is_vip = Column(Boolean, default=False)
    referral_code = Column(String(10), unique=True)
    referred_by = Column(BigInteger, ForeignKey('users.telegram_id'))
    daily_streak = Column(Integer, default=0)
    last_daily = Column(DateTime)
    last_free_stars_claim = Column(DateTime) 
    created_at = Column(DateTime, default=datetime.now)

    def __init__(self, telegram_id: int, name: str, stars: float = 100.0):
        self.telegram_id = telegram_id
        self.name = name
        self.stars = stars
        self.referral_code = self.generate_referral_code()

    def generate_referral_code(self):
        try:
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not session.query(User).filter_by(referral_code=code).first():
                    return code
        except Exception as e:
            logger.error(f"Ошибка при генерации реферального кода: {e}", exc_info=True)
            raise

    def add_stars(self, amount: float):
        try:
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            self.stars += amount
            session.commit()
            logger.info(f"Added {amount} Stars to user {self.telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении Stars: {e}", exc_info=True)
            session.rollback()
            raise

    def remove_stars(self, amount: float):
        try:
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            if self.stars >= amount:
                self.stars -= amount
                session.commit()
                logger.info(f"Removed {amount} Stars from user {self.telegram_id}")
                return True
            logger.warning(f"Not enough Stars for user {self.telegram_id}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при снятии Stars: {e}", exc_info=True)
            session.rollback()
            raise

    def get_vip_multiplier(self) -> float:
        return 1.5 if self.is_vip else 1.0

    def add_win(self):
        try:
            self.wins += 1
            session.commit()
            logger.info(f"Added win for user {self.telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении победы: {e}", exc_info=True)
            session.rollback()
            raise

    def add_loss(self):
        try:
            self.losses += 1
            session.commit()
            logger.info(f"Added loss for user {self.telegram_id}")
        except Exception as e:
            logger.error(f"Ошибка при добавлении поражения: {e}", exc_info=True)
            session.rollback()
            raise

async def init_db():
    try:
        Base.metadata.create_all(engine)
        
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'last_free_stars_claim' not in columns:
            # Добавляем колонку, если её нет
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_free_stars_claim DATETIME"))
                conn.commit()
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}", exc_info=True)
        raise