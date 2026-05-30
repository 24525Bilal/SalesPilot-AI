"""SalesPilot AI — Research API Router."""

import uuid
import asyncio
import json
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.models.schemas import (
    CompanyResearchRequest,
    FullResearchReport,
    ResearchStatusResponse,
    JobStatus,
    AgentStatus,
    AgentStatusEvent,
)
from app.agents.orchestrator import run_research_pipeline
from app.database import save_job, get_job, get_all_jobs

router = APIRouter()

# In-memory store for streaming events (DB handles persistence)
_job_events: dict[str, asyncio.Queue] = {}


@router.post("/research", response_model=dict)
async def start_research(request: CompanyResearchRequest):
    """Start an autonomous research workflow for a company."""
    job_id = str(uuid.uuid4())[:8]

    # Initialize the job
    report = FullResearchReport(
        job_id=job_id,
        company_name=request.company_name,
        status=JobStatus.QUEUED,
        created_at=datetime.utcnow(),
    )
    save_job(report)
    _job_events[job_id] = asyncio.Queue()

    # Run pipeline in background
    asyncio.create_task(_execute_research(job_id, request))

    return {
        "job_id": job_id,
        "status": "queued",
        "message": f"Research started for '{request.company_name}'",
        "stream_url": f"/api/research/{job_id}/stream",
    }


async def _execute_research(job_id: str, request: CompanyResearchRequest):
    """Execute the full research pipeline and update job state."""
    report = get_job(job_id)
    if not report:
        return
    event_queue = _job_events.get(job_id)
    if not event_queue:
        event_queue = asyncio.Queue()
        _job_events[job_id] = event_queue
        
    report.status = JobStatus.RUNNING
    save_job(report)

    try:
        # Run the orchestrator — it yields status events as agents complete
        final_report = await run_research_pipeline(
            company_name=request.company_name,
            domain=request.domain,
            event_queue=event_queue,
            job_report=report,  # pass stored report so incremental updates are live
        )

        # Update stored report with results
        report.company_profile = final_report.company_profile
        report.hiring_signals = final_report.hiring_signals
        report.funding_news = final_report.funding_news
        report.tech_stack = final_report.tech_stack
        report.pain_points = final_report.pain_points
        report.competitor_intel = final_report.competitor_intel
        report.buying_intent = final_report.buying_intent
        report.outreach_drafts = final_report.outreach_drafts
        report.status = JobStatus.COMPLETE
        report.completed_at = datetime.utcnow()
        save_job(report)

        # Signal completion
        await event_queue.put(
            AgentStatusEvent(
                agent_name="pipeline",
                status=AgentStatus.COMPLETE,
                message="All agents complete — research report ready",
            )
        )

    except Exception as e:
        report.status = JobStatus.FAILED
        save_job(report)
        await event_queue.put(
            AgentStatusEvent(
                agent_name="pipeline",
                status=AgentStatus.ERROR,
                message=f"Pipeline failed: {str(e)}",
            )
        )
        print(f"[Research] Pipeline error for job {job_id}: {e}")


@router.get("/research/{job_id}/stream")
async def stream_research_status(job_id: str):
    """SSE endpoint for real-time agent status updates."""
    if not get_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job_id not in _job_events:
        _job_events[job_id] = asyncio.Queue()

    async def event_generator() -> AsyncGenerator[dict, None]:
        queue = _job_events[job_id]
        while True:
            try:
                # Use a short 15s timeout to send frequent keepalive pings
                # This prevents the browser from dropping the SSE connection 
                # while waiting for slow local Ollama inference
                event = await asyncio.wait_for(queue.get(), timeout=15)
                yield {
                    "event": "agent_status",
                    "data": event.model_dump_json(),
                }
                # Stop streaming when pipeline is done
                if event.agent_name == "pipeline" and event.status in (
                    AgentStatus.COMPLETE,
                    AgentStatus.ERROR,
                ):
                    break
            except asyncio.TimeoutError:
                yield {"event": "ping", "data": "keepalive"}

    return EventSourceResponse(event_generator())


@router.get("/research/{job_id}", response_model=FullResearchReport)
async def get_research_results(job_id: str):
    """Get the full research report for a completed job."""
    report = get_job(job_id)
    if not report:
        raise HTTPException(status_code=404, detail="Job not found")
    return report


@router.get("/research", response_model=list[dict])
async def get_research_history():
    """List all past research jobs."""
    history = []
    jobs = get_all_jobs()
    for report in jobs:
        history.append({
            "job_id": report.job_id,
            "company_name": report.company_name,
            "status": report.status.value,
            "created_at": report.created_at.isoformat() + "Z",
            "completed_at": (report.completed_at.isoformat() + "Z") if report.completed_at else None,
            "intent_score": report.buying_intent.overall_score if report.buying_intent else None,
        })
    return history
