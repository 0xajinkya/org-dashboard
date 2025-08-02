"""This module provides a connection to the database."""

import os

import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


@st.cache_resource(show_spinner="Connecting to database...")
def connect_to_db():
    try:
        session = SessionLocal()
        session.execute(text("SELECT 1"))
        print("✅ Database connection established.")
    except Exception as e:
        print("❌ Failed to connect to the database:", e)
        raise
    return session


db = connect_to_db()
