import uuid
from sqlalchemy.orm import Session
from src.database import SessionLocal, engine
from src.models import Base, User, Role
from src.auth import get_password_hash

def create_admin():
    # Создаем таблицы, если их еще нет
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Проверяем, существует ли уже админ
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            # Создаем нового админа
            admin = User(
                id=str(uuid.uuid4()),
                email="admin@example.com",
                name="Admin",
                hashed_password=get_password_hash("admin123"),  # Пароль: admin123
                role=Role.ADMIN
            )
            db.add(admin)
            db.commit()
            print("Администратор успешно создан!")
            print("Email: admin@example.com")
            print("Пароль: admin123")
        else:
            print("Администратор уже существует!")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 