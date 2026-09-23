import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.session import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.setting import AppSetting
from app.models.wish import Wish


def seed_database():
    print("[+] Initializing Database Tables...")
    Base.metadata.create_all(bind=engine)
    print("[+] Tables created successfully!")

    db = SessionLocal()
    try:
        print("[+] Seeding Admin User...")
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=1
            )
            db.add(admin)
            db.commit()
            print("[+] Admin created: username='admin' (Password: admin123)")
        else:
            print("[i] Admin already exists.")

        print("[+] Seeding App Settings...")
        setting = db.query(AppSetting).filter(AppSetting.key == "frontend_display_limit").first()
        if not setting:
            setting = AppSetting(key="frontend_display_limit", value="50")
            db.add(setting)
            db.commit()
            print("[+] Default display limit set to 50.")
        else:
            print("[i] Settings already initialized.")

        # Sample wishes if empty
        wishes_count = db.query(Wish).count()
        if wishes_count == 0:
            print("[+] Seeding Initial Sample Wishes...")
            sample_wishes = [
                Wish(name="Budi Santoso", age_range="26-35 tahun", text="Semoga riset kelautan Indonesia semakin maju dan mandiri!", status="approved"),
                Wish(name="Siti Rahma", age_range="18-25 tahun", text="Harapan saya BRIN bisa mendukung inovasi teknologi pertanian berbasis AI.", status="approved"),
                Wish(name="Dr. Hendra", age_range="36-45 tahun", text="Maju terus peneliti muda Indonesia untuk kemajuan bangsa.", status="approved"),
            ]
            db.add_all(sample_wishes)
            db.commit()
            print("[+] Sample wishes created.")

    finally:
        db.close()
    print("\n[+] DREAM WALL SEEDING COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    seed_database()

