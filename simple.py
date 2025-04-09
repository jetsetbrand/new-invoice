import fitz

try:
    doc = fitz.open("static/invoice_template.pdf")
    print("PDF loaded successfully")
except Exception as e:
    print("Error:", e)
