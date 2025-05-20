from pathlib import Path
from unittest import mock

import pandas as pd
import sqlalchemy as sa
import utils.load as ld      # sesuaikan path paket

# ──────────────────────────────
# DataFrame sampel
# ──────────────────────────────
DF_SAMPLE = pd.DataFrame(
    {
        "Title":  ["Hoodie 1", "Jacket 2"],
        "Price":  [128000, 256000],
        "Rating": [4.5, 4.8],
    }
)


# ──────────────────────────────
# 1) save_csv
# ──────────────────────────────
def test_save_csv(tmp_path: Path):
    """File CSV harus tercipta & isinya sama persis."""
    out_file = tmp_path / "export" / "fashion.csv"   # folder 'export' belum ada
    ld.save_csv(DF_SAMPLE, path=out_file.as_posix())

    # 1) file ada
    assert out_file.exists()

    # 2) isinya identik
    df_read = pd.read_csv(out_file)
    pd.testing.assert_frame_equal(df_read, DF_SAMPLE)


# ──────────────────────────────
# 2) save_sql
# ──────────────────────────────
def test_save_sql(tmp_path: Path):
    """Data harus tersimpan di tabel sqlite sementara."""
    db_file = tmp_path / "db.sqlite"
    db_url  = f"sqlite:///{db_file}"

    # panggil fungsi
    ld.save_sql(DF_SAMPLE, sql_url=db_url)

    # verifikasi
    eng = sa.create_engine(db_url)
    with eng.connect() as con:
        rows = con.execute(sa.text("SELECT COUNT(*) FROM fashion")).scalar_one()
    assert rows == len(DF_SAMPLE)


# ──────────────────────────────
# 3) save_gsheet
# ──────────────────────────────
def test_save_gsheet_mock(monkeypatch):
    """
    Memastikan save_gsheet:
    • mem‑build service Sheets v4
    • memanggil method 'values().update()'

    Kita mock googleapiclient.build agar tak ada request eksternal.
    """
    # --- Fake objek service.spreasheets().values() chain ------------
    mock_values = mock.Mock()
    mock_values.update.return_value.execute.return_value = {}  # sukses
    mock_values.clear.return_value.execute.return_value  = {}

    mock_spreadsheets = mock.Mock()
    mock_spreadsheets.values.return_value = mock_values

    mock_service = mock.Mock()
    mock_service.spreadsheets.return_value = mock_spreadsheets

    # googleapiclient.build akan mengembalikan mock_service
    monkeypatch.setattr(ld, "build", mock.Mock(return_value=mock_service))
    # Credentials.from_service_account_file → dummy
    monkeypatch.setattr(ld, "Credentials", mock.Mock())

    # panggil fungsi
    ld.save_gsheet(
        DF_SAMPLE,
        creds_json="dummy.json",
        spreadsheet_id="sheet123",
        sheet_name="Sheet1",
    )

    # assertions – pastikan chain dipanggil
    assert mock_service.spreadsheets.call_count == 2
    assert mock_values.update.called
    assert mock_values.clear.called