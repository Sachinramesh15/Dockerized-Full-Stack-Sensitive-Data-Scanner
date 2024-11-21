from pydantic import BaseModel
from enum import Enum

class UploadResponse(BaseModel):
    message: str
    scan_id: int

class DataType(str, Enum):
    PII = "PII"
    PCI = "PCI"
    PHI = "PHI"

class DataTypeRequest(BaseModel):
    data_type: DataType
