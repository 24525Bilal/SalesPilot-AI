"""SalesPilot AI — SQLite Database Persistence."""

import sqlite3
import json
import os
from typing import Optional, List
from datetime import datetime

from app.models.schemas import FullResearchReport

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "salespilot.db")

def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            completed_at TEXT,
            intent_score INTEGER,
            report_data TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print(f"[DB] Initialized database at {DB_PATH}")

def save_job(report: FullResearchReport):
    """Save or update a research job in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    intent_score = None
    if report.buying_intent and hasattr(report.buying_intent, 'overall_score'):
        intent_score = report.buying_intent.overall_score
        
    completed_at = report.completed_at.isoformat() if report.completed_at else None
    
    # Store the entire object as JSON
    report_json = report.model_dump_json()
    
    cursor.execute('''
        INSERT INTO jobs (job_id, company_name, status, created_at, completed_at, intent_score, report_data)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            status=excluded.status,
            completed_at=excluded.completed_at,
            intent_score=excluded.intent_score,
            report_data=excluded.report_data
    ''', (
        report.job_id,
        report.company_name,
        report.status.value,
        report.created_at.isoformat(),
        completed_at,
        intent_score,
        report_json
    ))
    
    conn.commit()
    conn.close()

def get_job(job_id: str) -> Optional[FullResearchReport]:
    """Retrieve a job by ID from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT report_data FROM jobs WHERE job_id = ?', (job_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return FullResearchReport.model_validate_json(row[0])
    return None

def get_all_jobs() -> List[FullResearchReport]:
    """Retrieve all jobs, ordered by created_at descending."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT report_data FROM jobs ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    jobs = []
    for row in rows:
        try:
            jobs.append(FullResearchReport.model_validate_json(row[0]))
        except Exception as e:
            print(f"[DB] Error parsing job from DB: {e}")
            
    return jobs
