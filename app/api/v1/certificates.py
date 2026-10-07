from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import RecipientCertificate, RecipientStatus
from app.schemas import VerificationResponse

router = APIRouter(prefix="/certificates", tags=["Certificates"])

@router.get("/{cert_id}/download", summary="Download Individual Certificate")
def download_certificate(cert_id: str, db: Session = Depends(get_db)):
    """
    Downloads the generated certificate file (PDF/PNG) for a recipient.
    """
    recipient = db.query(RecipientCertificate).filter(RecipientCertificate.id == cert_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail=f"Certificate with ID '{cert_id}' not found.")

    if recipient.status != RecipientStatus.SUCCESS or not recipient.file_path:
        raise HTTPException(
            status_code=400,
            detail=f"Certificate '{cert_id}' is not in SUCCESS state (current status: {recipient.status})."
        )

    file_path = Path(recipient.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=500, detail="Certificate file missing from server storage.")

    media_type = "application/pdf" if file_path.suffix.lower() == ".pdf" else "image/png"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=recipient.file_name or file_path.name
    )

@router.get("/{cert_id}/verify", response_model=VerificationResponse, summary="Verify Certificate Authenticity")
def verify_certificate(cert_id: str, db: Session = Depends(get_db)):
    """
    Public verification endpoint to validate certificate authenticity by ID.
    """
    recipient = db.query(RecipientCertificate).filter(RecipientCertificate.id == cert_id).first()
    if not recipient or recipient.status != RecipientStatus.SUCCESS:
        return VerificationResponse(
            valid=False,
            certificate_id=cert_id,
            verification_message="INVALID OR UNISSUED CERTIFICATE. No matching official record found."
        )

    job = recipient.job
    return VerificationResponse(
        valid=True,
        certificate_id=recipient.id,
        recipient_name=recipient.recipient_name,
        recipient_email=recipient.recipient_email,
        title=job.title if job else "N/A",
        issuer=job.issuer if job else "N/A",
        issue_date=job.issue_date if job else "N/A",
        custom_text=recipient.custom_text,
        created_at=recipient.created_at,
        verification_message="OFFICIAL CERTIFICATE VERIFIED. Authenticity confirmed by issuing authority."
    )
