
from __future__ import annotations

"""
The Living Data Brain (formerly Unified Advanced Export System)
Version 3.0.0

This script serves as the central data hub and export engine for the entire
CESAR and Jerry Agent ecosystem. It defines the master database schema and
provides a comprehensive suite of tools for exporting data to various formats,
including CSV, Excel, Markdown, and a detailed PDF report with charts and
code listings.

Key Features:
- Unified Schema: Integrates operational metadata with rich data from agent
  executions, including business processes, knowledge fragments, financial
  metrics, and agent strategies.
- ExecutionReceipt Integration: Captures detailed data from agent runs,
  including tool calls and reasoning steps.
- Comprehensive Exports: Generates detailed reports that provide a holistic
  view of the entire AI ecosystem.
- PhD Quality Code: Well-documented, modular, robust, and follows best
  practices.
"""

import io
import os
import sys
import json
import logging
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional, Generator, Tuple

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, Preformatted,
)
from reportlab.lib.enums import TA_CENTER

# SQLAlchemy imports
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Float, Boolean, ForeignKey,
    Enum as SAEnum, JSON as SAJSON, text, func, select, Text, Date, UniqueConstraint
)
from sqlalchemy.orm import joinedload, declarative_base, relationship, sessionmaker
from sqlalchemy.exc import OperationalError

# ─────────────────────────────────────────────────────────────
# Centralized Configuration
# ─────────────────────────────────────────────────────────────

def _compute_allowed_code_dir() -> Path:
    """Compute a safe default for ALLOWED_CODE_DIR even if __file__ is undefined."""
    if "__file__" in globals():
        try:
            return Path(os.path.dirname(os.path.abspath(__file__))).resolve()
        except Exception:
            return Path().resolve()
    return Path().resolve()

ALLOWED_CODE_DIR = _compute_allowed_code_dir()
THIS_FILE: Optional[Path] = Path(os.path.abspath(__file__)) if "__file__" in globals() else None

def _is_relative_to(p: Path, base: Path) -> bool:
    """Python <3.9 compatibility for Path.is_relative_to."""
    try:
        return p.is_relative_to(base)
    except AttributeError:
        try:
            p.relative_to(base)
            return True
        except ValueError:
            return False

PDF_STYLES: Dict[str, Any] = {
    "colors": {
        "primary": colors.HexColor("#1a365d"), "secondary": colors.HexColor("#2c5282"),
        "accent": colors.HexColor("#38a169"), "text_light": colors.whitesmoke,
        "bg_light": colors.HexColor("#edf2f7"), "grid": colors.HexColor("#cbd5e0"),
        "table_header": colors.HexColor("#4a5568"), "row_alt": colors.HexColor("#f7fafc"),
    },
    "fonts": {"normal": "Helvetica", "bold": "Helvetica-Bold", "italic": "Helvetica-Oblique", "code": "Courier"},
    "title_size": 24, "heading1_size": 16, "code_font_size": 7, "code_leading": 9,
}

# ─────────────────────────────────────────────────────────────
# Master Database Schema (The Living Data Brain)
# ─────────────────────────────────────────────────────────────

Base = declarative_base()


def utcnow() -> datetime:
    """Return a timezone-aware UTC timestamp suitable for database defaults."""
    return datetime.now(timezone.utc)

class ExportFormat(str):
    CSV = "csv"; PDF = "pdf"; EXCEL = "excel"; MARKDOWN = "markdown"

