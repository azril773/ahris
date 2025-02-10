<p align="center">
<img src="https://i.postimg.cc/gJxzpc5m/ahrisicon.png" />
<br>
<b>AHRIS (Asia Human Resource Information System) </b>
<br>
<!-- <a href="https://www.npmjs.com/~nestjscore" target="_blank"><img src="https://img.shields.io/npm/l/@nestjs/core.svg" alt="Package License" /></a> -->
</p>

## Cara penggunaan

- Ubuntu

  Buat virtual environment

  ```
  $ python3 -m venv namafolder_env
  ```

  Aktifkan virtual env

  ```
  $ source namafolder_env/bin/activate
  ```

  Install package

  ```
  (env)$ pip install -r requirements.txt
  ```

  Buat database dengan nama seperti dibawah ini

  - hrd
  - hrd\_(**namacabang**)

  Migrate models

  ```
  (env)$ python3 manage.py makemigrations
  (env)$ python3 manage.py migrate # untuk default database (hrd)
  (env)$ python3 manage.py migrate --database=namacabang # untuk spesifik cabang
  ```

  Jalankan server

  ```
  (env)$ python3 manage.py runserver
  ```

## Struktur folder

```
.
├── hrd
|   ├── /* file lainnya */
│   ├── settings.py
│   └── urls.py
├── hrd_app
│   ├── controllers
|   |   ├── /* folder controller */
|   |   └── views.py #main controller
│   ├── function
|   |   └── /* file function */
│   ├── middleware
|   |   └── /* file middleware */
│   ├── migrations
|   |   └── /* file migrations */
│   ├── router
|   |   ├── /* folder router */
|   |   └── urls.py #main router
|   └── templates
|       ├── master #main templates
|       └── /* folder templates */
├── static
├── tongbebeja
└── source
```

- **hrd**
  Folder ini digunakan untuk melakukan pengaturan pada aplikasi AHRIS, seperti database, folder static, redirect login, dll. Folder ini layaknya konfigurasi untuk aplikasi AHRIS

- **hrd_app**
  Folder ini merupakan folder utama untuk aplikasi AHRIS. Jika ingin mengubah atau menambahkan sesuatu pada aplikasi AHRIS bisa lewat folder ini

## Nama Cabang

Nama cabang harus sesuai dengan yang dibawah ini:

1. tasik
2. sumedang
3. cirebon
4. cihideung
5. garut

## Authors

- [Mohammad Azril Sugiarto](https://github.com/azril773)
