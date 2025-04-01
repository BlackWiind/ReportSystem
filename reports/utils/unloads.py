import io

from django.core.files.base import ContentFile
from django.http import FileResponse
from reportlab.lib.colors import black
from reportlab.lib.fonts import addMapping

from .utils import word_to_genitive

from reportlab.lib.styles import ParagraphStyle
from reports.models import Report
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from PyPDF2 import PdfWriter, PdfReader


def create_pdf_unloading(pk, user=None):
    data = Report.objects.get(pk=pk)

    buffer = io.BytesIO()
    width, height = A4

    my_canvas = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(
        TTFont('Arial', 'reports/static/reports/fonts/arial.ttf',
               'UTF-8'))

    main_stile = ParagraphStyle('Arial Style', fontName='Arial', fontSize=12)
    title_style = ParagraphStyle('Title Arial Style', fontName='Arial', fontSize=16)
    small_style = ParagraphStyle('Title Arial Style', fontName='Arial', fontSize=10)

    paragraph = Paragraph(f"Главному врачу<br></br>"
                          f"КГБУЗ ККБ Им. проф. С.И.Сергеева<br></br>"
                          f"Субботину Андрею Юрьевичу<br></br>"
                          f"От {' '.join(map(word_to_genitive, data.creator.job_title.strip().split(' ')))}<br></br>"
                          f"{' '.join(map(word_to_genitive, data.creator.__str__().strip().split(' ')))}<br></br>"
                          , small_style)
    paragraph.wrapOn(my_canvas, 200, 20)
    paragraph.drawOn(my_canvas, width - 250, height - 100)

    paragraph = Paragraph(f"<b>Рапорт</b>", title_style)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 400, height - 200)

    main_text = f"{data.text}<br></br><br></br>"
    if data.justification:
        main_text += f"Обоснование: {data.justification}<br></br><br></br>"
    main_text += f" {'{:0,.2f}'.format(data.price).replace(',', ' ')}р."

    paragraph = Paragraph(main_text, main_stile)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 550, height - 300)

    paragraph = Paragraph(f"Одобренно:", main_stile)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 500, height - 450)

    paragraph = Paragraph(f"{user}", main_stile)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 250, height - 450)

    paragraph = Paragraph(f"{data.date_create.strftime('%d.%m.%Y')}", main_stile)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 500, height - 500)

    paragraph = Paragraph(f"{data.creator}", main_stile)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 250, height - 500)

    my_canvas.showPage()
    my_canvas.save()

    buffer.seek(0)
    # return FileResponse(buffer, as_attachment=True, filename=f"Рапорт{data.pk}.pdf")
    return f"Рапорт{data.pk}.pdf", buffer


def create_file_from_buffer(data) -> ContentFile:
    return ContentFile(data.getvalue(), 'print_form.pdf')


def edit_pdf(pdf_file, text):
    buffer = io.BytesIO()
    width, height = A4

    my_canvas = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(
        TTFont('Arial', 'reports/static/reports/fonts/arial.ttf',
               'UTF-8'))

    main_stile = ParagraphStyle('Arial Style', fontName='Arial', fontSize=12)

    paragraph = Paragraph(f"<b>Тут типа новый текст</b>", main_stile)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 500, height - 400)

    my_canvas.save()

    buffer.seek(0)
    new_pdf = PdfReader(buffer)
    existing_pdf = PdfReader(open(pdf_file, "rb"))
    output = PdfWriter()

    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    outputStream = open("temp.pdf", "w+b")
    output.write(outputStream)
    outputStream.seek(0)

    return FileResponse(outputStream, as_attachment=True, filename=f"report.pdf")


