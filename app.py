from flask import Flask, render_template, request, send_file, redirect, url_for
import fitz  # PyMuPDF
import io
import os
import qrcode
from num2words import num2words
from datetime import datetime
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Template and logo paths
    template_path = 'static/invoice_template.pdf'
    logo_path = 'static/web_auto_logo.png'

    # Safety check
    if not os.path.exists(template_path):
        return "Invoice template not found!", 404

    doc = fitz.open(template_path)
    page = doc[0]

    # Form data
    name = request.form.get('name')
    address = request.form.get('address')
    bill_no = request.form.get('bill_no')
    bill_date = request.form.get('bill_date')
    gst = request.form.get('gst')
    v_no = request.form.get('v_no')

    remove_reflecting = request.form.get('remove_reflecting') or '0'
    denting = request.form.get('denting') or '0'
    painting = request.form.get('painting') or '0'

    try:
        total_amount = sum([
            float(remove_reflecting),
            float(denting),
            float(painting)
        ])
    except ValueError:
        total_amount = 0.0

    total_in_words = num2words(total_amount, lang='en_IN').upper() + " RUPEES ONLY"

    # Draw fixed fields
    page.insert_text((80, 158), name, fontsize=10)

    # Handle address wrapping
    addr_lines = [address[i:i+10] for i in range(0, len(address), 10)]
    for idx, line in enumerate(addr_lines[:2]):
        page.insert_text((80, 173 + (idx * 13)), line, fontsize=10)

    page.insert_text((400, 152), bill_no, fontsize=10)

    try:
        formatted_date = datetime.strptime(bill_date, "%Y-%m-%d").strftime("%d-%m-%Y")
    except Exception:
        formatted_date = bill_date
    page.insert_text((400, 182), formatted_date, fontsize=10)

    page.insert_text((110, 218), gst, fontsize=10)
    page.insert_text((420, 215), v_no, fontsize=10)

    # Items (dynamic)
    base_y = 265
    items = []
    for i in range(1, 51):  # Support up to 50 rows
        detail = request.form.get(f'detail{i}')
        hsn = request.form.get(f'hsn{i}')
        gst_rate = request.form.get(f'gst_rate{i}')
        qty = request.form.get(f'qty{i}')
        if detail or hsn or gst_rate or qty:
            items.append((str(i), detail, hsn, gst_rate, qty))

    for idx, item in enumerate(items):
        offset = base_y + (idx * 20)
        page.insert_text((35, offset), item[0], fontsize=10)  # Sr No
        if item[1]: page.insert_text((85, offset), item[1], fontsize=10)
        if item[2]: page.insert_text((260, offset), item[2], fontsize=10)
        if item[3]: page.insert_text((320, offset), item[3], fontsize=10)
        if item[4]: page.insert_text((360, offset), item[4], fontsize=10)

    # Additional fields
    page.insert_text((390, 265), remove_reflecting, fontsize=10)
    page.insert_text((450, 265), denting, fontsize=10)
    page.insert_text((500, 265), painting, fontsize=10)
    page.insert_text((550, 265), str(total_amount), fontsize=10)
    page.insert_text((550, 477), str(total_amount), fontsize=10)
    page.insert_text((150, 477), total_in_words, fontsize=10)

    # Add QR Code
    qr_data = f"Bill No: {bill_no}\nGST No: {gst}\nParty name : {name}"
    qr = qrcode.make(qr_data)
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)
    qr_pix = fitz.Pixmap(qr_io.read())
    qr_rect = fitz.Rect(300, 650, 360, 710)
    page.insert_image(qr_rect, pixmap=qr_pix)

    # Add Logo
   

    # Save preview
    output_path = 'static/preview_invoice.pdf'
    doc.save(output_path)

    return render_template('preview.html', pdf_url=url_for('static', filename='preview_invoice.pdf'))

if __name__ == '__main__':
    app.run(debug=True)
