from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

def add_last_free_stars_claim_column():
    try:
        with engine.connect() as conn:
            conn.execute(text('ALTER TABLE users ADD COLUMN last_free_stars_claim DATETIME'))
            conn.commit()
        print("Колонка last_free_stars_claim успешно добавлена")
    except Exception as e:
        print(f"Ошибка при добавлении колонки: {e}")

if __name__ == "__main__":
    add_last_free_stars_claim_column() 