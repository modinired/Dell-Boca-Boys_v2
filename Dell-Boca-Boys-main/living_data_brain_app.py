
import streamlit as st
import pandas as pd
from sqlalchemy import (
    create_engine,
    inspect,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    ForeignKey,
    Text,
    Date,
    JSON as SAJSON,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Configuration ---
# Database file path.  Use environment variable `LIVING_DB_FILE_PATH` if set,
# otherwise default to a local file `living_data_brain.db` in the project root.
DB_FILE_PATH = os.getenv("LIVING_DB_FILE_PATH")
if not DB_FILE_PATH:
    # Determine project root relative to this file (repo root is one level up)
    repo_root = Path(__file__).resolve().parents[1]
    DB_FILE_PATH = str(repo_root / "living_data_brain.db")

# --- Page Config ---
st.set_page_config(
    page_title="Living Data Brain",
    page_icon="🧠",
    layout="wide",
)

# --- Database Schema ---
Base = declarative_base()

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    script_name = Column(String, nullable=True)
    run_ts = Column(DateTime, default=datetime.utcnow)
    # ... (add all other columns from your schema)

# (All other SQLAlchemy classes from living_data_brain.py go here)
# ...

# --- Database Functions ---

def init_database():
    """Create and seed the database."""
    engine = create_engine(f"sqlite:///{DB_FILE_PATH}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seeding logic from living_data_brain.py
    # ... (add the full seeding logic here)

    session.commit()
    session.close()

# --- Main App Logic ---

if not os.path.exists(DB_FILE_PATH):
    st.title("🧠 Welcome to the Living Data Brain Setup")
    st.write("The database file has not been created yet.")
    st.write("Click the button below to create and seed the database. This may take a moment.")

    if st.button("Create and Seed Database", type="primary"):
        with st.spinner("Creating database..."):
            init_database()
        st.success("Database created successfully!")
        st.write("The application will now reload to display the dashboard.")
        st.rerun()
else:
    # --- Main Dashboard UI ---
    st.title("🧠 Living Data Brain")

    # (The entire Streamlit UI from living_data_brain_ui.py goes here)
    # ...
    # --- Database Connection ---
    @st.cache_resource
    def get_engine():
        return create_engine(f"sqlite:///{DB_FILE_PATH}")

    engine = get_engine()

    @st.cache_data
    def get_table_names():
        inspector = inspect(engine)
        return inspector.get_table_names()

    @st.cache_data
    def load_data(table_name):
        return pd.read_sql_table(table_name, engine)

    # --- UI Layout ---
    tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "🗂️ Data Explorer", "📊 Advanced Visualizations"])

    # (The rest of the UI code...)

