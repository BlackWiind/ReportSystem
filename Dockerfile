FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /report_web

RUN mkdir /report_web/static && mkdir /report_web/media
RUN chmod -R 777 /report_web/static && chmod -R 777 /report_web/media
RUN chown -R root:root /report_web/static

COPY ./req.txt /req.txt
RUN pip install -r /req.txt

COPY . /report_web

EXPOSE 8000

# CMD ["python", "manage.py", "migrate"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]