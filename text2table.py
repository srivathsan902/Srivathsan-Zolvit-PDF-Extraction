import os
import re
import pandas as pd
from pdf2text import extract_text_from_rectangle

def tabulate_text(pdf_path, text, out_folder):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    
    # Make the framework of csv if it doesn't exist
    csv_path = os.path.join(out_folder, "invoice.csv")
    if not os.path.exists(csv_path):
        # Columns are: Invoice Number, Invoice Date, Invoice Due Date, Customer Name, Customer Address, Taxable Amount, Tax Amount, Total Amount, Total Discount.
        
        df = pd.DataFrame(columns=["Invoice Number", "Invoice Date", "Invoice Due Date", "Customer Name", "Mobile", "Place of Supply", "Address", "Taxable Amount", "Tax Amount", "Total Amount", "Total Discount"])

        df.to_csv(csv_path, index=False)

    # Make structured data from text:

    # Extract customer details
    customer_details_rect = (0, 150, 200, 250)  # Define the rectangle (x1, y1, x2, y2)
    extracted_text = extract_text_from_rectangle(pdf_path, 0, customer_details_rect)

    # Extract customer name (2nd line)
    customer_name = extracted_text.split("\n")[1]
    
    mobile_number = None
    place_of_supply = None
    address = None

    for line in extracted_text.split("\n"):
        if "Ph:" in line:
            mobile_number = line.split("Ph:")[1].strip()
        
        if "Place of Supply:" in line:
            # Next line is the address
            place_of_supply = extracted_text.split("\n")[extracted_text.split("\n").index(line) + 1]
    


    address_rect = (200, 150, 400, 200)  # Define the rectangle (x1, y1, x2, y2)
    extracted_text = extract_text_from_rectangle(pdf_path, 0, address_rect)

    if extracted_text:
        address = extracted_text.strip()


    # Define regex patterns for extraction
    invoice_number_pattern = r"Invoice #:\s*(\S+)"
    invoice_date_pattern = r"Invoice Date:\s*([\dA-Za-z\s]+?)\s*Due Date:"
    due_date_pattern = r"Due Date:\s*([\dA-Za-z\s]+?)\s*Customer Details:"
    
    taxable_amount_pattern = r"Taxable Amount ₹([\d,\.]+)"
    tax_amount_pattern = r"(CGST \d+\.\d+% ₹([\d,\.]+))|((SGST \d+\.\d+% ₹([\d,\.]+)))"

    total_amount_pattern = r"Total ₹([\d,\.]+)"
    total_discount_pattern = r"Total Discount ₹([\d,\.]+)"

    invoice_number = re.search(invoice_number_pattern, text).group(1)
    invoice_date = re.search(invoice_date_pattern, text).group(1)
    due_date = re.search(due_date_pattern, text).group(1)

    taxable_amount = re.search(taxable_amount_pattern, text).group(1)
    tax_amount_matches = re.findall(tax_amount_pattern, text)
    cgst_amounts = []
    sgst_amounts = []

    # Process each match
    for match in tax_amount_matches:
        if match[1]:  # Check if it's a CGST match
            cgst_amounts.append(float(match[1]))
        if match[4]:  # Check if it's an SGST match
            sgst_amounts.append(float(match[4]))

    # Calculate total tax amount
    total_tax_amount = sum(cgst_amounts) + sum(sgst_amounts)
    total_amount = re.search(total_amount_pattern, text).group(1)
    total_discount = re.search(total_discount_pattern, text).group(1)

    # Append to the csv
    df = pd.read_csv(csv_path)
    new_data = {
        "Invoice Number": [invoice_number],
        "Invoice Date": [invoice_date],
        "Invoice Due Date": [due_date],
        "Customer Name": [customer_name],
        "Mobile": [mobile_number],
        "Place of Supply": [place_of_supply],
        "Address": [address],
        "Taxable Amount": [taxable_amount],
        "Tax Amount": [total_tax_amount],
        "Total Amount": [total_amount],
        "Total Discount": [total_discount]
    }
    new_df = pd.DataFrame(new_data)
    df = pd.concat([df, new_df], ignore_index=True)

    df.to_csv(csv_path, index=False)

if __name__ == "__main__":
    text = """
TAX INVOICE ORIGINAL FOR RECIPIENT
UNCUE DERMACARE PRIVATE LIMITED
GSTIN 23AADCU2395N1ZY
C/o KARUNA GUPTA KURELE, 1st Floor
S.P Bungalow Ke Pichhe, Shoagpur Shahdol, Shahdol
Shahdol, MADHYA PRADESH, 484001
Mobile +91 8585960963 Email ruhi@dermaq.in
Invoice #: INV-117 Invoice Date: 01 Feb 2024 Due Date: 29 Jan 2024
Customer Details:
Naman
Place of Supply:
23-MADHYA PRADESH
# Item Rate / Item Qty Taxable Value Tax Amount Amount
492.86
1 Kera M 5% Solution 1 BTL 492.86 59.14 (12%) 552.00
616.07 (-20%)
299.58
2 Arachitol Nano (60k) 4*5ml 3 BTL 898.73 107.85 (12%) 1,006.58
340.43 (-12%)
30.58
3 Neurobion Forte - 30 tablets 3 STRP 91.73 16.51 (18%) 108.24
34.75 (-12%)
Taxable Amount ₹1,483.32
CGST 6.0% ₹83.50
SGST 6.0% ₹83.50
CGST 9.0% ₹8.26
SGST 9.0% ₹8.26
Round Off 0.18
Total ₹1,667.00
Total Discount ₹290.02
Total Items / Qty : 3 / 7.000 Total amount (in words): INR One Thousand, Six Hundred And Sixty-Seven Rupees Only.
Amount Paid
Pay using UPI: Bank Details:
For UNCUE DERMACARE PRIVATE LIMITED
Bank: Kotak Mahindra Bank
Account #: 1146860541
IFSC Code: kkbk0000725
Branch: PUNE - CHINCHWAD
Authorized Signatory
UnCue Dermacare Pvt Ltd
Powered By
Swipe | Simple Invoicing, Billing and Payments | Visit getswipe.in
Page 1 / 1 This is a computer generated document and requires no signature."""

    out_folder = "outputs"
    pdf_path = "src/2.pdf"
    tabulate_text(pdf_path, text, out_folder)

    