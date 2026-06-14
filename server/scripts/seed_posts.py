import sys
from pathlib import Path

# Add server/ folder to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from db.database import SessionLocal, engine, Base
from db.models import Post


DEFAULT_POSTS = [
    {
        "title": "Junior Engineer",
        "level": 1,
        "can_monitor": 0,
        "can_manage_hierarchy": 0
    },
    {
        "title": "Senior Engineer",
        "level": 2,
        "can_monitor": 1,
        "can_manage_hierarchy": 0
    },
    {
        "title": "Team Lead",
        "level": 3,
        "can_monitor": 1,
        "can_manage_hierarchy": 0
    },
    {
        "title": "Manager",
        "level": 4,
        "can_monitor": 1,
        "can_manage_hierarchy": 0
    },
    {
        "title": "Hierarchy Admin",
        "level": 5,
        "can_monitor": 1,
        "can_manage_hierarchy": 1
    },
]


def seed_posts():
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        for item in DEFAULT_POSTS:
            existing = db.query(Post).filter(Post.title == item["title"]).first()

            if not existing:
                db.add(Post(**item))

        db.commit()
        print("Posts seeded successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_posts()