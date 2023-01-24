from flask import Flask, render_template, send_from_directory, request, redirect, session
import io
import PyPDF2
from reportlab.pdfgen import canvas
from flask_session import Session

app = Flask(__name__, static_folder='static')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    if 'pesan' in session:
        pesan = session['pesan']
        session.pop('pesan', None)
    else:
        pesan = None
    return render_template('index.html', pesan=pesan)

@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)

@app.route('/encrypt', methods=['POST'])
def encrypt():
    # Baca file pdf, pesan, dan kunci yang diterima dari form input
    pdf_file = request.files.get('file_pdf').read()
    pesan = request.form.get('pesan')
    kunci = request.form.get('kunci')

    # Enkripsi pesan yang ingin disimpan dengan menggunakan kunci enkripsi yang telah ditentukan
    pesan_enkripsi = ""
    for i, c in enumerate(pesan):
        pesan_enkripsi += chr(ord(c) ^ ord(kunci[i % len(kunci)]))

    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
    pdf_writer = PyPDF2.PdfWriter()

    # Iterasi setiap halaman dalam file PDF
    for halaman in range(len(pdf_reader.pages)):
        # Baca halaman yang sedang diterjemahkan
        teks = pdf_reader.pages[halaman].extract_text()
        halaman_pdf = pdf_reader.pages[halaman]

        # Geser baris-baris yang merupakan baris genap atau ganjil sesuai dengan kunci enkripsi yang telah ditentukan
        baris_baru = ""
        for i, baris in enumerate(teks.splitlines()):
            if i % 2 == 0:
                baris_baru += pesan_enkripsi + "\n"
            else:
                baris_baru += baris + "\n"

        # Buat file PDF baru yang memiliki header %PDF-
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer)
        c.drawString(0, 0, baris_baru)
        c.save()

        # Baca file PDF baru yang telah dibuat sebagai halaman baru
        halaman_baru = PyPDF2.PdfReader(buffer).pages[0]
        #halaman_baru = halaman_pdf
        # Merge halaman baru yang telah disisipi pesan dengan halaman asli
        halaman_baru.merge_page(halaman_pdf)

        # Menambahkan watermark
        watermark_file = io.BytesIO()
        watermark = canvas.Canvas(watermark_file)
        watermark.setFont("Helvetica", 60)
        watermark.rotate(50)
        watermark.drawString(600, 200, "Watermark")  # add your watermark text here
        watermark.save()
        watermark_page = PyPDF2.PdfReader(watermark_file)
        halaman_baru.merge_page(watermark_page.pages[0])
        # Tambahkan halaman yang telah disisipi pesan ke dalam objek pdf_writer
        pdf_writer.add_page(halaman_baru)

    # Simpan perubahan yang telah dilakukan pada file PDF tersebut
    pdf_output = io.BytesIO()
    pdf_writer.write(pdf_output)
    pdf_output.seek(0)

    # Kirim file pdf hasil enkripsi ke browser
    response = app.make_response(pdf_output.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=hasil.pdf'
    return response


@app.route('/decrypt', methods=['POST'])
def decrypt():
    # Baca file pdf dan kunci yang diterima dari form input
    pdf_file = request.files.get('file_pdf').read()
    kunci = request.form.get('kunci')

    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_file))
    pdf_writer = PyPDF2.PdfWriter()

    # Dekripsi pesan yang disisipkan dengan menggunakan kunci enkripsi yang telah ditentukan
    pesan = ""

    # Iterasi setiap halaman dalam file PDF
    for halaman in range(len(pdf_reader.pages)):
        # Baca halaman yang sedang diterjemahkan
        teks = pdf_reader.pages[halaman].extract_text()
        halaman_pdf = pdf_reader.pages[halaman]

        # Geser baris-baris yang merupakan baris genap atau ganjil kembali ke posisi semula sesuai dengan kunci enkripsi yang telah ditentukan
        for i, baris in enumerate(teks.splitlines()):
            if i % 2 == 0:
                pesan += baris

    # Dekripsi pesan yang telah dibuka
    pesan_dekripsi = ""
    for i, c in enumerate(pesan):
        pesan_dekripsi += chr(ord(c) ^ ord(kunci[i % len(kunci)]))

    session['pesan'] = pesan_dekripsi
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)