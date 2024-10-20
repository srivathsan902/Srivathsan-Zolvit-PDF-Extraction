def pipeline(invoice_path, out_path):
    """
    Pipeline to extract text from a file and tabulate it.
    """
    # Extract text from the file:
    filetype = invoice_path.split(".")[-1]
    text = ""
    if filetype == "txt":
        with open(invoice_path, "r") as file:
            text = file.read()
    
    elif filetype == "pdf":
        from pdf2text import extract_pdfplumber, extract_fitz
        text = extract_fitz(invoice_path)

    elif filetype == "jpg" or filetype == "png":
        raise NotImplementedError("Image processing not implemented yet")
    
    else:
        raise ValueError("Unsupported file type")
    
    # Tabulate the text:
    try:
        from text2table import tabulate_text
        tabulate_text(text, out_path)
    except Exception as e:
        print(f"Tabulation failed for {invoice_path}")
        print(e)
    



if __name__ == '__main__':
    out_path = "outputs"
    # Process all pdfs in the Jan to Mar directory
    import os
    pdf_dir = "Jan to Mar"
    for file in os.listdir(pdf_dir):
        try:
            invoice_path = os.path.join(pdf_dir, file)
            pipeline(invoice_path, out_path)
        except Exception as e:
            print(e)
            print(f"Failed for {file}")
    
    