class PdfReports:
    width, height = A4
    pdfmetrics.registerFont(
        TTFont('Arial', 'reports/static/reports/fonts/arial.ttf',
               'UTF-8'))
    pdfmetrics.registerFont(
        TTFont('Arial Bold', 'reports/static/reports/fonts/arial_bold.ttf',
               'UTF-8'))

    addMapping('Arial', 0, 0, 'Arial')
    addMapping('Arial', 1, 0, 'Arial Bold')

    main_stile = ParagraphStyle('Arial Style', firstLineIndent=5, fontName='Arial', fontSize=12)
    title_style = ParagraphStyle('Title Arial Style', fontName='Arial', fontSize=16)
    small_style = ParagraphStyle('Small Arial Style', fontName='Arial', fontSize=10)
    sign_style = ParagraphStyle('Arial Style', firstLineIndent=5, borderPadding=3,
                                borderColor=black, borderWidth=2, fontName='Arial',
                                fontSize=8)

    obj = None

    canvas = None

    buffer = None

    def get_object(self, pk):
        self.obj = Report.objects.get(pk=pk)

    def draw_text(self, text, aW, aH, width, height, style=None):
        if style is None:
            style = self.main_stile
        paragraph = Paragraph(text, style)
        paragraph.wrapOn(self.canvas, aW, aH)
        paragraph.drawOn(self.canvas, width, height)

    def __init__(self, pk):
        self.buffer = io.BytesIO()
        self.get_object(pk)
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)

    def create_new_file(self):
        text = (f"Главному врачу<br></br>"
                f"КГБУЗ ККБ Им. проф. С.И.Сергеева<br></br>"
                f"Субботину Андрею Юрьевичу<br></br>"
                f"От {' '.join(map(word_to_genitive, self.obj.creator.job_title.strip().split(' ')))}<br></br>"
                f"{' '.join(map(word_to_genitive, self.obj.creator.__str__().strip().split(' ')))}<br></br>")
        self.draw_text(text, 200, 20, 395, 760, self.small_style)

        text = f"<b>Рапорт</b>"
        self.draw_text(text, 200, 20, 270, 600, self.title_style)

        text = f"{self.obj.text}<br></br><br></br>"
        if self.obj.justification:
            text += f"Обоснование: {self.obj.justification}<br></br><br></br>"
        text += f" {'{:0,.2f}'.format(self.obj.price).replace(',', ' ')}р."
        self.draw_text(text, 500, 20, 20, 450)

        text = f"{self.obj.date_create.strftime('%d.%m.%Y')}"
        self.draw_text(text, 200, 20, 20, 200)

        text = f"{self.obj.creator}"
        self.draw_text(text, 200, 20, 400, 200)

        self.add_sign({'fio': self.obj.creator, 'start': self.obj.date_create, 'end': self.obj.date_create},
                      70, 760)

        return self.return_file()

    def return_file(self):
        self.canvas.showPage()
        self.canvas.save()

        self.buffer.seek(0)
        return f"Рапорт{self.obj.pk}.pdf", self.buffer

    def add_sign(self, data:dict, width, height):
        text = (f"<para alignment=CENTER><b>Документ подписан<br></br> электронной подписью</b><br></br></para>"
                f"<para>Сертификат<br></br>"
                f"Туттипабудетсамсертификатпоказаглушка<br></br>"
                f"{data['fio']}<br></br>"
                f"Действителен с {data['start']} по {data['end']}</para>")
        self.draw_text(text, 200, 20, width, height, self.sign_style)


    def add_curator(self, user, file):

        text = f"Одобрил:"
        self.draw_text(text, 200, 20, 20, 160)

        text = f"{user}"
        self.draw_text(text, 200, 20, 400, 160)

        self.canvas.save()

        self.buffer.seek(0)
        new_pdf = PdfReader(self.buffer)
        existing_pdf = PdfReader(open(file.path, "rb"))
        output = PdfWriter()

        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

        outputStream = open("temp.pdf", "w+b")
        output.write(outputStream)
        outputStream.seek(0)

        return f"Рапорт{self.obj.pk}.pdf", outputStream
