from flask import Flask, render_template, request, send_file, redirect, url_for
import fitz  # PyMuPDF
import io
import os
import qrcode

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return redirect('/')

    # Load the template PDF
    template_path = 'static/invoice_template.pdf'
    doc = fitz.open(template_path)
    page = doc[0]

    # Get form data
    name = request.form.get('name')
    address = request.form.get('address')
    bill_no = request.form.get('bill_no')
    bill_date = request.form.get('bill_date')
    gst = request.form.get('gst')
    v_no = request.form.get('v_no')

    items = []
    for i in range(1, 11):
        sr = request.form.get(f'sr{i}')
        detail = request.form.get(f'detail{i}')
        hsn = request.form.get(f'hsn{i}')
        gst_rate = request.form.get(f'gst_rate{i}')
        qty = request.form.get(f'qty{i}')
        if sr or detail or hsn or gst_rate or qty:
            items.append((sr, detail, hsn, gst_rate, qty))

    # Draw fixed fields
    page.insert_text((80, 160), name, fontsize=10)

    # Handle address wrapping
    addr_lines = [address[i:i+10] for i in range(0, len(address), 10)]
    for idx, line in enumerate(addr_lines[:2]):
        page.insert_text((80, 175 + (idx * 10)), line, fontsize=10)

    page.insert_text((400, 165), bill_no, fontsize=10)
    page.insert_text((400, 185), bill_date, fontsize=10)
    page.insert_text((110, 216), gst, fontsize=10)
    page.insert_text((420, 215), v_no, fontsize=10)

    # Draw items
    base_y = 265
    for idx, item in enumerate(items):
        offset = base_y + (idx * 20)
        if item[0]: page.insert_text((35, offset), item[0], fontsize=10)
        if item[1]: page.insert_text((85, offset), item[1], fontsize=10)
        if item[2]: page.insert_text((260, offset), item[2], fontsize=10)
        if item[3]: page.insert_text((320, offset), item[3], fontsize=10)
        if item[4]: page.insert_text((360, offset), item[4], fontsize=10)

    # Generate QR code with bill number and GST
    qr_data = f"Bill No: {bill_no}\nGST No: {gst}"
    qr = qrcode.make(qr_data)
    qr_io = io.BytesIO()
    qr.save(qr_io, format='PNG')
    qr_io.seek(0)

    # Insert QR into PDF at (300, 700)
    qr_image = fitz.Pixmap(qr_io.read())
    rect = fitz.Rect(300, 650, 360, 700)  # Width/Height = 60x60
    page.insert_image(rect, pixmap=qr_image)

    # Save the PDF to a static preview file
    preview_path = os.path.join('static', 'preview_invoice.pdf')
    doc.save(preview_path)

    return render_template('preview.html', pdf_url=url_for('static', filename='preview_invoice.pdf'))

if __name__ == '__main__':
    app.run(debug=True)
