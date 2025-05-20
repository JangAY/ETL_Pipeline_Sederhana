from pathlib import Path
import argparse
import sys
from datetime import datetime
import subprocess
import logging

# ── modul internal ──────────────────────────────────────────
from utils.extract import scrape_fashion
from utils.transform import transform_DataFrame, transform_data
from utils.load import save_csv, save_gsheet, save_sql

# ── CONFIG ─────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).resolve().parent
BASE_URL     = "https://fashion-studio.dicoding.dev/{}"
EXCHANGE_RATE = 16_000

# Output
CSV_DIR   = ROOT_DIR / ""
CSV_PATH  = CSV_DIR / f"fashion.csv"

# Google Sheets
GCREDS_FILE    = ROOT_DIR / "google-sheets-api.json"
SPREADSHEET_ID = "17EtvDvS-a9W-x_NVDzT02KUeSpwvFU3aSfGm2hAgVNo"
SHEET_NAME     = "Sheet1"

# SQL Database (contoh PostgreSQL; ganti bila perlu)
SQL_URL = "postgresql+psycopg2://zham:hahaha@localhost:5432/fashiondb"


# ── CLI ────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="ETL Fashion Studio")
parser.add_argument("--no-gsheet", action="store_true", help="Lewati upload ke Google Sheets")
parser.add_argument("--no-sql",    action="store_true", help="Lewati upload ke DB SQL")
parser.add_argument("--log-level", default="INFO",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                    help="Tingkat logging (default: INFO)")
args = parser.parse_args()


# ── Logging setup ──────────────────────────────────────────
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / f"etl_{datetime.now():%Y%m%d}.log"

logging.basicConfig(
    level=getattr(logging, args.log_level),
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ],
)

log = logging.getLogger(__name__)


# ── MAIN ───────────────────────────────────────────────────
def main() -> None:
    log.info("=== ETL STARTED ===")

    # -----------------------------------------------------------------
    # 1) EXTRACT
    # -----------------------------------------------------------------
    log.info("Step 1/3 – EXTRACT")
    raw_data = scrape_fashion(BASE_URL)
    if not raw_data:
        log.error("Tidak ada data terambil. Proses dihentikan.")
        sys.exit(1)
    log.info("Berhasil mengekstrak %d baris.", len(raw_data))

    # -----------------------------------------------------------------
    # 2) TRANSFORM
    # -----------------------------------------------------------------
    log.info("Step 2/3 – TRANSFORM")
    try:
        df = transform_DataFrame(raw_data)
        df = transform_data(df, EXCHANGE_RATE)
    except Exception as e:
        log.exception("Transformasi gagal: %s", e)
        sys.exit(1)
    log.info("Data setelah transform: %d baris, %d kolom", *df.shape)

    # -----------------------------------------------------------------
    # 3) LOAD
    # -----------------------------------------------------------------
    log.info("Step 3/3 – LOAD")
    # CSV
    try:
        save_csv(df, path=CSV_PATH)
        log.info("CSV disimpan di %s", CSV_PATH.relative_to(ROOT_DIR))
    except Exception:
        log.exception("Gagal simpan CSV")

    # Google Sheets
    if args.no_gsheet:
        log.info("Lewati Google Sheets (--no-gsheet)")
    else:
        try:
            save_gsheet(df, GCREDS_FILE, SPREADSHEET_ID, SHEET_NAME)
        except Exception:
            log.exception("Gagal upload ke Google Sheets")

    # SQL
    if args.no_sql:
        log.info("Lewati SQL DB (--no-sql)")
    else:
        try:
            save_sql(df, sql_url=SQL_URL)
        except Exception:
            log.exception("Gagal simpan ke database")

    log.info("=== ETL FINISHED ===")


def write_requirements(out_file: str | Path = "requirements.txt") -> None:
    """
    Menyimpan daftar paket + versi yang aktif di lingkungan saat ini
    ke requirements.txt.

    Setara dengan:
        pip freeze > requirements.txt
    """
    out_file = Path(out_file)
    try:
        # pip list --format=freeze memberi daftar "package==version"
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            check=True,
            text=True,
            capture_output=True,
        )
        out_file.write_text(result.stdout)
        print(f"✔ requirements tersimpan → {out_file.resolve()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Gagal menghasilkan requirements: {e}")

if __name__ == "__main__":
    main()
    write_requirements()
