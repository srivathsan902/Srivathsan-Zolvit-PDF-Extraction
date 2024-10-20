import fitz  # PyMuPDF
from pdf2text import extract_fitz

def extract_text_from_rectangle(pdf_path, page_number, rect):
    """
    Extracts text from a specific rectangle in a PDF page.

    Args:
        pdf_path (str): Path to the PDF file.
        page_number (int): Page number to extract text from (0-indexed).
        rect (tuple): A tuple (x1, y1, x2, y2) defining the rectangle coordinates.
    
    Returns:
        str: Extracted text from the specified rectangle.
    """
    # Open the PDF
    doc = fitz.open(pdf_path)

    # Access the specific page
    page = doc.load_page(page_number)

    # Define the rectangle coordinates (x1, y1, x2, y2)
    rect_area = fitz.Rect(rect[0], rect[1], rect[2], rect[3])

    # Extract text from the specified rectangle
    text = page.get_text("text", clip=rect_area)

    # Close the document
    doc.close()

    return text

# Example usage
pdf_path = "src/2.pdf"  # Replace with your PDF file path
page_number = 0  # First page
rect = (0, 260, 225, 430)  # Define the rectangle (x1, y1, x2, y2)
rect = (0, 0, 1000, 1000)
extracted_text = extract_text_from_rectangle(pdf_path, page_number, rect)
# print(extracted_text)

text = extract_fitz(pdf_path)
print(text)