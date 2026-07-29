from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    url=DATABASE_URL,
    echo=False # turning off db logging in terminal
)

Session_local = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)