# --- Core Execution & Agent Tables ---

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True)
    script_name = Column(String, nullable=True)
    run_ts = Column(DateTime(timezone=True), default=utcnow)
    execution_time_ms = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    learning_reward = Column(Float, nullable=True)
    output_payload = Column(SAJSON)
    meta = Column(SAJSON)
    step_runs = relationship("StepRun", back_populates="run", cascade="all, delete-orphan")
    reflections = relationship("ReflectionLog", back_populates="run", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCallLog", back_populates="run", cascade="all, delete-orphan")
    reasoning_steps = relationship("ReasoningStep", back_populates="run", cascade="all, delete-orphan")

class Script(Base):
    __tablename__ = "scripts"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    path = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    version = Column(String, default="1.0.0")
    success_rate = Column(Float, nullable=True)
    total_runs = Column(Integer, default=0)
    snapshots = relationship("CodeSnapshot", back_populates="script", cascade="all, delete-orphan")

class StepRun(Base):
    __tablename__ = "step_runs"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    status = Column(String, default="success")
    run = relationship("Run", back_populates="step_runs")

class ReflectionLog(Base):
    __tablename__ = "reflections"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    reflection_ts = Column(DateTime(timezone=True), default=utcnow)
    insight_type = Column(String, nullable=True)
    pattern_detected = Column(String, nullable=True)
    reward = Column(Float, nullable=True)
    penalty = Column(Float, nullable=True)
    proposed_action = Column(SAJSON, nullable=True)
    run = relationship("Run", back_populates="reflections")

class CodeSnapshot(Base):
    __tablename__ = "code_snapshots"
    id = Column(Integer, primary_key=True)
    script_id = Column(Integer, ForeignKey("scripts.id"))
    created_ts = Column(DateTime(timezone=True), default=utcnow)
    content = Column(Text)
    script = relationship("Script", back_populates="snapshots")

class ToolCallLog(Base):
    __tablename__ = "tool_call_logs"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    tool_name = Column(String, nullable=False)
    arguments = Column(SAJSON)
    result_summary = Column(Text)
    latency_ms = Column(Integer)
    run = relationship("Run", back_populates="tool_calls")

class ReasoningStep(Base):
    __tablename__ = "reasoning_steps"
    id = Column(Integer, primary_key=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    step_order = Column(Integer, nullable=False)
    description = Column(Text)
    run = relationship("Run", back_populates="reasoning_steps")

# --- Business & Strategy Tables ---

class Strategy(Base):
    __tablename__ = "strategies"
    id = Column(String, primary_key=True)
    family = Column(String, nullable=False)
    description = Column(String)
    weight = Column(Float, default=1.0)
    num_trials = Column(Integer, default=0)
    total_reward = Column(Float, default=0.0)
    avg_reward = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), default=utcnow)

class BusinessProcess(Base):
    __tablename__ = "business_processes"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    version = Column(String, default="1.0")
    yaml_definition = Column(Text)

class BusinessProcessRun(Base):
    __tablename__ = "business_process_runs"
    id = Column(Integer, primary_key=True)
    process_id = Column(Integer, ForeignKey("business_processes.id"))
    run_id = Column(Integer, ForeignKey("runs.id"))
    status = Column(String, default="started")
    input_data = Column(SAJSON)
    output_data = Column(SAJSON)

# --- Knowledge & Financial Tables ---

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String)
    uri = Column(String)

class KnowledgeFragment(Base):
    __tablename__ = "knowledge_fragments"
    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("knowledge_sources.id"))
    content = Column(Text)
    faiss_index_id = Column(String)
    graph_node_id = Column(String)
    fragment_metadata = Column(SAJSON)

class FinancialMetric(Base):
    __tablename__ = "financial_metrics"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime(timezone=True))

class RevenueForecast(Base):
    __tablename__ = "revenue_forecasts"
    id = Column(Integer, primary_key=True)
    forecast_date = Column(DateTime(timezone=True), default=utcnow)
    period_start = Column(Date)
    period_end = Column(Date)
    predicted_revenue = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)


class DashboardKPI(Base):
    __tablename__ = "dashboard_kpis"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    sql_query = Column(Text, nullable=False)
    description = Column(Text)
    value_format = Column(String, default="number")
    created_ts = Column(DateTime(timezone=True), default=utcnow)


