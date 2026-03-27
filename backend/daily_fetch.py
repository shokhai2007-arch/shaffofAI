import os
import sys

# Backend papkasini tushunishi uchun
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.services import fetch_and_populate

def daily_job():
    print("Kunlik Ma'lumotlarni tortib olish skripti ishga tushdi...")
    db = SessionLocal()
    try:
        # Masalan, kunlik 500 ta olish mumkin
        count = fetch_and_populate(db, max_records=100)
        print(f"Muvaffaqiyatli saqlandi. Jami olingan tenderlar: {count}")
    finally:
        db.close()

if __name__ == "__main__":
    daily_job()
