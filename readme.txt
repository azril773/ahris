For ubuntu environment only

1.  install this libs first ()
    $ sudo apt install python3-pip python3-venv mysql-server python3-dev libmysqlclient-dev

2.  create virtual environment name : env
    $ python3 -m venv env    

3.  install libs in virtual env
    (env) pip install -r requirements.txt

4.  create database name : hrd
    mysql> create database hrd

5.  makemigrations and migrate model to database
    (env) python manage.py makemigrations
    (env) python manage.py migrate

6.  create super user
    (env) python manage.py createsuperuser

7.  if in development mode:
    (env) python manage.py runserver 0.0.0.0:8001
    you can use any port available, here i use 8001

8.  open browser
    localhost:8001/adminnya
    login with super user account
    add first status pegawai with "Staff"
    add your akses (choose your user, choose your akses, empty pegawai, choose sid with Staff)
    in the right corner click "lihat situs to go to site"