class DashboardVisualization(Base):
    __tablename__ = "dashboard_visualizations"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    chart_type = Column(String, nullable=False, default="line")
    sql_query = Column(Text, nullable=False)
    x_column = Column(String, nullable=False)
    y_column = Column(String, nullable=False)
    color_column = Column(String)
    description = Column(Text)
    created_ts = Column(DateTime(timezone=True), default=utcnow)


class WorkflowAutomation(Base):
    __tablename__ = "workflow_automations"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    objective = Column(Text)
    status = Column(String, default="draft")
    owner = Column(String)
    last_reviewed = Column(DateTime(timezone=True))
    created_ts = Column(DateTime(timezone=True), default=utcnow)


class WorkflowAutomationLog(Base):
    __tablename__ = "workflow_automation_logs"
    id = Column(Integer, primary_key=True)
    automation_id = Column(Integer, ForeignKey("workflow_automations.id"), nullable=False)
    summary = Column(Text, nullable=False)
    source = Column(String, default="manual")
    created_ts = Column(DateTime(timezone=True), default=utcnow)
    automation = relationship("WorkflowAutomation", backref="logs")


class GovernanceResource(Base):
    __tablename__ = "governance_resources"
    __table_args__ = (UniqueConstraint("file_path", name="uq_governance_resource_path"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=False)
    source = Column(String)
    metadata_json = Column(SAJSON)
    created_ts = Column(DateTime(timezone=True), default=utcnow)


class NLPResource(Base):
    __tablename__ = "nlp_resources"
    __table_args__ = (UniqueConstraint("file_path", name="uq_nlp_resource_path"),)

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    sha256 = Column(String, nullable=False)
    category = Column(String)
    metadata_json = Column(SAJSON)
    created_ts = Column(DateTime(timezone=True), default=utcnow)


class AutomationRegistryEntry(Base):
    __tablename__ = "automation_registry"
    __table_args__ = (UniqueConstraint("identifier", name="uq_automation_identifier"),)

    id = Column(Integer, primary_key=True)
    identifier = Column(String, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String)
    endpoint = Column(String)
    auth = Column(String)
    quality_score = Column(Float)
    metadata_json = Column(SAJSON)
    created_ts = Column(DateTime(timezone=True), default=utcnow)


class SkillNodeRecord(Base):
    __tablename__ = "skill_nodes"
    __table_args__ = (UniqueConstraint("node_id", name="uq_skill_node_id"),)

    id = Column(Integer, primary_key=True)
    node_id = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    department = Column(String)
    version = Column(String)
    status = Column(String)
    metadata_json = Column(SAJSON)
    created_ts = Column(DateTime(timezone=True), default=utcnow)

def init_living_data_brain_db(db_url: str):
    engine = create_engine(db_url, future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    return engine, SessionLocal

# ─────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# ─────────────────────────────────────────────────────────────
# The ExportEngine Class
# ─────────────────────────────────────────────────────────────

class ExportEngine:
    """
    The Living Data Brain's enterprise-grade export system.
    Handles export formats with professional quality, security, and robustness.
    """

    def __init__(self, db_url: str = "sqlite:///living_data_brain.db", export_dir: Path | str = "exports"):
        self.engine, self._SessionLocal = init_living_data_brain_db(db_url)
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True, parents=True)
        self._styles = getSampleStyleSheet()
        self._setup_pdf_styles()

    @contextmanager
    def session_scope(self) -> Generator[sessionmaker, None, None]:
        session = self._SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            logger.exception("Session rollback due to exception")
            raise
        finally:
            session.close()

    def _ts(self) -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _outfile(self, stem: str, suffix: str) -> Path:
        return self.export_dir / f"{stem}_{self._ts()}{suffix}"

    @staticmethod
    def _pct(value: Optional[float]) -> str:
        try:
            return f"{float(value):.2%}"
        except (ValueError, TypeError, AttributeError):
            return "N/A"

    def _excel_engine(self) -> str:
        try:
            import openpyxl; return "openpyxl"
        except ImportError:
            try:
                import xlsxwriter; return "xlsxwriter"
            except ImportError:
                return "openpyxl"

    def _setup_pdf_styles(self):
        self.title_style = ParagraphStyle("CustomTitle", parent=self._styles["Heading1"], fontName=PDF_STYLES["fonts"]["bold"], fontSize=PDF_STYLES["title_size"], textColor=PDF_STYLES["colors"]["primary"], spaceAfter=30, alignment=TA_CENTER)
        self.heading_style = ParagraphStyle("CustomHeading", parent=self._styles["Heading2"], fontName=PDF_STYLES["fonts"]["bold"], fontSize=PDF_STYLES["heading1_size"], textColor=PDF_STYLES["colors"]["secondary"], spaceAfter=12, spaceBefore=12)
        self.code_style = ParagraphStyle("Code", parent=self._styles["Code"], fontName=PDF_STYLES["fonts"]["code"], fontSize=PDF_STYLES["code_font_size"], leading=PDF_STYLES["code_leading"], leftIndent=10, rightIndent=10)

    def seed_demo_data(self, n_runs: int = 20, force: bool = False) -> None:
        with self.session_scope() as s:
            if s.query(Run).count() and not force:
                return
            if force:
                for table in reversed(Base.metadata.sorted_tables):
                    s.execute(table.delete())

            # Seed Scripts and Runs
            this_file_path: Optional[str] = str(THIS_FILE.resolve()) if THIS_FILE else None
            sc1 = Script(name="ingest_pipeline.py", path=this_file_path, active=True, version="1.2.0", success_rate=0.88, total_runs=100)
            sc2 = Script(name="living_data_brain.py", path=this_file_path, active=True, version="3.0.0", success_rate=0.93, total_runs=75)
            s.add_all([sc1, sc2])
            s.flush()

            base_ts = utcnow() - timedelta(days=n_runs)
            for i in range(n_runs):
                r = Run(script_name=sc1.name if i % 2 == 0 else sc2.name, run_ts=base_ts + timedelta(hours=i * 3), cost_usd=0.02 * i, confidence_score=0.5 + (i % 6) * 0.08)
                s.add(r)
                s.flush()
                snapshot_content = THIS_FILE.read_text(encoding="utf-8") if THIS_FILE and THIS_FILE.exists() else "# snapshot unavailable"
                s.add(CodeSnapshot(script_id=sc1.id, content=snapshot_content))
                s.add(ReflectionLog(run_id=r.id, reward=(i % 7) * 0.1, pattern_detected=("drift" if i % 5 == 0 else None)))
                s.add(ToolCallLog(run_id=r.id, tool_name="read_file", arguments={"path": "/path/to/file"}, latency_ms=150))
                s.add(ReasoningStep(run_id=r.id, step_order=0, description="Agent decided to read a file."))

            # Seed Strategies
            s.add(Strategy(id="finance.forecast.v1", family="finance_reasoning", description="Financial forecasting with Monte Carlo simulation", avg_reward=0.85, num_trials=50))
            s.add(Strategy(id="general.cot.v1", family="general", description="Chain-of-thought reasoning", avg_reward=0.72, num_trials=120))

            # Seed Business Processes
            bp = BusinessProcess(
                name="AP Invoice Processing",
                description="Automated processing of accounts payable invoices across ingestion, validation, and reconciliation stages.",
                yaml_definition=(
                    "stages:\n"
                    "  - name: ingest-invoice\n"
                    "    tasks:\n"
                    "      - load_email_attachment\n"
                    "      - normalize_vendor_fields\n"
                    "  - name: validate\n"
                    "    tasks:\n"
                    "      - cross_check_po\n"
                    "      - verify_tax_codes\n"
                    "      - flag_anomalies\n"
                    "  - name: reconcile\n"
                    "    tasks:\n"
                    "      - enter_erp_journal\n"
                    "      - route_exception_to_analyst\n"
                ),
            )
            s.add(bp)
            s.flush()
            s.add(BusinessProcessRun(process_id=bp.id, run_id=r.id, status="completed"))

            # Seed Knowledge and Financial Data
            ks = KnowledgeSource(name="Q3 Financial Report", type="document", uri="/docs/q3.pdf")
            s.add(ks)
            s.flush()
            s.add(KnowledgeFragment(source_id=ks.id, content="Revenue was up 20% YoY.", faiss_index_id="vec_123"))
            now_utc = utcnow()
            s.add(FinancialMetric(name="Quarterly Revenue", value=1.2e6, unit="USD", timestamp=now_utc))
            today_utc = now_utc.date()
            s.add(
                RevenueForecast(
                    period_start=today_utc,
                    period_end=(now_utc + timedelta(days=90)).date(),
                    predicted_revenue=1.5e6,
                )
            )

            # Seed Dashboard customization data
            s.add(DashboardKPI(
                name="Monthly Run Volume",
                description="Count of runs executed in the last 30 days",
                sql_query="SELECT COUNT(*) AS value FROM runs WHERE run_ts >= DATE('now', '-30 day')",
                value_format="number",
            ))
            s.add(DashboardKPI(
                name="Average Confidence",
                description="Average run confidence over entire history",
                sql_query="SELECT AVG(confidence_score) AS value FROM runs",
                value_format="percentage",
            ))
            s.add(DashboardVisualization(
                name="Confidence Trend",
                description="Average confidence score per day",
                chart_type="line",
                sql_query="SELECT DATE(run_ts) AS run_date, AVG(confidence_score) AS avg_confidence FROM runs GROUP BY DATE(run_ts) ORDER BY DATE(run_ts)",
                x_column="run_date",
                y_column="avg_confidence",
            ))
            automation = WorkflowAutomation(
                name="Invoice Reconciliation",
                objective="Match invoices against purchase orders and flag mismatches",
                status="active",
                owner="CESAR Ops",
                last_reviewed=utcnow(),
            )
            s.add(automation)
            s.flush()
            s.add(WorkflowAutomationLog(
                automation_id=automation.id,
                summary="Initial automation configured with 3-stage validation and nightly reconciliation run.",
                source="system",
            ))

    def export_excel(self) -> Path:
        output_path = self._outfile("living_data_brain_analysis", ".xlsx")
        with pd.ExcelWriter(output_path, engine=self._excel_engine()) as writer:
            with self.session_scope() as s:
                for table in Base.metadata.sorted_tables:
                    df = pd.read_sql_query(select(table), self.engine)
                    df.to_excel(writer, sheet_name=table.name, index=False)
        logger.info("Excel export complete: %s", output_path)
        return output_path

    def export_pdf_comprehensive(self, max_code_kb: int = 512) -> Path:
        output_path = self._outfile("comprehensive_report", ".pdf")
        doc = SimpleDocTemplate(str(output_path), pagesize=letter, topMargin=1*inch, bottomMargin=0.75*inch)
        story: List[Any] = []
        with self.session_scope() as s:
            self._add_title_page(story)
            self._add_executive_summary(story, s)
            self._add_recent_runs_table(story, s)
            story.append(PageBreak())
            self._add_strategy_performance_table(story, s)
            story.append(PageBreak())
            self._add_charts(story, s)
            story.append(PageBreak())
            self._add_code_listings(story, s, max_code_kb)
        doc.build(story)
        logger.info("Comprehensive PDF report complete: %s", output_path)
        return output_path

    def _add_title_page(self, story: list):
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Living Data Brain", self.title_style))
        story.append(Paragraph("Comprehensive Ecosystem Analysis Report", self._styles["Heading2"]))
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", self._styles["Normal"]))
        story.append(Paragraph("Powered by CESAR.AI & The Jerry Agent", self._styles["Italic"]))

    def _add_executive_summary(self, story: list, s: sessionmaker):
        story.append(Paragraph("Executive Summary", self.heading_style))
        summary_row = s.execute(text("SELECT (SELECT COUNT(*) FROM runs) AS total_runs, (SELECT COUNT(*) FROM scripts WHERE active = 1) AS total_scripts, (SELECT COUNT(*) FROM reflections) AS total_reflections, (SELECT AVG(confidence_score) FROM runs) AS avg_confidence")).first()
        summary_data = [
            ["Metric", "Value"],
            ["Total Workflow Runs", str(summary_row.total_runs if summary_row else 'N/A')],
            ["Active Scripts", str(summary_row.total_scripts if summary_row else 'N/A')],
            ["Learning Reflections", str(summary_row.total_reflections if summary_row else 'N/A')],
            ["Average Confidence Score", self._pct(summary_row.avg_confidence if summary_row else 0.0)],
        ]
        table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PDF_STYLES["colors"]["secondary"]), ("TEXTCOLOR", (0, 0), (-1, 0), PDF_STYLES["colors"]["text_light"]), ("FONTNAME", (0, 0), (-1, 0), PDF_STYLES["fonts"]["bold"]), ("BACKGROUND", (0, 1), (-1, -1), PDF_STYLES["colors"]["bg_light"]), ("GRID", (0, 0), (-1, -1), 1, PDF_STYLES["colors"]["grid"])]))
        story.append(table)
        story.append(Spacer(1, 0.5 * inch))

    def _add_recent_runs_table(self, story: list, s: sessionmaker):
        story.append(Paragraph("Recent Workflow Executions", self.heading_style))
        recent_runs: List[Run] = s.query(Run).order_by(Run.run_ts.desc()).limit(10).all()
        runs_data = [["Timestamp", "Script", "Confidence"]]
        for run in recent_runs:
            runs_data.append([run.run_ts.strftime("%Y-%m-%d %H:%M") if run.run_ts else "", (run.script_name or "")[:30], self._pct(run.confidence_score)])
        table = Table(runs_data, colWidths=[1.5 * inch, 3 * inch, 1.5 * inch])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PDF_STYLES["colors"]["table_header"]), ("TEXTCOLOR", (0, 0), (-1, 0), PDF_STYLES["colors"]["text_light"]), ("FONTNAME", (0, 0), (-1, 0), PDF_STYLES["fonts"]["bold"]), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PDF_STYLES["colors"]["row_alt"]]), ("GRID", (0, 0), (-1, -1), 1, PDF_STYLES["colors"]["grid"])]))
        story.append(table)

    def _add_strategy_performance_table(self, story: list, s: sessionmaker):
        story.append(Paragraph("Strategy Performance", self.heading_style))
        strategies: List[Strategy] = s.query(Strategy).order_by(Strategy.avg_reward.desc()).limit(10).all()
        if not strategies:
            story.append(Paragraph("No strategy data available.", self._styles["Normal"]))
            return
        strategy_data = [["Strategy ID", "Family", "Avg Reward", "Trials"]]
        for strat in strategies:
            strategy_data.append([strat.id, strat.family, f"{strat.avg_reward:.3f}", str(strat.num_trials)])
        table = Table(strategy_data, colWidths=[2 * inch, 1.5 * inch, 1 * inch, 1 * inch])
        table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), PDF_STYLES["colors"]["accent"]), ("TEXTCOLOR", (0, 0), (-1, 0), PDF_STYLES["colors"]["text_light"]), ("GRID", (0, 0), (-1, -1), 1, PDF_STYLES["colors"]["grid"])]))
        story.append(table)

    def _add_charts(self, story: list, s: sessionmaker):
        story.append(Paragraph("Key Charts", self.heading_style))
        try:
            import matplotlib; matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            df = pd.read_sql_query(select(Run.run_ts, Run.cost_usd, Run.confidence_score), self.engine)
            if df.empty or df.isnull().all().all():
                story.append(Paragraph("No data available for charts.", self._styles["Normal"]))
                return
            if len(df) > 5000:
                df = df.sort_values("run_ts").iloc[:: max(1, len(df)//1000), :]
            for col, title, ylabel in [("cost_usd", "Cost over Time", "Cost (USD)"), ("confidence_score", "Confidence over Time", "Confidence Score")]:
                if col in df and df[col].notna().any():
                    buf = io.BytesIO()
                    plt.figure(figsize=(8, 4)); plt.plot(df["run_ts"], df[col].fillna(0)); plt.title(title); plt.ylabel(ylabel); plt.gcf().autofmt_xdate(); plt.tight_layout(); plt.savefig(buf, format="png", dpi=150); plt.close(); buf.seek(0)
                    story.append(Image(buf, width=6.5 * inch, height=3.25 * inch))
                    story.append(Spacer(1, 0.2 * inch))
        except Exception as e:
            logger.warning("Chart rendering failed: %s. Matplotlib might be missing.", e)
            story.append(Paragraph(f"Charts unavailable: {e}", self._styles["Normal"]))

    def _add_code_listings(self, story: list, s: sessionmaker, max_kb: int):
        story.append(Paragraph("Source Code Repository", self.heading_style))
        scripts: List[Script] = s.query(Script).filter(Script.active == True).options(joinedload(Script.snapshots)).all()
        byte_limit = max(64, int(max_kb)) * 1024
        for script in scripts:
            story.append(Paragraph(f"Script: {script.name}", self._styles["Heading3"]))
            code, truncated, origin = self._get_secure_code(script, byte_limit)
            story.append(Paragraph(f"Version: {script.version} | Source: {origin}", self._styles["Italic"]))
            story.append(Spacer(1, 0.1 * inch))
            if code:
                story.append(Preformatted(code, self.code_style))
                if truncated: story.append(Paragraph(f"[Truncated to {max_kb}KB]", self._styles["Italic"]))
            else:
                story.append(Paragraph("Source code not available.", self._styles["Normal"]))
            story.append(Spacer(1, 0.25 * inch))

    @staticmethod
    def _utf8_prefix(data: bytes) -> str:
        view = data
        while True:
            try: return view.decode("utf-8")
            except UnicodeDecodeError:
                view = view[:-1]
                if not view: return ""

    def _get_secure_code(self, script: Script, byte_limit: int) -> Tuple[str, bool, str]:
        if getattr(script, "snapshots", None):
            latest_snapshot = max(script.snapshots, key=lambda sn: sn.created_ts)
            data = latest_snapshot.content.encode("utf-8", errors="replace")
            if len(data) > byte_limit: return self._utf8_prefix(data[:byte_limit]), True, "Database (Snapshot)"
            return data.decode("utf-8", errors="replace"), False, "Database (Snapshot)"
        if not getattr(script, "path", None): return "", False, "N/A"
        try:
            p = Path(script.path).resolve()
            if not _is_relative_to(p, ALLOWED_CODE_DIR):
                logger.error("SECURITY VIOLATION: Path traversal attempt blocked for %s", p)
                return f"Error: Access denied to path {script.path}", False, "Filesystem (Blocked)"
            if not p.is_file(): raise FileNotFoundError(f"Path is not a file: {p}")
            read, chunks = 0, []
            with p.open("rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    if read + len(chunk) >= byte_limit:
                        remaining = byte_limit - read
                        if remaining > 0: chunks.append(chunk[:remaining]); read += remaining
                        break
                    chunks.append(chunk); read += len(chunk)
            data = b"".join(chunks)
            truncated = p.stat().st_size > len(data)
            return self._utf8_prefix(data), truncated, "Filesystem"
        except Exception as e:
            logger.error("Failed to read source file %s: %s", script.path, e)
            return f"Error reading source: {e}", False, "Filesystem (Error)"

if __name__ == "__main__":
    engine = ExportEngine()
    engine.seed_demo_data(force=True)
    engine.export_excel()
    engine.export_pdf_comprehensive()
    print("Living Data Brain exports generated successfully.")
