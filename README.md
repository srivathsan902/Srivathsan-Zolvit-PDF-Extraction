# Invoice Processing Pipeline

This project implements a pipeline to extract structured information from invoices in various formats (PDF, TXT, and image files) and tabulate the extracted data into CSV files for further analysis.

## Features

- Extract text from PDF invoices using multiple libraries: `PyMuPDF` (fitz), `PyPDF2`, `pdfplumber`, and `pytesseract`.
- Handle various invoice layouts and extract key details like invoice number, date, customer information, item details, and financials.
- Output the structured data in CSV format for easy integration with data analysis tools.

## Requirements
Clone the repository in your local machine.

To run this project, ensure you have the following dependencies installed:

- `pandas`
- `PyMuPDF` (fitz)
- `PyPDF2`
- `pdfplumber`
- `pytesseract`
- `pdf2image` (if using image processing)

You can install the required packages using pip:

```bash
pip install -r requirements.txt
```

# Usage

To process invoices:

1. Place your PDF invoices in the designated directory (Jan to Mar) currently.
2. Configure the file paths in the pipeline script.
3. Run the script:

    ```bash
    python src/pipeline.py
    ```

4. The output will include structured data saved in CSV format.

## Code Structure

- `utils.py`: Contains utility functions for text extraction and data processing.
- `main.py`: Main script that drives the data extraction pipeline.
- `outputs/`: Directory where output files are stored.
- `invoice_samples/`: Directory containing sample PDF invoices for testing.


# Contributions
Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.
