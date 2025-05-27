import io

from django.core.files.base import ContentFile
from django.http import FileResponse
from reportlab.lib.colors import black
from reportlab.lib.fonts import addMapping

from users.models import User
from .utils import word_to_genitive

from reportlab.lib.styles import ParagraphStyle
from reports.models import Report
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph
from PyPDF2 import PdfWriter, PdfReader


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

    # Обновленные стили
    main_style = ParagraphStyle('Arial Style', firstLineIndent=5, fontName='Arial', fontSize=12,
                                spaceBefore=12, spaceAfter=12)
    title_style = ParagraphStyle('Title Arial Style', alignment=1, fontName='Arial Bold',
                                 fontSize=16, spaceBefore=40, spaceAfter=40)
    small_style = ParagraphStyle('Small Arial Style', fontName='Arial', fontSize=10)
    sign_style = ParagraphStyle('Arial Style', firstLineIndent=5, borderPadding=3,
                                borderColor=black, borderWidth=2, fontName='Arial',
                                fontSize=8)
    db_style = ParagraphStyle('DBStyle', fontName='Arial', fontSize=8, alignment=2,
                              rightIndent=20, bottomIndent=20)  # Добавлены отступы

    obj = None
    canvas = None
    buffer = None

    def get_object(self, pk):
        self.obj = Report.objects.get(pk=pk)

    def draw_text(self, text, aW, aH, width, height, style=None):
        if style is None:
            style = self.main_style
        paragraph = Paragraph(text, style)
        paragraph.wrapOn(self.canvas, aW, aH)
        paragraph.drawOn(self.canvas, width, height)

    def __init__(self, pk):
        self.buffer = io.BytesIO()
        self.get_object(pk)
        self.canvas = canvas.Canvas(self.buffer, pagesize=A4)

    def create_new_file(self):
        # Шапка документа
        text = (f"Главному врачу<br></br>"
                f"КГБУЗ ККБ Им. проф. С.И.Сергеева<br></br>"
                f"Субботину Андрею Юрьевичу<br></br>"
                f"От {' '.join(map(word_to_genitive, self.obj.creator.job_title.strip().split(' ')))}<br></br>"
                f"{' '.join(map(word_to_genitive, self.obj.creator.__str__().strip().split(' ')))}<br></br>")
        self.draw_text(text, 200, 20, 395, 760, self.small_style)

        # Заголовок "Рапорт" точно по центру
        text = f"<b>Рапорт</b>"
        self.draw_text(text, self.width, 20, 0, 600, self.title_style)  # Центрирование по всей ширине

        # Основной текст с отступами и динамическим позиционированием
        content_height = 500  # Стартовая позиция для контента
        text_content = f"{self.obj.text}<br/><br/>"

        if self.obj.justification:
            text_content += f"Обоснование: {self.obj.justification}<br/><br/>"

        text_content += f" {'{:0,.2f}'.format(self.obj.price).replace(',', ' ')}р."

        # Рассчитываем высоту контента
        temp_para = Paragraph(text_content, self.main_style)
        content_height_needed = temp_para.wrap(self.width - 113.4, self.height)[1]  # 113.4 = 2cm*2

        # Если контент слишком большой, уменьшаем стартовую позицию
        # if content_height_needed > 400:
        #     content_height = 550 - content_height_needed
        content_height = 550 - content_height_needed

        self.draw_text(text_content, self.width - 113.4, self.height, 56.7, content_height)

        # Дата и подписи с проверкой на длину
        date_text = f"{self.obj.date_create.strftime('%d.%m.%Y')}"
        self.draw_text(date_text, 200, 20, 56.7, 100)

        creator_name = f"{self.obj.creator}"
        self.draw_text(creator_name, 200, 20, self.width - 256.7, 100)  # 206.7 = 56.7 + 150

        curator = self.obj.creator if self.obj.creator.custom_permissions.name == 'curator' else\
            User.objects.get(custom_permissions__name='curator', curators_group=self.obj.curators_group)
        self.draw_text("Одобрил:", 200, 20, 56.7, 70)
        self.draw_text(f"{curator}", 200, 20, self.width - 256.7, 70)

        # Номер в базе данных с защитой от выхода за границы
        db_text = f"номер в базе данных: {self.obj.pk}"
        self.draw_text(db_text, 200, 20, self.width - 230, 30, self.db_style)

        return self.return_file()

    def return_file(self):
        self.canvas.showPage()
        self.canvas.save()
        self.buffer.seek(0)
        return f"Рапорт{self.obj.pk}.pdf", self.buffer

    # Остальные методы без изменений
    def add_sign(self, data: dict, width, height):
        text = (f"<para alignment=CENTER><b>Документ подписан<br/> электронной подписью</b><br/></para>"
                f"<para>Сертификат<br/>"
                f"Туттипабудетсамсертификатпоказаглушка<br/>"
                f"{data['fio']}<br/>"
                f"Действителен с {data['start']} по {data['end']}</para>")
        self.draw_text(text, 200, 20, width, height, self.sign_style)

    def add_curator(self, user, file):
        text = f"Одобрил:"
        self.draw_text(text, 200, 20, 56.7, 160)

        text = f"{user}"
        self.draw_text(text, 200, 20, self.width - 256.7, 160)

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