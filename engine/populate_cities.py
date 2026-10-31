# -*- coding: utf-8 -*-
"""
Populate world_cities.db with all Census of India statutory cities/towns and global cities.
"""
import urllib.request
import zipfile
import io
import sqlite3
import os

IN_STATES = {
    '01': 'Andaman and Nicobar', '02': 'Andhra Pradesh', '03': 'Assam', '05': 'Chandigarh',
    '06': 'Dadra and Nagar Haveli', '07': 'Delhi', '09': 'Gujarat', '10': 'Haryana',
    '11': 'Himachal Pradesh', '12': 'Jammu and Kashmir', '13': 'Kerala', '14': 'Lakshadweep',
    '16': 'Maharashtra', '17': 'Manipur', '18': 'Meghalaya', '19': 'Karnataka',
    '20': 'Nagaland', '21': 'Odisha', '22': 'Puducherry', '23': 'Punjab',
    '24': 'Rajasthan', '25': 'Tamil Nadu', '26': 'Tripura', '28': 'West Bengal',
    '29': 'Sikkim', '30': 'Arunachal Pradesh', '31': 'Mizoram', '32': 'Daman and Diu',
    '33': 'Goa', '34': 'Bihar', '35': 'Madhya Pradesh', '36': 'Uttar Pradesh',
    '37': 'Chhattisgarh', '38': 'Jharkhand', '39': 'Uttarakhand', '40': 'Telangana', '41': 'Ladakh'
}

def populate():
    url_in = 'https://download.geonames.org/export/dump/IN.zip'
    print('Downloading GeoNames IN.zip (all Census and urban places)...')
    req = urllib.request.Request(url_in, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as resp:
        zip_bytes = resp.read()

    os.makedirs('data', exist_ok=True)
    db_path = os.path.join('data', 'world_cities.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("DELETE FROM cities WHERE country = 'IN'")
    print('Cleared previous India entries.')

    print('Parsing all Indian places...')
    batch = []
    seen = set()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        with z.open('IN.txt') as f:
            for line in f:
                parts = line.decode('utf-8', errors='ignore').split('\t')
                if len(parts) > 14 and parts[6] == 'P':
                    name = parts[1].strip()
                    if not name:
                        continue
                    state_code = parts[10].strip()
                    state_name = IN_STATES.get(state_code, state_code)
                    try:
                        lat = round(float(parts[4]), 4)
                        lon = round(float(parts[5]), 4)
                    except:
                        continue
                    
                    key = (name.lower(), state_code, round(lat, 2), round(lon, 2))
                    if key in seen:
                        continue
                    seen.add(key)
                    
                    batch.append((name, 'IN', state_name, lat, lon, 5.5))
                    if len(batch) >= 20000:
                        cur.executemany('INSERT INTO cities (name, country, state, lat, lng, timezone_offset) VALUES (?, ?, ?, ?, ?, ?)', batch)
                        batch = []

    if batch:
        cur.executemany('INSERT INTO cities (name, country, state, lat, lng, timezone_offset) VALUES (?, ?, ?, ?, ?, ?)', batch)

    conn.commit()

    cur.execute('CREATE INDEX IF NOT EXISTS idx_cities_name_nocase ON cities(name COLLATE NOCASE)')
    cur.execute("SELECT COUNT(id) FROM cities WHERE country = 'IN'")
    in_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(id) FROM cities")
    total_count = cur.fetchone()[0]
    print(f'Total Indian Cities, Towns & Urban Centres stored: {in_count}')
    print(f'Total Worldwide Cities & Towns stored in Database: {total_count}')
    conn.close()

if __name__ == '__main__':
    populate()
