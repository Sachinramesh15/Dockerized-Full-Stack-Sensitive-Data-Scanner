import re

REGEX_PATTERNS = {
    "PAN": r"[A-Z]{5}[0-9]{4}[A-Z]",
    "SSN": r"\d{3}-\d{2}-\d{4}",
    "Credit Card": r"\b(?:\d[ -]*?){13,16}\b",
    "Medical Record Number": r"\bMRN-\d{6,10}\b",
    "Insurance ID": r"\b(?:INS|HID)-\d{6,10}\b",
    "Test Results": r"\b(?:Positive|Negative|[\d.]+ (mg|mmol|IU))\b"
}
def parse_content(content):
    results = {"pii": [], "pci": [], "phi": []}

    for field_type, pattern in REGEX_PATTERNS.items():
        matches = re.findall(pattern, content)
        if field_type in ["PAN", "SSN"]:
            category = "pii"
        elif field_type in ["Credit Card"]:
            category = "pci"
        else:
            category = "phi"

        for match in matches:
            results[category].append((match, field_type))

    PHI_KEYWORDS = ["Medical Record", "Test Result", "Health Insurance"]
    for line in content.splitlines():
        if any(keyword in line for keyword in PHI_KEYWORDS):
            results["phi"].append((line, "Keyword-based PHI"))

    return results
