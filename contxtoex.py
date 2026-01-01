import pandas as pd
import re
import streamlit as st

def extract_sales_data(file_content):
    lines = file_content.split("\n")
    shop_id, shop_name = None, None
    
    print("========== FILE CONTENT START ==========")
    print(file_content)
    print("========== FILE CONTENT END ==========")
    
    # Extract Shop ID and Name, handling different formats
    for line in lines:
        match = re.search(r"(\d{5,})[_\s-]+(.+)", line)  # Support underscores and dashes
        if match:
            shop_id, shop_name = match.groups()
            shop_name = shop_name.strip()  # Ensure no leading/trailing spaces
            print(f"✅ Extracted Shop ID: {shop_id}, Shop Name: {shop_name}")
            break
    
    sales_data = {
        "CARD": 0, "CASH": 0, "COD": 0, "CREDIT": 0, "MOBI KWIK": 0,"PAYBYLINK": 0,"GIFT VOUCHER": 0,
        "PAYTM CARD": 0, "PAYTM DQRC": 0, "QR CODE": 0, "RELIGARE": 0, "UPI": 0, "POS SALES": 0
    }
    
    def safe_extract(value):
        value = value.strip().replace(',', '')
        try:
            return float(value) if '.' in value else int(value)
        except ValueError:
            return 0
    
    # Extract Net Total values correctly from the right column
    for line in lines:
        for key in sales_data.keys():
            pattern = rf"^{key}\b"  # Ensures exact match at start of the line
            if re.search(pattern, line, re.IGNORECASE):  
                values = re.findall(r"[-+]?[0-9,]*\.?[0-9]+", line)
                print(f"🔍 DEBUG: {key} → Line: {line} → Extracted Numbers: {values}")
                
                if values and len(values) >= 3:  # Ensure Net Total column is present
                    sales_data[key] = safe_extract(values[-1])  # Extract last value (Net Total)
                    print(f"✅ {key} Net Total: {sales_data[key]}")
    
    # Extract POS SALES from the last column of TOTAL AMOUNT section
    for line in lines:
        if re.search(r"TOTAL[\s]*AMOUNT", line, re.IGNORECASE):
            values = re.findall(r"[-+]?[0-9,]*\.?[0-9]+", line)
            print(f"🔍 DEBUG: POS SALES → Line: {line} → Extracted Numbers: {values}")
            if values:
                sales_data["POS SALES"] = safe_extract(values[-1])  # Last value is POS SALES
                print(f"✅ POS SALES Net Total: {sales_data['POS SALES']}")
    
    print(f"✅ FINAL EXTRACTED DATA → Shop ID: {shop_id}, Shop Name: {shop_name}, Sales Data: {sales_data}")
    
    return shop_id, shop_name, sales_data

def convert_to_excel(data_list):
    if data_list:
        df = pd.DataFrame(data_list)
        df.to_excel("Sales_Report.xlsx", index=False)
        return "Sales_Report.xlsx", df
    return None, None

st.title("Text File to Excel Converter")
uploaded_files = st.file_uploader("Upload your text files", type=["txt"], accept_multiple_files=True)

data_list = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        file_content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        shop_id, shop_name, sales_data = extract_sales_data(file_content)
        if shop_id and shop_name:
            row_data = {"Shop id": shop_id, "Shop Name": shop_name, **sales_data}
            data_list.append(row_data)

    if data_list:
        output_file_path, df = convert_to_excel(data_list)
        st.write("### Extracted Data Preview")
        st.dataframe(df)
        
        st.success("Excel file generated successfully!")
        with open(output_file_path, "rb") as f:
            st.download_button("Download Excel File", f, file_name="Sales_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.error("Failed to process the files.")


