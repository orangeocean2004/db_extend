from pathlib import Path
from .deps import engine, SessionLocal, DB_PATH
from . import models, crud

def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not crud.get_user_by_account(db, "12345678"):
            crud.create_user(db, "12345678", "admin123", "admin")
            print("已创建管理员：12345678 / admin123")
        else:
            print("管理员已存在")
    finally:
        db.close()

if __name__ == "__main__":
    main()