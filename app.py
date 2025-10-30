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
            
            # 2️⃣ Fallback: if no currency symbols found, look for numeric prices
            if not currency_matches:
                # Look for patterns that might be prices
                all_prices = re.findall(r"\b(\d+[.,]\d{2})\b", text)
                for p in all_prices:
                    value = float(p.replace(',', '.'))
                    
                    # Parse the parts
                    parts = p.replace(',', '.').split('.')
                    whole_part = int(parts[0])
                    decimal_part = int(parts[1])
                    
                    # Skip if it looks like a date (valid day/month combinations)
                    # Common date patterns: DD.MM (01.01 to 31.12) or MM.DD
                    is_likely_date = (
                        (1 <= whole_part <= 31 and 1 <= decimal_part <= 12) or  # DD.MM
                        (1 <= whole_part <= 12 and 1 <= decimal_part <= 31)     # MM.DD
                    ) and whole_part <= 31 and decimal_part <= 59  # extra date check
                    
                    # Skip dates, but keep valid prices (like 25.00)
                    # The key insight: prices often have .00, .50, .99 endings
                    # Dates rarely have these endings
                    has_price_ending = decimal_part in [0, 50, 99] or str(decimal_part).endswith('0')
                    
                    if is_likely_date and not has_price_ending:
                        continue
                    
                    # Filter by reasonable price range
                    if 0.50 <= value <= 500:
                        all_detected_prices.append(value)
        
        # Add all detected prices from this file
        if all_detected_prices:
            detected_prices.extend(all_detected_prices)
            total += sum(all_detected_prices)
        else:
            detected_prices.append("Not found")
    
    # 🧮 Display results
    st.subheader("🧾 Results")
    ticket_num = 1
    for price in detected_prices:
        if isinstance(price, float):
            st.write(f"**Ticket {ticket_num}:** €{price:.2f}")
            ticket_num += 1
        else:
            st.write(f"**File:** ❌ Price not detected")
    
    st.markdown("---")
    st.write(f"**Total amount:** €{total:.2f}")
    st.write(f"**Number of tickets found:** {len([p for p in detected_prices if isinstance(p, float)])}")
else:
    st.info("⬆️ Please upload one or more transport tickets to begin.")
