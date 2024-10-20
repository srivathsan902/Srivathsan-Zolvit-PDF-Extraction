from utils import *
def extract_fitz(pdf_path):
    with fitz.open(pdf_path) as pdf:
        text = ""
        for page in pdf:
            text += page.get_text()
        return text
def extract_pypdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
        return text
    
def extract_pdfplumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        return text
    
def extract_pytessaract(pdf_path):
    # Convert PDF pages to images
    pages = convert_from_path(pdf_path)
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

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


if __name__ == "__main__":
    pdf_path = "Jan to Mar/INV-117_Naman.pdf"
    text = extract_pdfplumber(pdf_path)
    # Save it to a text file
    with open("outputs/pdfplumber.txt", "w", encoding="utf-8") as file:
        file.write(text)


    