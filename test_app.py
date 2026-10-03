from fastapi.testclient import TestClient
from app_supply import app
from tracking import insert_shipment, get_shipment

client = TestClient(app)

# Only insert SHIP123 if it doesn't already exist in the database —
# this way the test works whether the database is empty (like on
# GitHub) or already has this shipment (like on your own machine)
if get_shipment("SHIP123") is None:
    insert_shipment("SHIP123", "Paris", "Berlin")

def test_track_existing_shipment():
    response = client.get("/track/SHIP123")
    assert response.status_code == 200

def test_track_missing_shipment():
    response = client.get("/track/DOES_NOT_EXIST")
    assert response.status_code == 404