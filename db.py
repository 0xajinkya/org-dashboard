import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

@st.cache_resource(show_spinner="Connecting to database...")
def get_session():
    engine = create_engine(DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(bind=engine)

    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        print("✅ Database connection established.")
    except Exception as e:
        print("❌ Failed to connect to the database:", e)
        raise
    return session

db = get_session()
