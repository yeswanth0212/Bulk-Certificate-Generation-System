def test_download_individual_certificate(client):
    payload = {
        "title": "Cybersecurity Fundamentals",
        "issuer": "Security Institute",
        "recipients": [{"name": "Frank Castle", "email": "frank@example.com"}]
    }
    create_resp = client.post("/api/v1/jobs?sync=true", json=payload)
    cert_id = create_resp.json()["recipients"][0]["id"]

    dl_resp = client.get(f"/api/v1/certificates/{cert_id}/download")
    assert dl_resp.status_code == 200
    assert dl_resp.headers["content-type"] in ["application/pdf", "image/png"]
    assert len(dl_resp.content) > 0

def test_verify_certificate_valid_and_invalid(client):
    # 1. Create valid certificate
    payload = {
        "title": "Quantum Computing",
        "issuer": "Physics Org",
        "recipients": [{"name": "Grace Hopper", "email": "grace@example.com"}]
    }
    create_resp = client.post("/api/v1/jobs?sync=true", json=payload)
    cert_id = create_resp.json()["recipients"][0]["id"]

    # 2. Verify valid certificate
    verify_resp = client.get(f"/api/v1/certificates/{cert_id}/verify")
    assert verify_resp.status_code == 200
    v_data = verify_resp.json()
    assert v_data["valid"] is True
    assert v_data["recipient_name"] == "Grace Hopper"
    assert v_data["title"] == "Quantum Computing"
    assert "OFFICIAL CERTIFICATE VERIFIED" in v_data["verification_message"]

    # 3. Verify non-existent certificate
    fake_id = "00000000-0000-0000-0000-000000000000"
    fake_resp = client.get(f"/api/v1/certificates/{fake_id}/verify")
    assert fake_resp.status_code == 200
    f_data = fake_resp.json()
    assert f_data["valid"] is False
    assert "INVALID OR UNISSUED" in f_data["verification_message"]
