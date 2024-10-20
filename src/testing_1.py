import pdfplumber

def print_word_positions(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]
        
        # Extract words with positions (including x, y coordinates)
        words = first_page.extract_words()

        # Print the position and text for each word
        for word in words:
            print(f"Word: '{word['text']}', x0: {word['x0']}, x1: {word['x1']}, top: {word['top']}, bottom: {word['bottom']}")

# Example usage
pdf_path = 'src/2.pdf'  # Provide the actual path to your PDF file
print_word_positions(pdf_path)
