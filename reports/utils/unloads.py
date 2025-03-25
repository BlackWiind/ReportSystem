import io

from django.core.files.base import ContentFile
from django.http import FileResponse
from .utils import word_to_genitive

from reportlab.lib.styles import ParagraphStyle
from reports.models import Report
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph


def create_pdf_unloading(pk, user=None):
    data = Report.objects.get(pk=pk)

    buffer = io.BytesIO()
    width, height = A4

    my_canvas = canvas.Canvas(buffer, pagesize=A4)
    pdfmetrics.registerFont(
        TTFont('Arial', 'reports/static/reports/fonts/arial.ttf',
               'UTF-8'))

    main_stile = ParagraphStyle('Arial Style', fontName='Arial', fontSize=14)
    title_style = ParagraphStyle('Title Arial Style', fontName='Arial', fontSize=18)
    new_style = ParagraphStyle('Title Arial Style', fontName='Arial', fontSize=12)

    paragraph = Paragraph(f"Главному врачу<br></br>"
                          f"КГБУЗ ККБ Им. проф. С.И.Сергеева<br></br>"
                          f"Субботину Андрею Юрьевичу<br></br>"
                          f"От {' '.join(map(word_to_genitive,data.creator.job_title.strip().split(' ')))}<br></br>"
                          f"{' '.join(map(word_to_genitive,data.creator.__str__().strip().split(' ')))}<br></br>"
                          , new_style)
    paragraph.wrapOn(my_canvas, 200, 20)
    paragraph.drawOn(my_canvas, width - 250, height - 100)

    paragraph = Paragraph(f"<b>Рапорт.</b>", title_style)
    paragraph.wrapOn(my_canvas, 500, 20)
    paragraph.drawOn(my_canvas, width - 400, height - 200)

    paragraph = Paragraph(f"{data.text}<br></br><br></br>"
                          f"Обоснование: {data.justification}<br></br><br></br>"
                          f"Ориентировочная стоимость:"
                          f" {'{:0,.2f}'.format(data.price).replace(',', ' ')}р.", main_stile)
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

