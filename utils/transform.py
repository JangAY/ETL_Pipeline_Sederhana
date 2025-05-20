import pandas as pd
import numpy as np

def transform_DataFrame(data):
    df = pd.DataFrame(data)
    return df

def transform_data(data, Rupiah):
    try:
        # Hapus '$' dan konversi ke float, dengan mengabaikan error
        data['Price_Rp'] = data['Price'].str.replace('$', '', regex=False)
        data['Price_Rp'] = pd.to_numeric(data['Price_Rp'], errors='coerce')  # Konversi non-numeric jadi NaN
        
        # Kalikan dengan Rupiah
        data['Price_Rp'] = data['Price_Rp'] * Rupiah

        # Hapus baris dengan Price_Rp NaN atau infinite sebelum konversi ke int
        data = data[~data['Price_Rp'].isna()]  # buang NaN
        data = data[np.isfinite(data['Price_Rp'])]  # buang inf
        
        # Baru konversi ke integer
        data['Price_Rp'] = data['Price_Rp'].astype(float)

        # Hapus kolom Price lama
        data = data.drop(columns=['Price'])
        # Hapus unkown Product
        data = data[data['Title'] != 'Unknown Product']

        # Filter baris dengan rating valid (angka)
        data = data[data['Rating'].apply(lambda x: str(x).replace('.', '').isdigit())]
        data['Rating'] = pd.to_numeric(data['Rating'], errors='coerce')
        data = data.dropna(subset=['Rating'])

        # **Tambahkan filter rating antara 0 dan 5**
        data = data[(data['Rating'] >= 0) & (data['Rating'] <= 5)]

        # Hapus duplikat dan baris kosong
        data = data.drop_duplicates()
        data = data.dropna()

        # Transformasi tipe data
        data['Title'] = data['Title'].astype('string')
        data['Rating'] = data['Rating'].astype(float)
        data['Size'] = data['Size'].astype('string')
        data['Gender'] = data['Gender'].astype('string')

        return data
    except Exception as e:
        print(f"Transformation error: {str(e)}")
        return data
