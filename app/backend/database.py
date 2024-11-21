import psycopg2, os
from contextlib import contextmanager
from dotenv import load_dotenv
from security import encode_data, decode_data
load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

@contextmanager
def get_db_connection():
    """Context manager to connect to the PostgreSQL database using psycopg2."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def create_tables():
    """Creates the necessary tables for the application."""
    queries = [
        """
        CREATE TABLE IF NOT EXISTS scans (
            id SERIAL PRIMARY KEY,
            file_name TEXT NOT NULL,
            uploaded_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS pii (
            id SERIAL PRIMARY KEY,
            scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
            data TEXT NOT NULL,
            field_type TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS pci (
            id SERIAL PRIMARY KEY,
            scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
            data TEXT NOT NULL,
            field_type TEXT NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS phi (
            id SERIAL PRIMARY KEY,
            scan_id INTEGER REFERENCES scans(id) ON DELETE CASCADE,
            data TEXT NOT NULL,
            field_type TEXT NOT NULL
        );
        """
    ]
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for query in queries:
                cursor.execute(query)


def insert_scan(file_name):
    """Inserts a scan record into the scans table."""
    query = "INSERT INTO scans (file_name) VALUES (%s) RETURNING id;"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (file_name,))
            return cursor.fetchone()[0]


def insert_sensitive_data(scan_id, data, field_type, category):
    """Inserts sensitive data into the appropriate table after encoding it."""
    table_map = {"pii": "pii", "pci": "pci", "phi": "phi"}
    table_name = table_map[category]
    encoded_data = encode_data(data)
    query = f"INSERT INTO {table_name} (scan_id, data, field_type) VALUES (%s, %s, %s);"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (scan_id, encoded_data, field_type))


def fetch_scans():
    """Fetches all scan records from the scans table."""
    query = "SELECT * FROM scans;"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()


def delete_scan(scan_id):
    """Deletes a scan record and associated data by scan ID."""
    check_query = "SELECT id FROM scans WHERE id = %s;"
    delete_query = "DELETE FROM scans WHERE id = %s;"

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(check_query, (scan_id,))
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"Scan ID {scan_id} does not exist in the database.")
            
            cursor.execute(delete_query, (scan_id,))


def fetch_sensitive_data_by_type(scan_id, data_type):
    """Fetch sensitive data for a given scan ID and data type, decoding it."""
    table_map = {"pii": "pii", "pci": "pci", "phi": "phi"}
    table_name = table_map[data_type]

    query = f"SELECT data, field_type FROM {table_name} WHERE scan_id = %s;"
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (scan_id,))
            results = cursor.fetchall()
            
            # Decode the data before returning
            decoded_results = []
            for data, field_type in results:
                decoded_data = decode_data(data)  # Decode the data here
                decoded_results.append((decoded_data, field_type))
                
            return decoded_results