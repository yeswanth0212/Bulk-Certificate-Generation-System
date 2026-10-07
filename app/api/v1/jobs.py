from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pathlib import Path
from app.database import get_db, SessionLocal
from app.models import CertificateJob, RecipientCertificate, RecipientStatus
from app.schemas import JobCreate, JobResponse, RecipientOutput
from app.services.job_service import create_job, process_job
from app.services.zip_service import create_job_zip_archive
from app.config import settings

router = APIRouter(prefix="/jobs", tags=["Certificate Jobs"])

def run_job_in_background(job_id: str, output_format: str):
    """Worker task helper that creates its own DB session for background processing."""
    db = SessionLocal()
    try:
        process_job(db, job_id, output_format)
    finally:
        db.close()

def build_job_response(job: CertificateJob) -> JobResponse:
    """Helper to convert database ORM model to JobResponse schema with URLs."""
    progress = 0.0
    if job.total_recipients > 0:
        progress = round((job.processed_count / job.total_recipients) * 100, 2)

    recipients_out = []
    for r in job.recipients:
        rec_dict = {
            "id": r.id,
            "recipient_name": r.recipient_name,
            "recipient_email": r.recipient_email,
            "custom_text": r.custom_text,
            "status": r.status,
            "error_message": r.error_message,
            "created_at": r.created_at,
            "download_url": f"{settings.BASE_URL}/api/v1/certificates/{r.id}/download" if r.status == RecipientStatus.SUCCESS else None,
            "verify_url": f"{settings.BASE_URL}/api/v1/certificates/{r.id}/verify" if r.status == RecipientStatus.SUCCESS else None
        }
        recipients_out.append(RecipientOutput(**rec_dict))

    zip_url = f"{settings.BASE_URL}/api/v1/jobs/{job.id}/download-zip" if job.success_count > 0 else None

    return JobResponse(
        id=job.id,
        title=job.title,
        issuer=job.issuer,
        issue_date=job.issue_date,
        signatory_name=job.signatory_name,
        signatory_title=job.signatory_title,
        status=job.status,
        total_recipients=job.total_recipients,
        processed_count=job.processed_count,
        success_count=job.success_count,
        failure_count=job.failure_count,
        progress_percentage=progress,
        created_at=job.created_at,
        completed_at=job.completed_at,
        recipients=recipients_out,
        zip_download_url=zip_url
    )

@router.post("", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED, summary="Create Bulk Certificate Generation Job")
def submit_certificate_job(
    job_in: JobCreate,
    background_tasks: BackgroundTasks,
    sync: bool = Query(False, description="Set to true for synchronous generation in testing"),
    db: Session = Depends(get_db)
):
    """
    Submits a bulk certificate generation job.
    
    - Validates recipient list.
    - Queues generation in background (or synchronously if sync=true).
    - Returns job ID and initial pending status.
    """
    job = create_job(db, job_in)
    
    if sync:
        process_job(db, job.id, output_format=job_in.format)
        db.refresh(job)
    else:
        background_tasks.add_task(run_job_in_background, job.id, job_in.format)

    return build_job_response(job)

@router.get("/{job_id}", response_model=JobResponse, summary="Get Certificate Job Status & Progress")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Retrieves the status, progress metrics, recipient statuses, and certificate links for a job.
    """
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")
    return build_job_response(job)

@router.get("/{job_id}/download-zip", summary="Download ZIP of All Generated Certificates")
def download_job_zip(job_id: str, db: Session = Depends(get_db)):
    """
    Generates and returns a downloadable ZIP archive containing all certificates for a job.
    """
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail=f"Job with ID '{job_id}' not found.")

    if job.success_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No certificates were successfully generated for this job yet."
        )

    zip_path = create_job_zip_archive(job.id, job.recipients)
    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename=zip_path.name
    )
