import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect
import os
from pathlib import Path
import matplotlib.pyplot as plt

# --- Configuration ---
# Database file path.  Use environment variable `LIVING_DB_FILE_PATH` if set,
# otherwise default to a local file `living_data_brain.db` in the project root.
DB_FILE_PATH = os.getenv("LIVING_DB_FILE_PATH")
if not DB_FILE_PATH:
    # Determine project root: this file resides in the root of the repository
    repo_root = Path(__file__).resolve().parents[1]
    DB_FILE_PATH = str(repo_root / "living_data_brain.db")

# --- Page Config ---
st.set_page_config(
    page_title="Living Data Brain UI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Database Connection ---
@st.cache_resource
def get_engine():
    """Create a SQLAlchemy engine."""
    if not os.path.exists(DB_FILE_PATH):
        st.error(f"Database file not found at: {DB_FILE_PATH}")
        st.stop()
    return create_engine(f"sqlite:///{DB_FILE_PATH}")

engine = get_engine()

@st.cache_data
def get_table_names():
    """Get a list of all table names in the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

@st.cache_data
def load_data(table_name):
    """Load data from a specific table into a pandas DataFrame."""
    try:
        return pd.read_sql_table(table_name, engine)
    except Exception as e:
        st.error(f"Could not load data from table '{table_name}': {e}")
        return pd.DataFrame()

# --- UI Layout ---

st.title("🧠 Living Data Brain")

# --- Create Tabs ---
tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "🗂️ Data Explorer", "📊 Advanced Visualizations"])

# --- Tab 1: Dashboard ---
with tab1:
    st.header("Real-time Ecosystem Dashboard")

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    try:
        runs_df = load_data("runs")
        if not runs_df.empty:
            total_runs = len(runs_df)
            avg_confidence = runs_df["confidence_score"].mean()
            col1.metric("Total Workflow Runs", f"{total_runs:,}")
            col2.metric("Avg. Confidence Score", f"{avg_confidence:.2%}")

        strategies_df = load_data("strategies")
        if not strategies_df.empty:
            total_strategies = len(strategies_df)
            col3.metric("Total Strategies", f"{total_strategies}")

        financial_df = load_data("financial_metrics")
        if not financial_df.empty:
            total_revenue = financial_df[financial_df['name'] == 'Quarterly Revenue']['value'].sum()
            col4.metric("Total Revenue", f"${total_revenue:,.2f}")
    except Exception as e:
        st.warning(f"Could not load key metrics: {e}")

    st.divider()

    # Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Runs Over Time")
        if not runs_df.empty:
            runs_df['run_ts'] = pd.to_datetime(runs_df['run_ts'])
            runs_over_time = runs_df.set_index('run_ts').resample('D').size()
            st.line_chart(runs_over_time, use_container_width=True)
        else:
            st.write("No run data to visualize.")

    with col2:
        st.subheader("Script Distribution")
        if not runs_df.empty:
            script_counts = runs_df["script_name"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(script_counts, labels=script_counts.index, autopct="%1.1f%%", startangle=90)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)
        else:
            st.write("No script data to visualize.")

# --- Tab 2: Data Explorer ---
with tab2:
    st.header("Interactive Data Explorer")

    # Sidebar for table selection
    st.sidebar.title("Database Explorer")
    table_names = get_table_names()
    if not table_names:
        st.warning("No tables found in the database.")
        st.stop()

    selected_table = st.sidebar.selectbox("Select a table to view", table_names, key="data_explorer_table_select")

    # Display the selected table
    if selected_table:
        st.subheader(f"Table: `{selected_table}`")
        data_df = load_data(selected_table)

        # Search bar
        search_query = st.text_input(f"Search in {selected_table}", key=f"search_{selected_table}")
        if search_query:
            # Simple string search across all columns
            mask = data_df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)
            data_df = data_df[mask]

        if not data_df.empty:
            st.dataframe(data_df, use_container_width=True)
        else:
            st.write(f"No data matching your search in table '{selected_table}'.")

# --- Tab 3: Advanced Visualizations ---
with tab3:
    st.header("Advanced Visualizations")

    # Strategy Performance Chart
    st.subheader("Strategy Performance")
    strategies_df = load_data("strategies")
    if not strategies_df.empty:
        st.bar_chart(strategies_df.set_index("id")["avg_reward"], use_container_width=True)
        st.write("This chart shows the average reward for each strategy, giving an indication of which strategies are performing the best.")
    else:
        st.write("No strategy data to visualize.")