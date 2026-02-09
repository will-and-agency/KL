import pandas as pd
import json
import os

def process_frederiksberg_data(folder_path, file_map):
    maint_path = os.path.join(folder_path, file_map["maintenance"])
    proj_path = os.path.join(folder_path, file_map["projects"])
    
    # --- A. PROCESS VEDLIGEHOLDELSE (D1 & D7) ---
    # Row 1 = headers, Row 2 = useless, Row 3+ = data
    df_m = pd.read_excel(maint_path, header=0, skiprows=[1])
    df_m.columns = [str(c).strip() for c in df_m.columns]
    
    target_years = [str(year) for year in range(2023, 2034)]
    maint_results = []
    
    cat_col = next((c for c in df_m.columns if "hovedomkost" in c.lower() or "område" in c.lower()), "Kategori")
    cond_col = next((c for c in df_m.columns if "tilstand" in c.lower()), "Tilstand")

    for _, row in df_m.iterrows():
        raw_cond = str(row.get(cond_col, "2")).strip()
        cond_num = raw_cond[0] if raw_cond and raw_cond[0].isdigit() else "2"
        category = str(row.get(cat_col, "Andet")).strip()
        
        for yr in target_years:
            if yr in df_m.columns:
                cost = pd.to_numeric(row[yr], errors='coerce')
                if cost and cost > 0:
                    maint_results.append({
                        "Year": int(yr),
                        "Condition": f"Grad {cond_num}",
                        "Category": category,
                        "Cost": float(cost)
                    })

    # --- B. PROCESS ENERGIPROJEKTER (D2 & D8) ---
    # Vi bruger 'Forbedringer' arket. Hvis det også har 2 headers, bruger vi header=1
    df_p = pd.read_excel(proj_path, sheet_name="Forbedringer", header=1)
    df_p.columns = [str(c).strip() for c in df_p.columns]
    
    project_results = []
    for _, row in df_p.iterrows():
        # Vi leder efter Investering (DDK), Besparelse (CO2) og Tilbagebetaling (TBT)
        ddk = pd.to_numeric(row.get("Investering", 0), errors='coerce')
        co2 = pd.to_numeric(row.get("Besparelse", 0), errors='coerce')
        tbt = pd.to_numeric(row.get("TBT", 0), errors='coerce')
        emne = str(row.get("Type", "Diverse"))
        forslag = str(row.get("Titel", "Ingen titel"))
        bygning = str(row.get("Bygninger","Ingen bygning navn"))
        
        if ddk > 0:
            project_results.append({
                "Type": emne,
                "Description": bygning+": "+forslag,
                "DDK": float(ddk),
                "CO2": float(co2),
                "TBT": float(tbt)
            })

    try:
        comp_path = os.path.join(folder_path, file_map["compliance"])
        
        # Load sheets with headers on Row 2
        df_byg = pd.read_excel(comp_path, sheet_name="Bygninger", header=1)
        df_teo = pd.read_excel(comp_path, sheet_name="Teoretisk forbrug", header=1)
        
        # Clean column names
        df_byg.columns = [str(c).strip() for c in df_byg.columns]
        df_teo.columns = [str(c).strip() for c in df_teo.columns]

        # Explicitly define the join columns based on your find
        left_col = "Bygningsnavn" if "Bygningsnavn" in df_byg.columns else "Navn"
        right_col = "Ejendomsnavn" if "Ejendomsnavn" in df_teo.columns else "Navn"

        # Perform the merge
        df_combined = pd.merge(
            df_byg, 
            df_teo, 
            left_on=left_col, 
            right_on=right_col, 
            how="inner"
        )

        compliance_results = []
        for _, row in df_combined.iterrows():
            area = pd.to_numeric(row.get("Opvarmet areal (m²)", 0), errors='coerce')
            year = pd.to_numeric(row.get("Opførelsesår", 0), errors='coerce')
            mark = str(row.get("Energimærke", "U"))
            
            save_col = "Besparelse % (kWh)"
            raw_val = pd.to_numeric(row.get(save_col, 0), errors='coerce')
            
            # 2. Logic: If Excel stores 0.20 instead of 20, convert it
            if pd.notnull(raw_val) and 0 < raw_val < 1:
                saving_val = raw_val * 100
            else:
                saving_val = raw_val if pd.notnull(raw_val) else 0

            compliance_results.append({
                "Building": str(row.get("Bygningsnavn", "Unknown")),
                "Area": float(area) if pd.notnull(area) else 0,
                "Year": int(year) if pd.notnull(year) else 0,
                "EnergyMark": mark,
                "SavingPct": round(float(saving_val), 2)
            })

        # Save integrated JSON
        final_output = {
            "maintenance": maint_results,
            "projects": project_results,
            "compliance": compliance_results
        }
        with open('frb_processed.json', 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=4, ensure_ascii=False)
            
        print(f"Sync Success! Merged {len(df_combined)} buildings.")

    except Exception as e:
        print(f"Sync Error: {e}")
        # Save empty compliance list so the app doesn't crash, but keep other data
        with open('frb_processed.json', 'w', encoding='utf-8') as f:
            json.dump({"maintenance": maint_results, "projects": project_results, "compliance": []}, f)
        raise e