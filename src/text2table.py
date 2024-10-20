import os
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

            # # Extract discounted price (may contain discount percentage)
            # item['Actual Price'] = float(extract_comma_ignored_number(data[i]))
            # item['Discount Percentage'] = extract_percentage(data[i])
            # i += 1

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


def tabulate_text(text, out_folder):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    
   
    # Make structured data from text:
    
    lines = text.split("\n")
    phone_number = None
    place_of_supply = None
    address = None
    cgst = 0
    sgst = 0
    total_discount = 0
    for line in lines:
        if "Invoice #" in line:
            invoice_number = line.split(":")[1].strip()
        if "Invoice Date" in line:
            invoice_date = line.split(":")[1].strip()
        if "Due Date" in line:
            due_date = line.split(":")[1].strip()
        if "Customer Details" in line:  # Next line is Customer Name
            customer_name = lines[lines.index(line) + 1]
        if "Ph:" in line:   # Phone number
            phone_number = line.split(":")[1].strip()
        if "Place of Supply" in line:   # Next line if the place of supply
            place_of_supply = lines[lines.index(line) + 1]
        if "Shipping Address" in line or "Billing Address" in line:  # Next few lines are the address, until the next section begins with Place of Supply
            address = ""
            for next_line in lines[lines.index(line) + 1:]:
                if next_line.startswith("Place of Supply"):
                    break
                address += next_line + " "
        # Check if the line contains just the word Total and not multiple words
        if  "Total" in line and len(line.split()) == 1:
            total_amount = float(lines[lines.index(line) + 1].replace(',', '').split("₹")[1])
        if "Total Discount" in line:    # Next line is the total discount
            total_discount = float(lines[lines.index(line) + 1].replace(',', '').split("₹")[1])
            
        if "Taxable Amount" in line:    # Next line is the taxable amount
            taxable_amount = float(lines[lines.index(line) +1].replace(',', '').split("₹")[1])
            
        if "CGST" in line:  # Next line is the CGST
            cgst += float(lines[lines.index(line) + 1].replace(',', '').split("₹")[1])
            
        if "SGST" in line:  # Next line is the SGST
            sgst += float(lines[lines.index(line) + 1].replace(',', '').split("₹")[1])
            

    total_tax_amount = cgst + sgst
    
    # Extract Item Details:
    for line in lines:
        if "Tax Amount" in line and "Amount" in lines[lines.index(line) + 1]:
            start_index = lines.index(line) + 2
        
        if "Taxable Amount" in line:
            end_index = lines.index(line)
            break
    
    item_details = lines[start_index:end_index]

    customer_purchase_entries = get_customer_purchase_entries(item_details, invoice_number)

    if os.path.exists(f'{out_folder}/purchase_items.csv'):
        customer_purchase_entries.to_csv(f'{out_folder}/purchase_items.csv', mode='a', header=False, index=False)
    else:
        customer_purchase_entries.to_csv(f'{out_folder}/purchase_items.csv', index=False)


    
    df = {
        "Invoice Number": [invoice_number],
        "Invoice Date": [invoice_date],
        "Invoice Due Date": [due_date],
        "Customer Name": [customer_name],
        "Phone": [phone_number],
        "Place of Supply": [place_of_supply],
        "Address": [address],
        "Taxable Amount": [taxable_amount],
        "Tax Amount": [total_tax_amount],
        "Total Amount": [total_amount],
        "Total Discount": [total_discount]
    }
    df = pd.DataFrame(df)


    if os.path.exists(f'outputs/invoice.csv'):
        df.to_csv(f'outputs/invoice.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('outputs/invoice.csv', header=True, index=False)

if __name__ == "__main__":

    out_folder = "outputs"
    pdf_path = "src/2.pdf"
    from pdf2text import extract_fitz
    text = extract_fitz(pdf_path)
    tabulate_text(text, out_folder)

    