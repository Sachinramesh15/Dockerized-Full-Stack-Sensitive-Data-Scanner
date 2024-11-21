
// Handle file upload as before (no changes needed here)
document.getElementById("upload-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent the form from submitting the default way
    
    const fileInput = document.getElementById("file-upload");
    const file = fileInput.files[0]; // Get the first file selected

    if (!file) {
        // Handle the case where no file is selected
        document.getElementById("upload-message").innerText = "No file selected!";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:8000/upload/", {
            method: "POST",
            body: formData,
            headers: {
                "Accept": "application/json",
            },
            mode: "cors", // Explicitly set to "cors" to ensure CORS is enabled
        });

        if (!response.ok) {
            // Handle server errors (like 400 or 500)
            throw new Error("Failed to upload file. Server error.");
        }

        const data = await response.json();
        console.log("Success:", data);
        document.getElementById("upload-message").innerText = data.message; // Display the success message
    } catch (error) {
        console.error("Error:", error);
        document.getElementById("upload-message").innerText = "Failed to upload file. Please try again."; // Display error message
    }
});

// Function to handle fetching scan data
document.getElementById("fetch-scan-form").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent the form from submitting the default way

    const scanIdInput = document.getElementById("scan-id");
    const dataTypeInput = document.getElementById("data-type");

    const scanId = scanIdInput.value;
    const dataType = dataTypeInput.value;

    if (!scanId || !dataType) {
        document.getElementById("scan-results").innerText = "Please provide both Scan ID and Data Type.";
        return;
    }

    try {
        // Make the API call to fetch scan data
        const response = await fetch(`http://127.0.0.1:8000/scans/?scan_id=${scanId}&data_type=${dataType}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            mode: "cors",
        });

        if (!response.ok) {
            throw new Error("Failed to fetch scan data.");
        }

        const scanData = await response.json();
        
        // Display the scan data
        const scanResultsContainer = document.getElementById("scan-results");
        scanResultsContainer.innerHTML = ""; // Clear previous results

        if (scanData.length === 0) {
            scanResultsContainer.innerText = "No sensitive data found for the given Scan ID and Data Type.";
        } else {
            const table = document.createElement("table");
            const tableHeader = document.createElement("thead");
            const headerRow = document.createElement("tr");

            const dataCell = document.createElement("th");
            dataCell.innerText = "Sensitive Data";
            headerRow.appendChild(dataCell);

            const fieldTypeCell = document.createElement("th");
            fieldTypeCell.innerText = "Field Type";
            headerRow.appendChild(fieldTypeCell);

            tableHeader.appendChild(headerRow);
            table.appendChild(tableHeader);

            const tableBody = document.createElement("tbody");
            scanData.forEach(item => {
                const row = document.createElement("tr");
                const dataCell = document.createElement("td");
                dataCell.innerText = item.data;
                row.appendChild(dataCell);

                const fieldTypeCell = document.createElement("td");
                fieldTypeCell.innerText = item.field_type;
                row.appendChild(fieldTypeCell);

                tableBody.appendChild(row);
            });

            table.appendChild(tableBody);
            scanResultsContainer.appendChild(table);
        }

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("scan-results").innerText = "Failed to fetch scan data. Please try again."; // Display error message
    }
});

// Handle the delete scan functionality
document.getElementById("delete-scan-form").addEventListener("submit", async function(event) {
    event.preventDefault();
    
    const scanIdInput = document.getElementById("delete-scan-id");
    const scanId = scanIdInput.value;

    if (!scanId) {
        document.getElementById("delete-message").innerText = "Please provide a valid scan ID.";
        return;
    }

    try {
        const response = await fetch(`http://127.0.0.1:8000/scans/${scanId}`, {
            method: "DELETE",
            headers: {
                "Accept": "application/json",
            },
            mode: "cors",
        });

        if (!response.ok) {
            throw new Error("Failed to delete scan. Server error.");
        }

        const data = await response.json();
        document.getElementById("delete-message").innerText = data.message;
    } catch (error) {
        document.getElementById("delete-message").innerText = "Failed to delete scan. Please try again.";
    }
});