from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///game_bot.db')

# Создаем движок базы данных
engine = create_engine(DATABASE_URL)

# Создаем сессию
Session = sessionmaker(bind=engine)
session = Session()

def add_last_free_stars_claim_column():
    """Добавляет колонку last_free_stars_claim в таблицу users"""
    try:
        # Добавляем колонку
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE users ADD COLUMN last_free_stars_claim DATETIME'))
            conn.commit()
        print("Колонка last_free_stars_claim успешно добавлена")
    except Exception as e:
        print(f"Ошибка при добавлении колонки: {e}")

if __name__ == "__main__":
    add_last_free_stars_claim_column() 