import PyPDF2
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import fitz
import re
import pandas as pd

def extract_or_default(pattern, text, default="N/A"):
    match = re.search(pattern, text)
    return match.group(1) if match else default

def extract_comma_ignored_number(text, default="N/A"):
    match = re.search(r'\d{1,3}(?:,\d{3})*\.\d+', text)
    return float(match.group(0).replace(',', '')) if match else default

def extract_percentage(text):
    match = re.search(r'\((\d+)%\)', text)
    match = re.search(r'([-]?\d+)%', text)
    return int(match.group(1)) if match else None

# Helper function to clean up quantity text
def clean_quantity(text):
    match = re.search(r'(\d+)', text)
    return int(match.group(1)) if match else int(text)

# Helper function to process the item name spread across multiple elements
def extract_item_name(start_index, data):
    name = ''
    index = start_index
    # Keep appending name parts until a price is encountered (since prices are always numeric)
    while not re.match(r'\d+\.\d+', data[index]):
        name += data[index].strip() + ' '
        index += 1
    return name.strip(), index


# Helper function to extract customer purchase entries
def get_customer_purchase_entries(item_details, invoice_number):
    try:
        items = []
        
        i = 0
        data = item_details
        while i < len(data):
            item = {'Invoice Number': invoice_number}
            
            # Extract item number
            item['Item Number'] = int(data[i])
            i += 1

            # Extract item name (may span multiple elements)
            item['Item Name'], i = extract_item_name(i, data)

            # # Extract actual price, discounted price, quantity, taxable value, tax amount, and final price
            item['Discounted Price'] = float(data[i].replace(',', ''))
            i += 1


            # Initialize discounted price and percentage to None
            item['Actual Price'] = None
            item['Discount Percentage'] = None

            # Check if the next element is a valid discounted price
            if i < len(data):
                # Check if the current element can be a discounted price
                discounted_price_str = data[i]
                if invoice_number == 'INV-128':
                    print(data[i])
                if re.match(r'^\d+(\.\d+)? \(\-\d+%\)$', discounted_price_str):
                    item['Actual Price'] = float(extract_comma_ignored_number(discounted_price_str))
                    item['Discount Percentage'] = extract_percentage(discounted_price_str)  # Use the updated function
                    if item['Discount Percentage'] is None:
                        item['Discount Percentage'] = float(item['Discounted Price'] / item['Actual Price'] * 100, 2)
                        i += 1
                    i += 1

            else:
                i += 1  # Move ahead by 1 if no more data
            
            if item['Actual Price'] is None:
                item['Actual Price'] = item['Discounted Price']
                item['Discount Percentage'] = 0

            # Extract quantity
            item['Quantity'] = clean_quantity(data[i])
            i += 1

            # Extract taxable value
            item['Taxable Value'] = float(extract_comma_ignored_number(data[i]))
            i += 1

            # Extract tax amount and tax percentage
            item['Tax Amount'] = float(extract_comma_ignored_number(data[i]))
            item['Tax Percentage'] = extract_percentage(data[i])
            i += 1

            # Extract final price (after tax)
            item['Amount'] = float(extract_comma_ignored_number(data[i]))
            i += 1
            
            # Append the parsed item to the list
            items.append(item)
            # Create a DataFrame
        df = pd.DataFrame(items)

        return df

    except:
        return pd.DataFrame()
