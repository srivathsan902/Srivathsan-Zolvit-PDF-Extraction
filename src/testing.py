import pdfplumber

def extract_data_using_positions(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        first_page = pdf.pages[0]

        # Extract detailed information with positions
        words = first_page.extract_words()

        name = ""
        phone_number = ""
        shipping_address = ""

        name_block = []
        shipping_block = []

        # Define x-coordinates and y-coordinate ranges
        name_x_threshold = 190  # Adjust based on the left side text for the Name section
        shipping_x_threshold = 200  # Adjust for the right side text (Shipping Address)

        # Define a y-coordinate range where we expect the name and shipping details to appear
        name_y_min = 150  # Set to a lower y-coordinate limit (based on visual layout)
        name_y_max = 300  # Upper y-coordinate limit for the "Name" and "Shipping Address"

        # Separate words based on their x and y coordinates
        for word in words:
            # Use both x and y thresholds to classify words into "Name" or "Shipping Address"
            if name_y_min < word['top'] < name_y_max:  # Only consider lines within the expected region
                if word['x0'] < name_x_threshold:  # Likely the "Name" section on the left
                    name_block.append(word['text'])
                elif word['x0'] > shipping_x_threshold:  # Likely the "Shipping Address" on the right
                    shipping_block.append(word['text'])

        # Combine the name block and shipping block into final strings
        name = ' '.join(name_block).split("Ph:")[0].strip()  # Clean up extra details after the name
        phone_number = next((word['text'] for word in words if "Ph:" in word['text']), "Phone number not found")
        shipping_address = ' '.join(shipping_block).strip()

        return name, phone_number, shipping_address


# Example usage
pdf_path = 'src/2.pdf'  # Provide the actual path to your PDF file
name, phone_number, shipping_address = extract_data_using_positions(pdf_path)
print(f"Name: {name}")
print(f"Phone Number: {phone_number}")
print(f"Shipping Address: {shipping_address}")
