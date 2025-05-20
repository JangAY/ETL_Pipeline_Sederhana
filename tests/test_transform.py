import pandas as pd
import numpy as np
import pytest

# sesuaikan import modul
from utils.transform import transform_DataFrame, transform_data

# ────────────────────────────────────────────────────────────────
#  1)  Data tiruan (raw)
# ────────────────────────────────────────────────────────────────
RAW_DATA = [
    {
        "Title": "Unknown Product", "Price": "$10.00",
        "Rating": "invalid", "Colors": 3, "Size": "M",  "Gender": "Men",
        "timestamp": "2025‑05‑18 09:00:00",
    },
    {   # baris valid
        "Title": "Hoodie 1", "Price": "$20.00",
        "Rating": "4.5", "Colors": 3, "Size": "M", "Gender": "Men",
        "timestamp": "2025‑05‑18 09:00:00",
    },
    {   # duplikat → akan dibuang
        "Title": "Hoodie 1", "Price": "$20.00",
        "Rating": "4.5", "Colors": 3, "Size": "M", "Gender": "Men",
        "timestamp": "2025‑05‑18 09:00:00",
    },
    {   # Rating di luar range (7) → dianggap invalid, dibuang
        "Title": "Bad Rating", "Price": "$30.00",
        "Rating": "7", "Colors": 3, "Size": "L", "Gender": "Women",
        "timestamp": "2025‑05‑18 09:00:00",
    },
]

RUPIAH_RATE = 16_000


# ────────────────────────────────────────────────────────────────
#  2)  Fixtures
# ────────────────────────────────────────────────────────────────
@pytest.fixture
def raw_df():
    """DataFrame mentah sebagai input transformasi."""
    return transform_DataFrame(RAW_DATA)


# ────────────────────────────────────────────────────────────────
#  3)  Test transform_DataFrame
# ────────────────────────────────────────────────────────────────
def test_transform_dataframe(raw_df):
    """transform_DataFrame harus menghasilkan DataFrame dengan kolom tepat."""
    assert isinstance(raw_df, pd.DataFrame)
    expected_cols = {"Title", "Price", "Rating", "Colors", "Size", "Gender", "timestamp"}
    assert expected_cols.issubset(raw_df.columns)


# ────────────────────────────────────────────────────────────────
#  4)  Test transform_data (aturan bisnis)
# ────────────────────────────────────────────────────────────────
def test_transform_data_rules(raw_df):
    cleaned = transform_data(raw_df.copy(), Rupiah=RUPIAH_RATE)

    # 1) Unknown Product terbuang
    assert "Unknown Product" not in cleaned["Title"].values

    # 2) Duplikat len = 1
    assert cleaned["Title"].value_counts().max() == 1

    # 3) Semua Price_Rp int & hasil konversi benar
    assert cleaned["Price_Rp"].dtype == "float64"
    hoodie_price = cleaned.loc[cleaned["Title"] == "Hoodie 1", "Price_Rp"].iloc[0]
    assert hoodie_price == int(20.00 * RUPIAH_RATE)

    # 4) Rating float dan valid (0‑5)
    assert cleaned["Rating"].dtype == float
    assert cleaned["Rating"].between(0, 5).all()

    # 5) Kolom Price lama dihapus
    assert "Price" not in cleaned.columns