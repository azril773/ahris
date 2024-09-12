FROM python

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir gunicorn django django-import-export mysqlclient pyzk reportlab pandas django-weasyprint django-crontab django-mathfilters openpyxl requests django-debug-toolbar pika

# CMD python manage.py runserver