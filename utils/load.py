import os
import re
import pandas as pd
from sqlalchemy import create_engine
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import subprocess
from pathlib import Path

# ───────────────────────────
# 1)  CSV
# ───────────────────────────
def save_csv(data, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)  # pastikan folder ada
        data.to_csv(path, index=False)
        print(f"✔ CSV   → {path}")
    except Exception as e:
        print(f"❌ Gagal menyimpan CSV ke {path}: {e}")

# ───────────────────────────
# 2)  Google Sheets
# ───────────────────────────
def save_gsheet(data, creds_json, spreadsheet_id, sheet_name):
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(creds_json, scopes=scopes)
        service = build("sheets", "v4", credentials=creds)

        # Clear old content
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A:Z"
        ).execute()

        body = {"values": [data.columns.tolist()] + data.values.tolist()}

        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="RAW",
            body=body
        ).execute()
        print(f"✔ GSheet→ https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
    except FileNotFoundError:
        print(f"❌ File credential tidak ditemukan: {creds_json}")
    except HttpError as http_err:
        print(f"❌ Google Sheets API error: {http_err}")
    except Exception as e:
        print(f"❌ Gagal menyimpan ke Google Sheets: {e}")

# ───────────────────────────
# 3)  SQLAlchemy
# ───────────────────────────
def save_sql(data, sql_url):
    try:
        # Membuat engine database
        engine = create_engine(sql_url)
        
        # Menyimpan data ke tabel 'bookstoscrape' jika tabel sudah ada, data akan ditambahkan (append)
        with engine.connect() as con:
            data.to_sql('fashion', con=con, if_exists='append', index=False)
            print("Data berhasil ditambahkan Ke Database!")
  
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data: {e}")

def dump_sql(sql_url, output_file="fashion_dump.sql"):
    """
    Dump isi database ke file .sql di root project.
    Hanya support PostgreSQL (pg_dump harus tersedia di PATH).
    """

    # Parsing connection string postgresql+psycopg2://user:pass@host:port/dbname
    pattern = r'postgresql\+psycopg2://(?P<user>[^:]+):(?P<password>[^@]+)@(?P<host>[^:]+):(?P<port>\d+)/(?P<dbname>\w+)'
    match = re.match(pattern, sql_url)
    if not match:
        raise ValueError("Format sql_url tidak sesuai. Hanya mendukung postgresql+psycopg2.")

    user = match.group("user")
    password = match.group("password")
    host = match.group("host")
    port = match.group("port")
    dbname = match.group("dbname")

    output_path = Path(output_file).resolve()

    env = os.environ.copy()
    env["PGPASSWORD"] = password  # supaya password tidak diminta interaktif

    cmd = [
        "pg_dump",
        "-h", host,
        "-p", port,
        "-U", user,
        "-F", "p",  # plain SQL
        "-f", str(output_path),
        dbname
    ]

    print(f"Dumping database to: {output_path}")
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"✔ Database berhasil di-dump ke {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal dump database: {e}")