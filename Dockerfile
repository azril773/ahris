FROM python

WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install gunicorn django django-import-export mysqlclient pyzk reportlab pandas django-weasyprint django-crontab django-mathfilters openpyxl requests django-debug-toolbar pika psycopg django-cors-headers djangorestframework APScheduler python-dotenv Authlib
ENV port="8000"
CMD python env/bin/gunicorn --workers=3 --bind 0.0.0.0:8000 hrd.wsgi:application