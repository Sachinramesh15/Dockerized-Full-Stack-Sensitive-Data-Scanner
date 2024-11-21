import base64


def encode_data(data: str) -> str:
    """Encodes sensitive data before storing it."""
    encoded_data = base64.b64encode(data.encode("utf-8")).decode("utf-8")
    return encoded_data


def decode_data(data):
    """Decodes the data using base64."""
    return base64.b64decode(data).decode('utf-8')
