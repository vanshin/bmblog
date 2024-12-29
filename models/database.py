import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus as urlquote
from sqlalchemy.engine import Engine
from models import Base

from sqlalchemy.orm import sessionmaker

from config import Settings
from dependencies import get_settings
from fastapi import Depends
from models.article import Group

# 创建全局 engine 实例
engine = create_engine(
    get_settings().db_url, 
    echo=True, 
    pool_size=10, 
    max_overflow=20
)

# 创建全局 SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

def create_tables():
    """Create all database tables defined in models"""
    Base.metadata.create_all(bind=engine)

def init_db():
    # Create default session
    Session = sessionmaker(bind=engine)
    session = Session()
    create_tables()
    # Check if default group exists
    default_group = session.query(Group).filter(Group.name == "无分组").first()
    if not default_group:
        # Create default group if it doesn't exist
        default_group = Group(name="无分组")
        session.add(default_group)
        session.commit()
    
    session.close()

def migrate_db():
    """Run database migrations using alembic"""
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
