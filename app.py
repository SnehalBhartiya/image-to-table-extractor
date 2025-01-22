import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import re
import io

def extract_table_from_image(image):
    """Extract tabular data from an image using OCR and regex."""
    # Perform OCR with Tesseract
    custom_config = r'--oem 3 --psm 6'  # PSM 6: Assume a single uniform block of text
    ocr_result = pytesseract.image_to_string(image, config=custom_config)

    # Process the OCR text for tabular data
    lines = ocr_result.split('\n')
    data = []

    # Use regex to match table rows with a specific pattern
    for line in lines:
        if line.strip():
            match = re.match(r'^(\d+)\s+(\d{4}-\d{2}-\d{2})\s+(.+?)\s+([-+]?\d+)\s+([-+]?\d+)$', line)
            if match:
                data.append(match.groups())

    # Convert to pandas DataFrame
    columns = ['TransactionID', 'Date', 'Description', 'Amount', 'Balance']
    df = pd.DataFrame(data, columns=columns)
    return df

# Streamlit app
st.title("Image to Table Extractor")
st.write("Upload an image containing tabular data, and this app will extract it into a table!")

# File upload
uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Open the uploaded image
    image = Image.open(uploaded_file)

    # Display the image
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Extract table from image
    with st.spinner("Extracting table from image..."):
        try:
            df = extract_table_from_image(image)

            if not df.empty:
                # Display the extracted table
                st.write("### Extracted Table")
                st.dataframe(df)

                # Download button for CSV
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue().encode('utf-8')

                st.download_button(
                    label="Download Table as CSV",
                    data=csv_data,
                    file_name="extracted_table.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No tabular data detected in the image.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
