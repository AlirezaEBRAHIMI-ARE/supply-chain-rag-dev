from fastapi.testclient import TestClient
# TestClient lets us send fake requests to our FastAPI app directly in code,
# without needing a real running server — useful for automated testing.

from app_supply import app
# Import the actual FastAPI app object from your app_supply.py file

client = TestClient(app)
# Create a test client wired to your app

def test_track_exsiting_shipment ():
    response = cleint,get("/track/SHIP123")
    assert response.status_code == 200
    # assert = "this must be true, or the test fails"
    # status_code 200 means "request succeeded" in HTTP

def test_track_missing_shipment():
    response = client.get ("/track/DOES_NOT_EXIST")
    assert response.status_code==400
    # confirms your error handling (HTTPException) actually works correctly
