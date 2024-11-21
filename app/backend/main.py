from fastapi import FastAPI, UploadFile, File, HTTPException, Query, status
from contextlib import asynccontextmanager
from database import create_tables, insert_scan, insert_sensitive_data, fetch_scans, delete_scan, fetch_sensitive_data_by_type
from parser import parse_content
from models import UploadResponse, DataTypeRequest
from fastapi.middleware.cors import CORSMiddleware


# Add the CORS middleware


# Setup the lifespan function for the app
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Database tables created or verified.")
    yield
    print("Application shutting down.")

# Set the lifespan
app = FastAPI(lifespan=lifespan)

origins = [
    "http://127.0.0.1:5500",  # Allow the frontend app running on this URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.post("/upload/", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    scan_id = insert_scan(file.filename)
    content = (await file.read()).decode("utf-8")
    results = parse_content(content)    
    for category, data_list in results.items():
        for data, field_type in data_list:
            insert_sensitive_data(scan_id, data, field_type, category)
    message = f"'{file.filename}' has been uploaded and the data has been parsed with the scan ID {scan_id}."
    return UploadResponse(message=message, scan_id=scan_id)


@app.post("/scans/", response_model=list[dict])
def list_scans(scan_id: int = Query(..., description="ID of the scan to fetch data for"), data_type: str = Query(..., description="Type of data to fetch")):
    if data_type.lower() not in ["pii", "pci", "phi"]:
        raise HTTPException(status_code=400, detail="Invalid data type. Must be 'PII', 'PCI', or 'PHI'.")

    # Fetch the scan data based on the scan_id and data_type
    sensitive_data = fetch_sensitive_data_by_type(scan_id, data_type)
    if not sensitive_data:
        raise HTTPException(status_code=404, detail="No data found for the given scan ID and data type.")

    return [{"data": data[0], "field_type": data[1]} for data in sensitive_data]


@app.delete("/scans/{scan_id}")
def remove_scan(scan_id: int):
    try:
        delete_scan(scan_id)
        return {"message": f"Scan with ID {scan_id} deleted successfully."}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)  
        )
