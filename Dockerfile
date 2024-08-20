FROM python

WORKDIR /app/
COPY . .
USER root
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir django django-import-export mysqlclient pyzk reportlab pandas django-weasyprint django-crontab django-mathfilters openpyxl requests

# CMD python manage.py runserver