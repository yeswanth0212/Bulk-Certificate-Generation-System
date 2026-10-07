from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models import CertificateJob, RecipientCertificate, JobStatus, RecipientStatus
from app.schemas import JobCreate
from app.services.generator import render_certificate

def create_job(db: Session, job_in: JobCreate) -> CertificateJob:
    """Creates a new certificate job record and recipient placeholders in PENDING state."""
    issue_date_str = job_in.issue_date or datetime.now(timezone.utc).strftime("%B %d, %Y")
    
    job = CertificateJob(
        title=job_in.title,
        issuer=job_in.issuer,
        issue_date=issue_date_str,
        signatory_name=job_in.signatory_name or "Dr. Alex Vance",
        signatory_title=job_in.signatory_title or "Director of Certification",
        status=JobStatus.PENDING,
        total_recipients=len(job_in.recipients),
        processed_count=0,
        success_count=0,
        failure_count=0
    )
    db.add(job)
    db.flush()  # populate job.id

    for r_in in job_in.recipients:
        recipient = RecipientCertificate(
            job_id=job.id,
            recipient_name=r_in.name,
            recipient_email=r_in.email,
            custom_text=r_in.custom_text,
            status=RecipientStatus.PENDING
        )
        db.add(recipient)

    db.commit()
    db.refresh(job)
    return job

def process_job(db: Session, job_id: str, output_format: str = "pdf"):
    """
    Processes all recipient certificates for a given job in the background.
    Handles individual recipient errors gracefully without stopping the overall job execution.
    """
    job = db.query(CertificateJob).filter(CertificateJob.id == job_id).first()
    if not job:
        return

    job.status = JobStatus.PROCESSING
    db.commit()

    recipients = db.query(RecipientCertificate).filter(RecipientCertificate.job_id == job_id).all()

    for recipient in recipients:
        try:
            # 1. Validation check for simulated or edge-case invalid data
            if not recipient.recipient_name or len(recipient.recipient_name.strip()) == 0:
                raise ValueError("Recipient name is blank or invalid.")
            
            if "@" not in recipient.recipient_email:
                raise ValueError(f"Invalid email format: {recipient.recipient_email}")

            # 2. Render Certificate with Signatory parameters
            output_path = render_certificate(
                cert_id=recipient.id,
                recipient_name=recipient.recipient_name,
                course_title=job.title,
                issuer_name=job.issuer,
                issue_date=job.issue_date,
                custom_text=recipient.custom_text,
                signatory_name=job.signatory_name,
                signatory_title=job.signatory_title,
                output_format=output_format
            )

            # 3. Update Recipient Record on Success
            recipient.status = RecipientStatus.SUCCESS
            recipient.file_path = str(output_path)
            recipient.file_name = output_path.name
            recipient.error_message = None
            job.success_count += 1

        except Exception as err:
            # Handle individual certificate failure isolate from entire job
            recipient.status = RecipientStatus.FAILED
            recipient.error_message = str(err)
            job.failure_count += 1

        finally:
            job.processed_count += 1
            db.commit()

    # Finalize Job Status
    job.completed_at = datetime.now(timezone.utc)
    if job.failure_count == 0:
        job.status = JobStatus.COMPLETED
    elif job.success_count > 0:
        job.status = JobStatus.PARTIAL_SUCCESS
    else:
        job.status = JobStatus.FAILED

    db.commit()
