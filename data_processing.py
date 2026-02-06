import pandas as pd
import os
import re
import json


def clean_string(s):
    """Removes all special characters, spaces, and casing to make matching easier."""
    if not s: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()


def rearrange_carbon_data(file_path):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"

    xl = pd.ExcelFile(file_path)
    final_data = {}
    
    # We use very loose search terms to avoid missing data due to typos
    anchors = {
        "Gas": "gas",
        "Electricity": "el i kwh",
        "Heat": "el og varme",
        "Water": "vand"
    }
    years_to_find = [2019, 2020, 2021, 2022, 2023, 2024]

    print(f"--- STARTING DEBUG SCAN: {len(xl.sheet_names)} sheets ---")

    for sheet in xl.sheet_names:
        if sheet in ["Energi Oversigt", "Forside", "Template", "Kontrol"]: continue
        
        try:
            df = pd.read_excel(xl, sheet_name=sheet, header=None)
            building_carbon = {str(yr): {"Gas": 0, "Electricity": 0, "Heat": 0, "Water": 0} for yr in years_to_find}
            found_in_sheet = False

            for fuel_type, anchor_text in anchors.items():
                # 1. Search for the Island Anchor anywhere in the sheet
                mask = df.apply(lambda r: r.astype(str).str.contains(anchor_text, case=False).any(), axis=1)
                if not mask.any():
                    continue # This island just isn't on this sheet
                
                start_row = df[mask].index[0]
                
                # 2. Search for "kg CO2" within a 20-row window below that anchor
                search_window = df.iloc[start_row : start_row + 20, :]
                co2_mask = search_window.apply(lambda r: r.astype(str).str.contains('Kg. CO2 pr. år', case=False).any(), axis=1)
                
                if not co2_mask.any():
                    print(f"  [!] Found '{fuel_type}' anchor in {sheet}, but NO 'kg CO2' row nearby.")
                    continue
                
                co2_row_idx = search_window[co2_mask].index[0]
                co2_row_data = df.loc[co2_row_idx]

                # 3. Match Years to Columns (Search first 15 rows of the sheet for year labels)
                for yr in years_to_find:
                    yr_col = None
                    for c in range(len(df.columns)):
                        # Look in the top of the sheet or top of the island for the year
                        header_sample = df.iloc[0:20, c].astype(str).values
                        if any(str(yr) in val for val in header_sample):
                            yr_col = c
                            break
                    
                    if yr_col is not None:
                        val = pd.to_numeric(co2_row_data[yr_col], errors='coerce')
                        if pd.notnull(val) and val != 0:
                            building_carbon[str(yr)][fuel_type] = float(val)
                            found_in_sheet = True

            if found_in_sheet:
                final_data[sheet] = building_carbon
                print(f"  [OK] Successfully mapped Carbon for: {sheet}")
            else:
                pass # Sheet scanned but no numeric CO2 data found

        except Exception as e:
            print(f"  [ERROR] Could not process sheet {sheet}: {e}")

    # Final Summary
    with open('faaborg_carbon_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)
    
    print(f"--- SCAN FINISHED ---")
    print(f"Total Buildings with Carbon Data: {len(final_data)}")
    return len(final_data)


def get_faaborg_sheet_map(file_path):
    xl = pd.ExcelFile(file_path)
    all_sheets = xl.sheet_names
    
    # Load the master list
    df_ov = pd.read_excel(file_path, sheet_name='Energi Oversigt', skiprows=4)
    addr_col = df_ov.columns[0]
    df_ov[addr_col] = df_ov[addr_col].ffill()
    
    master_addresses = df_ov[addr_col].dropna().unique()
    
    mapping = {}
    for addr in master_addresses:
        c_addr = clean_string(addr)
        # Find the sheet where the cleaned name is a subset of the cleaned address or vice-versa
        match = next((s for s in all_sheets if c_addr in clean_string(s) or clean_string(s) in c_addr), None)
        mapping[str(addr)] = match
        
    return mapping

def extract_trend_data(file_path, sheet_name):
    if not sheet_name:
        return None, None, None

    # Load the specific building sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Pre-process: Find which row contains the energy data
    # We look for the row that has "Graddag" somewhere in it
    mask_act = df.apply(lambda row: row.astype(str).str.contains('Graddag', case=False).any(), axis=1)
    mask_tar = df.apply(lambda row: row.astype(str).str.contains('Mærke|Mål', case=False).any(), axis=1)
    
    if not mask_act.any() or not mask_tar.any():
        return None, None, None

    row_act = df[mask_act].iloc[0]
    row_tar = df[mask_tar].iloc[0]
    
    years = ['2019', '2020', '2021', '2022', '2023', '2024']
    y_act, y_tar, valid_yrs = [], [], []

    # Map the years to columns dynamically
    for yr in years:
        # Check if the year exists in any column header
        yr_col = next((c for c in df.columns if str(yr) in str(c)), None)
        if yr_col:
            val_a = pd.to_numeric(row_act[yr_col], errors='coerce')
            val_t = pd.to_numeric(row_tar[yr_col], errors='coerce')
            if pd.notnull(val_a) and pd.notnull(val_t):
                y_act.append(val_a)
                y_tar.append(val_t)
                valid_yrs.append(yr)
                
    return valid_yrs, y_act, y_tar


def get_domutech_footprint(file_path, target_address):
    try:
        # Load specifically the Domutech sheet
        df = pd.read_excel(file_path, sheet_name='Beregnede forbrug Domutech')
        
        # Clean column names
        df.columns = [str(c).strip() for c in df.columns]
        
        # Filter for the selected address (Kolonne 1)
        # We use a partial match to be safe
        mask = df['Kolonne1'].astype(str).str.contains(target_address, case=False, na=False)
        building_df = df[mask].copy()
        
        if building_df.empty:
            return None
            
        return building_df
    except Exception as e:
        print(f"Domutech Processing Error: {e}")
        return None