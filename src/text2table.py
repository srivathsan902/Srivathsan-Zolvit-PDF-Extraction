import os
import re
import pandas as pd

from utils import extract_comma_ignored_number, extract_percentage, clean_quantity, extract_item_name, get_customer_purchase_entries


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
    pdf_path = "Jan to Mar/INV-117_Naman.pdf"
    from pdf2text import extract_fitz
    text = extract_fitz(pdf_path)
    tabulate_text(text, out_folder)

    