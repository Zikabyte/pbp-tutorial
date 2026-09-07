# myportofolio

Nama: Mohammad Zidane Kurnianto

NPM: 2506584861

Kelas: F

> **PBP my beloved** ❤️

### Tugas 1

1. Saya menggunakan elemen semantik HTML5, contohnya section pada subbagian profile dan projects dan article untuk masing-masing project-item. Pembangunan tampilan portfolio ini sebenarnya bisa dicapai hanya dengan `<div>` biasa karena tingkah elemen semantik persis sama dengan `<div>`, yaitu blok HTML biasa yang tidak ada styling. Akan tetapi, penggunaan elemen semantik ini memiliki andil besar dalam SEO improvement dan aksesibilitas (seperti membantu kerja screen reader).
2. Dalam menciptakan tampilan yang responsive, tantangan yang saya temukan adalah menyesuaikan tampilan grid, flexbox, cropping gambar ke bervariasi lebar layar. Saat berpindah dari desktop ke mobile, padding besar yang awalnya terlihat bagus pada desktop, saya perkecil untuk tampilan mobile. Lalu, kumpulan item (seperti list projects pada section projects) yang saya sajikan dalam banyak kolom grid, saya kurangi `grid-template-columns`-nya menjadi 1.
3. Informasi yang ingin saya tampilkan sangat hard-coded, terutama untuk list projects. Sehingga, setiap kali ada project yang ingin ditambahkan, HTML project card harus di-copy dan informasinya diisi secara manual di HTML. Idealnya, card project ini dibuat reusable, sehingga untuk kedepannya, jika saya mau menambahkan project baru, saya tinggal menambahkannya ke list of projects. Django lalu mengiterasi setiap item pada list tersebut untuk dimasukkan ke dalam project card.

#### AI Disclosure: Tugas 1

Tidak menggunakan AI.
