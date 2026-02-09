import pandas as pd
import json
import time
from io import StringIO
from geopy.geocoders import Nominatim

def process_randers_map_data(timesafe_txt_path, buildings_xlsx_path):
    geolocator = Nominatim(user_agent="randers_energy_map_final")
    print("\n--- Starting Data Processing (Randers) ---")

    # 1. LOAD TIMESAFE (Correcting the 'Chinese' encoding error)
    try:
        # We read the raw bytes first to ensure we handle the encoding manually
        with open(timesafe_txt_path, 'rb') as f:
            raw_bytes = f.read()
        
        # This file is UTF-16. 'utf-16' handles the translation correctly.
        # We also strip the NUL characters (\x00) which often cause the 'Rows: 0' issue.
        clean_content = raw_bytes.decode('utf-16', errors='ignore').replace('\x00', '')
        
        # Load into Pandas using Tab as separator
        df_ts = pd.read_csv(StringIO(clean_content), sep='\t')
        print(f"Success: Timesafe file loaded. Found {len(df_ts)} ventilation units.")
    except Exception as e:
        print(f"Error loading Timesafe: {e}")
        return 0

    # 2. LOAD BUILDING LIST
    try:
        # Since your terminal said 'Filen var faktisk en Excel-fil', we use read_excel
        df_byg = pd.read_excel(buildings_xlsx_path)
        print(f"Success: Building list loaded. Found {len(df_byg)} buildings.")
    except Exception as e:
        print(f"Error loading Building list: {e}")
        return 0

    # Clean headers (remove leading/trailing spaces)
    df_ts.columns = [c.strip() for c in df_ts.columns]
    df_byg.columns = [c.strip() for c in df_byg.columns]

    map_results = []
    
    # 3. MATCHING & GEOCODING
    for _, ts_row in df_ts.iterrows():
        # Get the location name from Timesafe (e.g., 'Kulturhuset')
        loc_name = str(ts_row.get('LOKATION_NAVN', '')).strip()
        if not loc_name or loc_name.lower() == 'nan':
            continue
        
        # Look for this name in the Building List (Institutionsnavn)
        match = df_byg[df_byg['Institutionsnavn'].str.contains(loc_name, case=False, na=False)]
        
        if not match.empty:
            target = match.iloc[0]
            address = str(target.get('Adresse', '')).strip()
            
            # If we found an address, geocode it to get Lat/Lon
            if address and address.lower() != 'nan':
                full_query = f"{address}, Randers, Denmark"
                try:
                    location = geolocator.geocode(full_query)
                    if location:
                        status = str(ts_row.get('ENHED_TILSTAND', 'Grøn'))
                        color = 'red' if 'Rød' in status else 'orange' if 'Gul' in status else 'gray' if 'Ukendt' in status else 'green'
                        
                        map_results.append({
                            "name": loc_name,
                            "address": address,
                            "lat": location.latitude,
                            "lon": location.longitude,
                            "color": color,
                            "status": status
                        })
                        print(f"Mapped: {loc_name} at {address}")
                        time.sleep(1.1) # Wait to respect geocoder terms
                except Exception as ge_err:
                    print(f"Geocoding failed for {address}: {ge_err}")

    # 4. SAVE TO JSON
    with open('randers_processed.json', 'w', encoding='utf-8') as f:
        json.dump({"map_points": map_results}, f, indent=4, ensure_ascii=False)
    
    print(f"Processing Complete! {len(map_results)} points saved for the map.")
    return len(map_results)