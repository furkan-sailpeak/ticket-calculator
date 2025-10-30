import re
from PIL import Image
import pytesseract
import streamlit as st
from pdf2image import convert_from_bytes

st.set_page_config(page_title="Ticket Total Calculator", page_icon="🧾")
st.title("🧾 Transport Ticket Total Calculator")
st.write("Upload your transport tickets (images or PDFs). The app will detect the main price on each ticket and give you the total.")

uploaded_files = st.file_uploader(
    "Upload your tickets",
    type=["jpg", "jpeg", "png", "pdf"],
    accept_multiple_files=True
)

if uploaded_files:
    total = 0.0
    detected_prices = []
    
    for file in uploaded_files:
        # Convert PDFs to images if needed
        if file.type == "application/pdf":
            images = convert_from_bytes(file.read())
        else:
            images = [Image.open(file)]
        
        # Collect all prices from all pages/images in this file
        all_detected_prices = []
        
        for img in images:
            text = pytesseract.image_to_string(img)
            
            # 1️⃣ Priority: find prices next to € or EUR (most reliable)
            currency_matches = re.findall(r"(?:€\s?|EUR\s?)[*\s]*(\d+[.,]\d{2})", text, re.IGNORECASE)
            for match in currency_matches:
                price = float(match.replace(',', '.'))
                if 0.50 <= price <= 500:  # reasonable range
                    all_detected_prices.append(price)
            
            # 2️⃣ Fallback