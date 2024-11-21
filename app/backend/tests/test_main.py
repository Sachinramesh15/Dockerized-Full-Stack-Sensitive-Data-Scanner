import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app  

client = TestClient(app)


@pytest.fixture
def mock_insert_scan():
    """Mock the `insert_scan` function."""
    with patch("main.insert_scan") as mock:
        mock.return_value = 1  
        yield mock


@pytest.fixture
def mock_insert_sensitive_data():
    """Mock the `insert_sensitive_data` function."""
    with patch("main.insert_sensitive_data") as mock:
        yield mock


@pytest.fixture
def mock_fetch_sensitive_data_by_type():
    """Mock the `fetch_sensitive_data_by_type` function."""
    with patch("main.fetch_sensitive_data_by_type") as mock:
        yield mock


@pytest.fixture
def mock_delete_scan():
    """Mock the `delete_scan` function."""
    with patch("main.delete_scan") as mock:
        yield mock


def test_upload_file(mock_insert_scan, mock_insert_sensitive_data):
    """Test the `/upload/` endpoint."""
    file_content = "sample content for testing"
    mock_file = {"file": ("test_file.txt", file_content)}

    with patch("main.parse_content") as mock_parse_content:
        mock_parse_content.return_value = {
            "pii": [("data1", "type1"), ("data2", "type2")],
            "pci": [("data3", "type3")],
        }
        response = client.post("/upload/", files=mock_file)

    assert response.status_code == 200
    assert response.json() == {
        "message": "'test_file.txt' has been uploaded and the data has been parsed with the scan ID 1.",
        "scan_id": 1,
    }
    mock_insert_scan.assert_called_once_with("test_file.txt")
    mock_insert_sensitive_data.assert_any_call(1, "data1", "type1", "pii")
    mock_insert_sensitive_data.assert_any_call(1, "data2", "type2", "pii")
    mock_insert_sensitive_data.assert_any_call(1, "data3", "type3", "pci")


def test_list_scans_valid(mock_fetch_sensitive_data_by_type):
    """Test the `/scans/` endpoint with valid inputs."""
    mock_fetch_sensitive_data_by_type.return_value = [
        ("data1", "type1"),
        ("data2", "type2"),
    ]
    params = {"scan_id": 1, "data_type": "pii"}
    response = client.post("/scans/", params=params)

    assert response.status_code == 200
    assert response.json() == [
        {"data": "data1", "field_type": "type1"},
        {"data": "data2", "field_type": "type2"},
    ]
    mock_fetch_sensitive_data_by_type.assert_called_once_with(1, "pii")


def test_list_scans_invalid_data_type(mock_fetch_sensitive_data_by_type):
    """Test the `/scans/` endpoint with an invalid data type."""
    params = {"scan_id": 1, "data_type": "invalid"}
    response = client.post("/scans/", params=params)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid data type. Must be 'PII', 'PCI', or 'PHI'."
    }
    mock_fetch_sensitive_data_by_type.assert_not_called()


def test_list_scans_no_data_found(mock_fetch_sensitive_data_by_type):
    """Test the `/scans/` endpoint when no data is found."""
    mock_fetch_sensitive_data_by_type.return_value = []
    params = {"scan_id": 1, "data_type": "pii"}
    response = client.post("/scans/", params=params)

    assert response.status_code == 404
    assert response.json() == {
        "detail": "No data found for the given scan ID and data type."
    }
    mock_fetch_sensitive_data_by_type.assert_called_once_with(1, "pii")


def test_remove_scan_valid(mock_delete_scan):
    """Test the `/scans/{scan_id}` endpoint for valid scan deletion."""
    response = client.delete("/scans/1")

    assert response.status_code == 200
    assert response.json() == {"message": "Scan with ID 1 deleted successfully."}
    mock_delete_scan.assert_called_once_with(1)


def test_remove_scan_not_found(mock_delete_scan):
    """Test the `/scans/{scan_id}` endpoint when the scan does not exist."""
    mock_delete_scan.side_effect = ValueError("Scan ID 1 does not exist in the database.")
    response = client.delete("/scans/1")

    assert response.status_code == 404
    assert response.json() == {"detail": "Scan ID 1 does not exist in the database."}
    mock_delete_scan.assert_called_once_with(1)
