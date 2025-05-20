# 📦 Fashion‑Studio ETL Pipeline

ETL (Extract‑Transform‑Load) sederhana untuk mengambil data katalog pakaian dari  
<https://fashion-studio.dicoding.dev>, membersihkan & mengubahnya, lalu
menyimpan ke:

1. **CSV** (timestamped)
2. **Google Sheets**
3. **PostgreSQL** melalui SQLAlchemy  
   (otomatis membuat/dump `fashion.sql` dengan `pg_dump`)

---

## 🗂 Struktur Folder
```
submission-fundamental-pemrosesan-data/
│
├── utils/ # fungsi inti
│ ├── extract.py # web‑scraping
│ ├── transform.py # pembersihan & konversi
│ └── load.py # simpan ke CSV / GSheet / DB
│
├── tests/ # unit‑test Pytest
│ ├── test_conftest.py
│ ├── test_extract.py
│ ├── test_transform.py
│ └── test_load.py
│
├── fashion.csv # Database
├── main.py # entry‑point CLI ETL
├── requirements.txt # pip freeze otomatis
└── README.md
```
---

## 🔧 Instalasi Lokal

```bash
# 1. Clone / download repo
git clone https://github.com/yourname/fashion-etl.git
cd fashion-etl

# 2. Buat virtualenv (opsional tapi disarankan)

python -m venv .env
# Windows
.env\Scripts\activate
# macOS / Linux
source .env/bin/activate

# 3. Install dependensi

pip install -r requirements.txt

# 4. Menjalankan ETL

python main.py           # run full ETL

# 5. Unit Test
# Semua fungsi inti memiliki test Pytest.
pytest -q

```
---
