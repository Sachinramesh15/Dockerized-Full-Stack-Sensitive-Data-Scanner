import pytest
from unittest.mock import patch, MagicMock
from database import insert_scan,insert_sensitive_data,fetch_scans,delete_scan


@pytest.fixture
def mock_db_connection():
    """Mock the database connection."""
    with patch("database.get_db_connection") as mock:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock.return_value.__enter__.return_value = mock_conn
        yield mock, mock_conn, mock_cursor


def test_insert_scan(mock_db_connection):
    """Test the `insert_scan` function."""
    _, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = [1]

    result = insert_scan("test_file.txt")
    assert result == 1
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO scans (file_name) VALUES (%s) RETURNING id;", ("test_file.txt",)
    )


def test_insert_sensitive_data(mock_db_connection):
    """Test the `insert_sensitive_data` function."""
    _, mock_conn, mock_cursor = mock_db_connection
    
    with patch("database.encode_data", return_value="encoded_data") as mock_encode_data:
        insert_sensitive_data(1, "sensitive_data", "field_type", "pii")

        mock_encode_data.assert_called_once_with("sensitive_data")

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO pii (scan_id, data, field_type) VALUES (%s, %s, %s);",
            (1, "encoded_data", "field_type"),
        )


def test_fetch_scans(mock_db_connection):
    """Test the `fetch_scans` function."""
    _, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [(1, "test_file.txt", "2024-11-21")]

    result = fetch_scans()
    assert result == [(1, "test_file.txt", "2024-11-21")]
    mock_cursor.execute.assert_called_once_with("SELECT * FROM scans;")


def test_delete_scan_valid(mock_db_connection):
    """Test the `delete_scan` function for a valid scan ID."""
    _, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = [1]

    delete_scan(1)
    mock_cursor.execute.assert_any_call("SELECT id FROM scans WHERE id = %s;", (1,))
    mock_cursor.execute.assert_any_call("DELETE FROM scans WHERE id = %s;", (1,))


def test_delete_scan_invalid(mock_db_connection):
    """Test the `delete_scan` function for an invalid scan ID."""
    _, mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = None

    with pytest.raises(ValueError, match="Scan ID 1 does not exist in the database."):
        delete_scan(1)

    mock_cursor.execute.assert_called_once_with("SELECT id FROM scans WHERE id = %s;", (1,))
