def test_validation_empty_recipients(client):
    payload = {
        "title": "Cloud Computing",
        "issuer": "DevOps Inst",
        "recipients": []
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422  # Unprocessable Entity

def test_validation_blank_name(client):
    payload = {
        "title": "Cloud Computing",
        "issuer": "DevOps Inst",
        "recipients": [
            {"name": "   ", "email": "valid@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422

def test_validation_invalid_email(client):
    payload = {
        "title": "Cloud Computing",
        "issuer": "DevOps Inst",
        "recipients": [
            {"name": "John Doe", "email": "not-an-email"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422

def test_validation_invalid_format(client):
    payload = {
        "title": "Cloud Computing",
        "issuer": "DevOps Inst",
        "format": "exe",
        "recipients": [
            {"name": "John Doe", "email": "john@example.com"}
        ]
    }
    response = client.post("/api/v1/jobs", json=payload)
    assert response.status_code == 422
