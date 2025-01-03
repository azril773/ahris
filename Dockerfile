FROM python

WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install gunicorn django django-import-export mysqlclient pyzk reportlab pandas django-weasyprint django-crontab django-mathfilters openpyxl requests django-debug-toolbar pika psycopg django-cors-headers djangorestframework APScheduler

# CMD python manage.py runserver