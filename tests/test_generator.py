import uuid
from pathlib import Path
from app.services.generator import render_certificate
from app.models import JobStatus, RecipientStatus
from app.services.job_service import create_job, process_job
from app.schemas import JobCreate, RecipientInput

def test_render_certificate_pdf_and_png(tmp_path):
    cert_id = str(uuid.uuid4())
    pdf_path = render_certificate(
        cert_id=cert_id,
        recipient_name="Test Recipient",
        course_title="Python Mastery",
        issuer_name="Test Academy",
        issue_date="October 2026",
        custom_text="Grade A",
        output_format="pdf"
    )
    assert pdf_path.exists()
    assert pdf_path.suffix == ".pdf"
    assert pdf_path.stat().st_size > 0

    png_path = render_certificate(
        cert_id=cert_id,
        recipient_name="Test Recipient",
        course_title="Python Mastery",
        issuer_name="Test Academy",
        issue_date="October 2026",
        custom_text="Grade A",
        output_format="png"
    )
    assert png_path.exists()
    assert png_path.suffix == ".png"
    assert png_path.stat().st_size > 0

def test_individual_certificate_failure_handling(db):
    """
    Tests that a single failing recipient record does NOT stop other valid certificates
    in the same job from being generated successfully.
    """
    # Create job with 1 valid recipient and 1 recipient with bad email bypassed at DB level to trigger background error
    job_in = JobCreate(
        title="Error Isolation Test Course",
        issuer="Test Org",
        recipients=[
            RecipientInput(name="Valid User", email="valid@test.com"),
            RecipientInput(name="Valid User Two", email="valid2@test.com")
        ]
    )
    job = create_job(db, job_in)

    # Manually corrupt second recipient's email in DB to force runtime rendering failure
    recipients = job.recipients
    recipients[1].recipient_email = "invalid-no-at-sign"
    db.commit()

    # Process job synchronously
    process_job(db, job.id, output_format="pdf")

    db.refresh(job)
    assert job.total_recipients == 2
    assert job.processed_count == 2
    assert job.success_count == 1
    assert job.failure_count == 1
    assert job.status == JobStatus.PARTIAL_SUCCESS

    # Recipient 0 should succeed
    r0 = db.query(type(recipients[0])).filter_by(id=recipients[0].id).first()
    assert r0.status == RecipientStatus.SUCCESS
    assert Path(r0.file_path).exists()

    # Recipient 1 should fail with detailed error message
    r1 = db.query(type(recipients[1])).filter_by(id=recipients[1].id).first()
    assert r1.status == RecipientStatus.FAILED
    assert "Invalid email format" in r1.error_message
