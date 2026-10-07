import zipfile
from pathlib import Path
from typing import List
from app.config import settings
from app.models import RecipientCertificate, RecipientStatus

def create_job_zip_archive(job_id: str, recipients: List[RecipientCertificate]) -> Path:
    """
    Bundles all successfully generated certificates for a job into a ZIP file.
    """
    zip_filename = f"job_{job_id}_certificates.zip"
    zip_path = settings.OUTPUT_DIR / zip_filename

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for recipient in recipients:
            if recipient.status == RecipientStatus.SUCCESS and recipient.file_path:
                cert_path = Path(recipient.file_path)
                if cert_path.exists():
                    arcname = recipient.file_name or cert_path.name
                    zip_file.write(cert_path, arcname=arcname)

    return zip_path
