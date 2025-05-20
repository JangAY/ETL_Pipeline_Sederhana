import requests
import pandas as pd
from bs4 import BeautifulSoup
import time
import re
from pathlib import Path
from datetime import datetime 

from utils.transform import transform_data, transform_DataFrame 
from utils.load import save_csv, save_gsheet, save_sql, dump_sql
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
    )
}

def fetching_content(url):
    session = requests.Session()
    response = session.get(url, headers=HEADERS)
    try:
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error saat melakukan request terhadap {url}: {e}")
        return None
    
def extract_fashion_data(web):
    product_element = web.find('div', class_='product-details')
    fashion_title = product_element.find('h3', class_='product-title').text
    try:
        price = product_element.find('span', class_='price').get_text(strip=True)
    except AttributeError:
        price = None
    
        # --- inisialisasi variabel ---
    rating, colors, size, gender = None, None, None, None

    for p in product_element.find_all('p'):
        text = p.get_text(strip=True)

        # rating
        if 'Rating' in text:
            try:
                rating = float(re.search(r'([\d.]+)\s*/\s*5', text).group(1))
            except (AttributeError, ValueError):
                rating = None

        # jumlah warna
        elif 'Colors' in text:
            try:
                colors = int(re.search(r'(\d+)', text).group(1))
            except (AttributeError, ValueError):
                colors = None

        # size
        elif 'Size' in text:
            try:
                size = re.search(r'Size:\s*([A-Za-z0-9]+)', text).group(1)
            except AttributeError:
                size = None

        # gender
        elif 'Gender' in text:
            try:
                gender = re.search(r'Gender:\s*([A-Za-z]+)', text).group(1)
            except AttributeError:
                gender = None
        
    fashion = {
        "Title": fashion_title,
        "Price": price,
        "Rating": rating,
        "Colors": colors,
        "Size": size,
        "Gender": gender,
        # kolom baru
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return fashion
    
def scrape_fashion(base_url, start_page=1, delay=2):

    data = []
    page_number = start_page

    while True:
        url = base_url.format("index.html" if page_number==1 else f"page{page_number}.html")
        print(f"Mengambil data pada halaman {url}")

        content = fetching_content(url)
        if content:
            soup = BeautifulSoup(content, "html.parser")
            article_element = soup.find_all('div', class_='collection-card')
            for article in article_element:
                fashion = extract_fashion_data(article)
                data.append(fashion)

            next_button = soup.find('li', class_='page-item next')
            if next_button:
                page_number +=1
                time.sleep(delay) 
            else:
                break
        else:
            break
    return data

def main():
    ROOT_DIR = Path(__file__).resolve().parent.parent   # naik 1 level
    BASE_URL = 'https://fashion-studio.dicoding.dev/{}'
    all_fashion_data = scrape_fashion(BASE_URL)
    if all_fashion_data:
        try:
            # Transformasi Data
            DataFrame = transform_DataFrame(all_fashion_data)
            DataFrame = transform_data(DataFrame, 16000)
            print(DataFrame)

            # Load Data
            save_csv(DataFrame, "fashion.csv")

            save_gsheet(DataFrame, creds_json= ROOT_DIR / "google-sheets-api.json",      # Path objek
                        spreadsheet_id="17EtvDvS-a9W-x_NVDzT02KUeSpwvFU3aSfGm2hAgVNo",
                        sheet_name="Sheet1"

            )

            save_sql(
                DataFrame,
                sql_url="postgresql+psycopg2://zham:hahaha@localhost:5432/fashiondb",
            )

            dump_sql(
                sql_url="postgresql+psycopg2://zham:hahaha@localhost:5432/fashiondb", 
                output_file="fashion.sql"
                )

        except Exception as e:
            print(f"Terjadi kesalahan dalam proses: {e}") 
    else:
        print("Tidak ada data yang ditemukan.")

    
if __name__ == '__main__':
    main()