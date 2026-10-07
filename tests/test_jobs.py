from app.models import JobStatus

def test_create_generation_job_sync(client):
    payload = {
        "title": "Machine Learning Fundamentals",
        "issuer": "AI Research Lab",
        "issue_date": "October 2026",
        "format": "pdf",
        "recipients": [
            {"name": "Alice Smith", "email": "alice@example.com", "custom_text": "Top Scorer"},
            {"name": "Bob Jones", "email": "bob@example.com"}
        ]
    }

    response = client.post("/api/v1/jobs?sync=true", json=payload)
    assert response.status_code == 202
    data = response.json()

    assert data["title"] == "Machine Learning Fundamentals"
    assert data["issuer"] == "AI Research Lab"
    assert data["total_recipients"] == 2
    assert data["processed_count"] == 2
    assert data["success_count"] == 2
    assert data["failure_count"] == 0
    assert data["progress_percentage"] == 100.0
    assert data["status"] == JobStatus.COMPLETED
    assert len(data["recipients"]) == 2
    assert data["zip_download_url"] is not None

def test_get_job_status(client):
    # 1. Submit job
    payload = {
        "title": "Data Science 101",
        "issuer": "Tech Academy",
        "recipients": [{"name": "Charlie Brown", "email": "charlie@example.com"}]
    }
    create_resp = client.post("/api/v1/jobs?sync=true", json=payload)
    job_id = create_resp.json()["id"]

    # 2. Fetch job status
    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["id"] == job_id
    assert data["status"] == JobStatus.COMPLETED
    assert data["recipients"][0]["status"] == "SUCCESS"
    assert data["recipients"][0]["download_url"] is not None

def test_download_job_zip(client):
    payload = {
        "title": "Web Development Bootcamp",
        "issuer": "Code Academy",
        "recipients": [
            {"name": "David Miller", "email": "david@example.com"},
            {"name": "Emma Watson", "email": "emma@example.com"}
        ]
    }
    create_resp = client.post("/api/v1/jobs?sync=true", json=payload)
    job_id = create_resp.json()["id"]

    zip_resp = client.get(f"/api/v1/jobs/{job_id}/download-zip")
    assert zip_resp.status_code == 200
    assert zip_resp.headers["content-type"] == "application/zip"
    assert len(zip_resp.content) > 0
