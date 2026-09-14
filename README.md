# myportofolio

Nama: Mohammad Zidane Kurnianto

NPM: 2506584861

Kelas: F

> **PBP my beloved** ❤️

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed         # seed database with Experience & Project data
python manage.py runserver
```

### Seed data

`python manage.py seed` populates the database with `Experience` and `Project` data used in this portfolio (FisioMate, GARDA NLP, Zikapedia, Samudera, etc.). The data itself is located in `main/management/commands/seed.py`, so simply edit it if you want to change it

## Dependencies

| Package         | Version | Purpose                                 |
| --------------- | ------- | --------------------------------------- |
| Django          | 6.1     | Web framework                           |
| gunicorn        | 26.2.0  | Production WSGI HTTP server             |
| whitenoise      | 6.12.0  | Static file serving in production       |
| psycopg2-binary | 2.9.12  | PostgreSQL database adapter             |
| requests        | 2.34.2  | HTTP client library                     |
| urllib3         | 2.7.0   | HTTP client (dependency of `requests`)  |
| python-dotenv   | 1.2.3   | Loads environment variables from `.env` |
| coverage        | 7.16.0  | Test coverage measurement               |
| selenium        | 4.49.0  | Browser automation for functional tests |

## Pertanyaan Reflektif

### Tugas 1

1. Saya menggunakan elemen semantik HTML5, contohnya section pada subbagian profile dan projects dan article untuk masing-masing project-item. Pembangunan tampilan portfolio ini sebenarnya bisa dicapai hanya dengan `<div>` biasa karena tingkah elemen semantik persis sama dengan `<div>`, yaitu blok HTML biasa yang tidak ada styling. Akan tetapi, penggunaan elemen semantik ini memiliki andil besar dalam SEO improvement dan aksesibilitas (seperti membantu kerja screen reader).
2. Dalam menciptakan tampilan yang responsive, tantangan yang saya temukan adalah menyesuaikan tampilan grid, flexbox, cropping gambar ke bervariasi lebar layar. Saat berpindah dari desktop ke mobile, padding besar yang awalnya terlihat bagus pada desktop, saya perkecil untuk tampilan mobile. Lalu, kumpulan item (seperti list projects pada section projects) yang saya sajikan dalam banyak kolom grid, saya kurangi `grid-template-columns`-nya menjadi 1.
3. Informasi yang ingin saya tampilkan sangat hard-coded, terutama untuk list projects. Sehingga, setiap kali ada project yang ingin ditambahkan, HTML project card harus di-copy dan informasinya diisi secara manual di HTML. Idealnya, card project ini dibuat reusable, sehingga untuk kedepannya, jika saya mau menambahkan project baru, saya tinggal menambahkannya ke list of projects. Django lalu mengiterasi setiap item pada list tersebut untuk dimasukkan ke dalam project card.

#### AI Disclosure: Tugas 1

Tidak menggunakan AI.

### Tugas 2

1. Ketika device client mengirim HTTP request ke sebuah route (misal: `/experience/`), Django mencari route yang sesuai di `urls.py` tingkat proyek, lalu mengarahkannya ke sebuah aplikasi (dalam kasus ini, aplikasi `main`) dan mencari route yang lebih spesifik di `urls.py` tingkat aplikasi tersebut untuk mencari view yang bertanggung jawab. View kemudian menerima request ini dan berkomunikasi dengan models terkait (dalam kasus ini, model `Experience`) untuk mengambil data yang tersimpan dalam DB. Model kemudian berinteraksi dengan Django ORM untuk meng-query data yang relevan dan mengembalikannya ke view dalam bentuk `QuerySet`. View kemudian menyimpan data tersebut dalam context dictionary dan mengopernya ke template. Django kemudian menggabungkan data dari view ke dalam HTML-nya. View kemudian mengirimkan HTML response kembali ke device client untuk ditampilkan.
2. Ada beberapa keunggulan menyimpan data portfolio dalam sebuah model:
   - Pembaruan data akan dimudahkan: dibanding harus mengedit HTML lalu redeploy setiap kali ada perubahan data, modifikasi data dapat dilakukan dengan mudah dan praktis melalui shell deployment atau Django Admin Dashboard built-in.
   - Data reusability: data yang sama (semisalnya data `Project`) dapat digunakan kembali di beberapa halaman lainnya dan akan tetap tersinkron ketika ada perubahan pada datanya.
   - Struktur data tervalidasi: field Django memastikan bahwasanya setiap attribute memiliki tipe data dan struktur yang valid. Ini dapat menghindari error akibat inkonsistensi.
3. Berikut adalah perbedaan `makemigrations` dan `migrate`
   - `makemigrations` berfungsi untuk merekam perubahan model dan mencatatnya dalam file migrasi. Django membandingkan file migrasi terakhir yang disimpan dengan model saat ini, ketika terdeteksi ada perubahhan, Django akan membuat file migrasi berisi skrip Python yang mengubah skema. Perubahan ini belum menyentuh database, command ini hanya membuat file migrations di folder `migrations/`.
   - `migrate` mengeksekusi file-file migrasi yang dibuat oleh `makemigrations`, dan menerjemahkan skrip tersebut untuk menjadi perintah SQL untuk mengubah skema database sesungguhnya.

   Misalnya, kita punya model Experience seperti berikut:

   ```python
    class Experience(models.Model):
        title = models.CharField(max_length=100)
        description = models.TextField()
   ```

   Lalu, menambahkan sebuah field baru (thumbnail):

   ```python
    class Experience(models.Model):
        title = models.CharField(max_length=100)
        description = models.TextField()
        thumbnail = models.URLField(blank=True, null=True)
   ```

   Untuk memperbarui skema database sesungguhnya, pertama eksekusi `python manage.py makemigrations` untuk membuat file migrasi, yang berisi skrip menambahkan field baru, yaitu field thumbnail. Untuk mengeksekusi skrip file migrasi ini, panggil `python manage.py migrate` supaya di database sesungguhnya tabel Experience memiliki kolom thumbnail :)

#### AI Disclosure: Tugas 2

Melihat hasil portfolio kawan-kawanku yang lain, saya menjadi merasa tidak mau kalah. Di submisi tugas sebelumnya, saya kurang memanfaatkan AI. Untuk tulis berikutnya, kemungkinan bakalan ada perombakan besar design language dari portfolio website saya :3

##### Tools yang Digunakan

- Claude Code: digunakan untuk membantu implementasi fitur, refactoring struktur template, dan pembuatan script pendukung.

> Catatan: Log penggunaan Claude Code disediakan di folder `logs/`

##### Bagian Spesifik yang Dibantu AI

1. Implementasi dark mode (fitur bonus), lengkap dengan function test via Selenium.

2. Refactor layout ke `base.html`: memindahkan komponen navbar dan footer yang sebelumnya terduplikasi di beberapa halaman ke satu `base.html`.
3. Seeder Script & Dokumentasi.

##### Strategi Prompting

- Menjalankan Claude Code dalam manual approval mode (bukan auto-accept), sehingga setiap perubahan/edit yang diajukan AI harus ditinjau dan disetujui secara eksplisit satu per satu.
- Semua kode hasil AI ditinjau dan diuji secara manual sebelum di-commit.
