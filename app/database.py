# import psycopg2
# from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_db}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Database connection
# try:
#     conn = psycopg2.connect(
#         database='fastapi-course',
#         user='postgres',
#         password='admin',
#         host='localhost',
#         cursor_factory=RealDictCursor
#     )
#     print("Database connection successfully")
#     cursor = conn.cursor()
# except Exception as e:
#     print("Databae connection error")
#     print(f"Error: {e}")