import pytest
from bs4 import BeautifulSoup
from utils.extract import extract_fashion_data

# Contoh snippet HTML produk (mirip struktur di extract_fashion_data)
HTML_SNIPPET = """
<div class="product-details">
  <h3 class="product-title">Jacket 1</h3>
  <span class="price">$123.45</span>
  <p>Rating: 4.3 / 5</p>
  <p>Colors: 3</p>
  <p>Size: M</p>
  <p>Gender: Men</p>
</div>
"""

HTML_SNIPPET_MISSING_PRICE = """
<div class="product-details">
  <h3 class="product-title">Jacket 2</h3>
  <p>Rating: 4.0 / 5</p>
  <p>Colors: 2</p>
  <p>Size: L</p>
  <p>Gender: Women</p>
</div>
"""

def test_extract_single_product():
    """Pastikan parser mengambil field dengan benar."""
    soup = BeautifulSoup(HTML_SNIPPET, "html.parser")
    data = extract_fashion_data(soup)
    assert data["Title"] == "Jacket 1"
    assert data["Price"] == "$123.45"
    assert data["Rating"] == 4.3
    assert data["Colors"] == 3
    assert data["Size"] == "M"
    assert data["Gender"] == "Men"
    assert "timestamp" in data  # timestamp otomatis ada

def test_extract_product_missing_price():
    """Pastikan parser menangani harga yang hilang dengan None."""
    soup = BeautifulSoup(HTML_SNIPPET_MISSING_PRICE, "html.parser")
    data = extract_fashion_data(soup)
    assert data["Title"] == "Jacket 2"
    assert data["Price"] is None
    assert data["Rating"] == 4.0
    assert data["Colors"] == 2
    assert data["Size"] == "L"
    assert data["Gender"] == "Women"

def test_extract_invalid_rating():
    """Pastikan rating yang invalid menjadi None."""
    html_invalid_rating = """
    <div class="product-details">
      <h3 class="product-title">Jacket 3</h3>
      <span class="price">$50.00</span>
      <p>Rating: not_a_number / 5</p>
      <p>Colors: 1</p>
      <p>Size: S</p>
      <p>Gender: Unisex</p>
    </div>
    """
    soup = BeautifulSoup(html_invalid_rating, "html.parser")
    data = extract_fashion_data(soup)
    assert data["Rating"] is None