import pypdfium2 as pdfium

pdf = pdfium.PdfDocument(
    r"C:\Users\Hasan\Documents\wise_uni\Semester 6\القواعد الفقهية\Buch.pdf"
)

# Abmessungen der ersten Seite übernehmen
width, height = pdf[0].get_size()

# Leere weiße Seite am Anfang einfügen
pdf.new_page(width=width, height=height, index=0)

# Neue PDF speichern
pdf.save(
    r"C:\Users\Hasan\Documents\wise_uni\Semester 6\القواعد الفقهية\Buch2.pdf"
)

pdf.close()