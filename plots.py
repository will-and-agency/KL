import pandas as pd
import numpy as np
import plotly.express as px
import json
import os
import traceback
import re
import plotly.graph_objects as go
from data_processing import *
from data_processing_randers import *
import folium

## Helper functions 

def extract_address_base(address):
    """
    Extract the base street name and number from an address.
    E.g., "Banegårdspladsen 2 A B C D" -> "banegårdspladsen 2"
          "Banegårdspladsen 2C" -> "banegårdspladsen 2"
    """
    addr = str(address).strip().lower()
    # Match: street name + first number (ignoring letters/units after)
    match = re.match(r'^(.+?)\s+(\d+)', addr)
    if match:
        return f"{match.group(1).strip()} {match.group(2)}"
    return addr


def clean_domutech_address(address):
    """
    Clean Domutech Address column by removing postal code and city suffix.
    E.g., "Banegårdspladsen 4, 5600 Faaborg" -> "Banegårdspladsen 4"
    """
    addr = str(address).strip()
    # Remove everything after the comma (postal code + city)
    if ',' in addr:
        addr = addr.split(',')[0].strip()
    return addr


def extract_from_energi_oversigt(df_ov, addr_row, selected_address):
    """
    Extract yearly kWh pr m2 data from Energi Oversigt sheet.
    First tries 'kWh pr m2' columns, then calculates from Varme+El/m2.
    Returns years list and actual_values list.
    """
    if addr_row is None or addr_row.empty:
        return [], []

    row = addr_row.iloc[0] if hasattr(addr_row, 'iloc') else addr_row
    years = []
    actual_values = []

    # Get m2 for calculating consumption per m2
    m2_col = next((c for c in df_ov.columns if str(c).lower().strip() == 'm2'), None)
    m2_value = pd.to_numeric(row[m2_col], errors='coerce') if m2_col else None

    for year in range(2019, 2026):
        value_found = None

        # First try: Look for "kWH pr m2" columns
        for col in df_ov.columns:
            col_lower = str(col).lower()
            if 'kwh' in col_lower and 'pr m2' in col_lower.replace('.', '') and str(year) in str(col):
                val = pd.to_numeric(row[col], errors='coerce')
                if pd.notna(val) and val > 0:
                    value_found = val
                break

        # Second try: Calculate from Varmeforbrug + Elforbrug / m2
        if value_found is None and m2_value and m2_value > 0:
            varme_col = next((c for c in df_ov.columns if 'varmeforbrug' in c.lower() and str(year) in c and 'kwh' in c.lower()), None)
            el_col = next((c for c in df_ov.columns if 'elforbrug' in c.lower() and str(year) in c and 'kwh' in c.lower()), None)

            varme = pd.to_numeric(row[varme_col], errors='coerce') if varme_col else 0
            el = pd.to_numeric(row[el_col], errors='coerce') if el_col else 0

            if pd.notna(varme) or pd.notna(el):
                varme = varme if pd.notna(varme) else 0
                el = el if pd.notna(el) else 0
                total = varme + el
                if total > 0:
                    value_found = total / m2_value

        if value_found is not None and value_found > 0:
            years.append(str(year))
            actual_values.append(value_found)

    return years, actual_values


def build_trend_chart_from_data(fig_detail, years, actual_values, target_value, selected_address, is_dark_mode):
    """
    Build the dual-line trend chart with actual vs target consumption.
    """
    # Add actual consumption line
    fig_detail.add_trace(go.Scatter(
        x=years,
        y=actual_values,
        mode='lines+markers',
        name='Faktisk Forbrug',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=10),
        hovertemplate='%{x}: %{y:.1f} kWh/m²<extra></extra>'
    ))

    gap_text = ""
    gap_color = "#666"

    # Add target line if available
    if target_value and pd.notna(target_value):
        target_line = [target_value] * len(years)

        fig_detail.add_trace(go.Scatter(
            x=years,
            y=target_line,
            mode='lines',
            name=f'Energimærke ({target_value:.0f} kWh/m²)',
            line=dict(color='#10b981', width=2, dash='dash'),
            hovertemplate='Mål: %{y:.1f} kWh/m²<extra></extra>'
        ))

        # Add shaded gap area
        fig_detail.add_trace(go.Scatter(
            x=years + years[::-1],
            y=actual_values + target_line[::-1],
            fill='toself',
            fillcolor='rgba(239, 68, 68, 0.2)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Ineffektivitets-gap',
            hoverinfo='skip',
            showlegend=True
        ))

        avg_gap = np.mean([a - target_value for a in actual_values])
        gap_text = f"Gns. afvigelse: {avg_gap:+.1f} kWh/m²"
        gap_color = "#ef4444" if avg_gap > 0 else "#10b981"

    fig_detail.update_layout(
        title=dict(text=f"Forbrugsudvikling: {selected_address}", font=dict(size=14)),
        template="plotly_dark" if is_dark_mode else "plotly_white",
        xaxis_title="År",
        yaxis_title="kWh pr. m²",
        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        margin=dict(t=80, b=80),
        hovermode='x unified',
        annotations=[
            dict(
                text=gap_text,
                xref="paper", yref="paper",
                x=0.5, y=1.06,
                showarrow=False,
                font=dict(size=12, color=gap_color),
                xanchor="center"
            )
        ] if gap_text else []
    )


def find_matching_domutech_rows(df_domu, selected_address, addr_column='Address'):
    """
    Find rows in Domutech data that match the selected address.
    Uses base address matching (street + number) for flexible matching.
    """
    selected_base = extract_address_base(selected_address)

    # Clean and extract base from Domutech addresses
    domu_bases = df_domu[addr_column].apply(
        lambda x: extract_address_base(clean_domutech_address(x))
    )

    # Match rows where the base address matches
    mask = domu_bases == selected_base

    return df_domu[mask]


# ============ Randers =============

def create_roi_matrix(muni_key, is_dark_mode=False):
    try:
        with open('mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        muni_cfg = mapping.get(muni_key)
        cfg = muni_cfg["roi_data"]
        cols = cfg["columns"] 
        
        file_path = os.path.join(muni_cfg["folder"], cfg["file"])
        df = pd.read_excel(file_path, sheet_name=cfg["sheet"], skiprows=cfg["skiprows"])

        # Data Cleaning
        df[cols["x"]] = pd.to_numeric(df[cols["x"]], errors='coerce')
        df[cols["y"]] = pd.to_numeric(df[cols["y"]], errors='coerce')
        df[cols["size"]] = pd.to_numeric(df[cols["size"]], errors='coerce')
        df = df.dropna(subset=[cols["x"], cols["y"]]).copy()
        df['plotly_size'] = df[cols["size"]].abs().fillna(1) 

        # Danish Legend Labels
        df['Resultat'] = df[cols["y"]].apply(lambda x: 'CO2 Besparelse' if x >= 0 else 'CO2 Stigning')

        fig = px.scatter(
            df, 
            x=cols["x"], 
            y=cols["y"],
            size='plotly_size',
            size_max=30,
            color='Resultat', 
            hover_name=cols["label"],
            # Using Danish terminology in tooltips
            labels={
                cols["x"]: "Investering (DKK)", 
                cols["y"]: "Årlig CO2-besparelse (tons)",
                "Resultat": "Type"
            },
            color_discrete_map={'CO2 Besparelse': '#10b981', 'CO2 Stigning': '#ef4444'},
            template="plotly_dark" if is_dark_mode else "plotly_white"
        )
        
        # Add reference lines at zero for both axes
        fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
        fig.add_vline(x=0, line_dash="dash", line_color="gray", line_width=1)

        # Calculate axis ranges
        y_min = df[cols["y"]].min()
        y_max = df[cols["y"]].max()
        y_padding = (y_max - y_min) * 0.15

        x_min = df[cols["x"]].min()
        x_max = df[cols["x"]].max()
        x_padding = (x_max - x_min) * 0.1

        # Add quadrant labels
        text_color = 'rgba(255,255,255,0.5)' if is_dark_mode else 'rgba(0,0,0,0.3)'
        quadrant_labels = [
            dict(x=x_max * 0.7, y=y_max * 0.8, text="Høj Investering<br>Høj Besparelse", showarrow=False,
                 font=dict(size=10, color=text_color)),
            dict(x=x_max * 0.7, y=y_min * 0.8, text="Høj Investering<br>Lav Effekt", showarrow=False,
                 font=dict(size=10, color=text_color)),
        ]

        # Add trendline
        if len(df) > 2:
            z = np.polyfit(df[cols["x"]], df[cols["y"]], 1)
            x_trend = [df[cols["x"]].min(), df[cols["x"]].max()]
            y_trend = [z[0] * x + z[1] for x in x_trend]
            fig.add_trace(go.Scatter(
                x=x_trend, y=y_trend, mode='lines',
                line=dict(color='rgba(100,100,100,0.5)', dash='dot', width=2),
                name='Tendens', showlegend=True
            ))

        fig.update_layout(
            margin=dict(l=50, r=20, t=40, b=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", y=-0.2, title_text=""),
            annotations=quadrant_labels,
            yaxis=dict(
                range=[y_min - y_padding, y_max + y_padding],
                zeroline=True,
                zerolinecolor='gray',
                zerolinewidth=1
            ),
            xaxis=dict(
                range=[x_min - x_padding, x_max + x_padding],
                zeroline=True,
                zerolinecolor='gray',
                zerolinewidth=1
            )
        )
        return fig
    except Exception as e:
        print(f"Fejl i create_roi_matrix: {str(e)}")
        return px.scatter(title="Fejl ved indlæsning af ROI-data")

def create_building_characteristics(muni_key, is_dark_mode=False):
    try:
        with open('mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)

        cfg = mapping[muni_key]["building_data"]
        cols = cfg["columns"]

        file_path = os.path.join(mapping[muni_key]["folder"], cfg["file"])
        df = pd.read_excel(file_path, sheet_name=cfg["sheet"], skiprows=cfg["skiprows"])
        df[cols["age"]] = pd.to_numeric(df[cols["age"]], errors='coerce')
        df = df.dropna(subset=[cols["age"], cols["label"]])

        # Danish energy label colors (official standard)
        energy_colors = {
            "A2020": "#00a651",  # Dark green
            "A2015": "#00a651",  # Dark green
            "A2010": "#00a651",  # Dark green
            "B": "#50b848",      # Light green
            "C": "#b5d333",      # Yellow-green
            "D": "#fff200",      # Yellow
            "E": "#f7941d",      # Orange
            "F": "#ed1c24",      # Red
            "G": "#be1e2d"       # Dark red
        }

        fig = px.histogram(
            df,
            x=cols["age"],
            color=cols["label"],
            category_orders={cols["label"]: ["A2020", "A2015", "A2010", "B", "C", "D", "E", "F", "G"]},
            color_discrete_map=energy_colors,
            labels={cols["age"]: "Opførelsesår", cols["label"]: "Energimærke"},
            template="plotly_dark" if is_dark_mode else "plotly_white",
            barmode="stack",
            nbins=30
        )

        fig.update_layout(
            margin=dict(l=50, r=20, t=40, b=50),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Opførelsesår",
            yaxis_title="Antal Bygninger",
            legend_title_text="Energimærke",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5
            )
        )
        return fig
    except Exception as e:
        print(f"Fejl i create_building_characteristics: {str(e)}")
        return px.scatter(title="Fejl ved indlæsning af bygningsdata")
    



def create_randers_map(is_dark_mode=False):
    try:
        from folium.plugins import MarkerCluster

        with open('randers_processed.json', 'r', encoding='utf-8') as f:
            data = json.load(f).get("map_points", [])

        # Center map on Randers city center
        m = folium.Map(
            location=[56.4607, 10.0364],
            zoom_start=12,
            tiles="cartodbpositron" if not is_dark_mode else "cartodbdark_matter"
        )

        # Create marker cluster for better performance
        marker_cluster = MarkerCluster(
            name="Bygninger",
            options={
                'spiderfyOnMaxZoom': True,
                'showCoverageOnHover': False,
                'maxClusterRadius': 50
            }
        ).add_to(m)

        # Track unique statuses for legend
        status_colors = {}

        for p in data:
            # Store status-color mapping for legend
            if p.get('status') and p.get('color'):
                status_colors[p['status']] = p['color']

            # Add marker with tooltip (hover) and popup (click)
            folium.CircleMarker(
                location=[p['lat'], p['lon']],
                radius=8,
                tooltip=f"<b>{p['name']}</b>",  # Shows on hover
                popup=folium.Popup(
                    f"<b>{p['name']}</b><br>{p['address']}<br>Status: {p['status']}",
                    max_width=300
                ),
                color=p['color'],
                fill=True,
                fill_color=p['color'],
                fill_opacity=0.7,
                weight=2
            ).add_to(marker_cluster)

        # Add legend
        if status_colors:
            legend_html = '''
            <div style="position: fixed; bottom: 30px; left: 30px; z-index: 1000;
                        background-color: white; padding: 10px 15px; border-radius: 8px;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.3); font-size: 12px;">
                <b style="font-size: 13px;">Status</b><br>
            '''
            for status, color in status_colors.items():
                legend_html += f'''
                <div style="margin-top: 5px;">
                    <span style="display: inline-block; width: 12px; height: 12px;
                                 background-color: {color}; border-radius: 50%;
                                 margin-right: 6px; vertical-align: middle;"></span>
                    {status}
                </div>
                '''
            legend_html += '</div>'
            m.get_root().html.add_child(folium.Element(legend_html))

        return m._repr_html_()  # Returns the HTML for the Dash Iframe
    except:
        return "<h3>Kort kunne ikke indlæses. Kør venligst datasync.</h3>"
    


# ============ Faaborg-Midtfyn =============


def create_faaborg_energy_performance(muni_key, is_dark_mode=False, selected_address=None):
    try:
        with open('mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        cfg = mapping[muni_key]["db2_energy"]
        file_path = os.path.join(mapping[muni_key]["folder"], cfg["file"])

        # Headers are on row 0, no skiprows needed
        df_ov = pd.read_excel(file_path, sheet_name='Energi Oversigt')
        df_ov.columns = [str(c).strip() for c in df_ov.columns]
        addr_col = df_ov.columns[0]
        df_ov[addr_col] = df_ov[addr_col].ffill()

        perf_col = next((c for c in df_ov.columns if "Forskel" in c or "Afvigelse" in c), df_ov.columns[-1])

        # This is the critical line: Remove anything that isn't a real address
        df_all = df_ov.copy()
        df_all[addr_col] = df_all[addr_col].astype(str).str.strip()
        df_all = df_all[
            (df_all[addr_col] != "") & 
            (df_all[addr_col] != "nan") & 
            (~df_all[addr_col].str.contains("Total|Sum|Kontrol|Forside", case=False))
        ].dropna(subset=[perf_col])

        # Sort and reset index to ensure Plotly maps 0 to N correctly
        df_all = df_all.sort_values(by=perf_col, ascending=True).reset_index(drop=True)

        # 2. CALIBRATED HEIGHT
        # A bit more height per bar (35px) makes the names easier to read and ensures all bars fit
        dynamic_height = max(len(df_all) * 35, 400) 

        fig_bar = px.bar(
            df_all, 
            x=perf_col, 
            y=addr_col, 
            orientation='h',
            color=perf_col,
            color_continuous_scale='RdYlGn_r',
            template="plotly_dark" if is_dark_mode else "plotly_white"
        )

        # 3. THE "SNAP" LAYOUT
        fig_bar.update_layout(
            height=dynamic_height,
            # t=5 (tiny gap), b=50 (room for the last axis label)
            margin=dict(l=220, r=20, t=5, b=50),
            yaxis={
                'type': 'category',
                'dtick': 1,
                'title': "",
                # Reversed range: first item (index 0) at TOP, last item at BOTTOM
                'range': [len(df_all) - 0.5, -0.5],
                'automargin': True
            },
            xaxis={
                'side': 'top',
                'title': "Afvigelse (%)",
                'gridcolor': 'rgba(0,0,0,0.1)'
            },
            showlegend=False,
            coloraxis_showscale=False
        )

        # Add vertical line at x=0 to separate positive/negative deviation
        fig_bar.add_vline(x=0, line_dash="solid", line_color="rgba(100,100,100,0.8)", line_width=2)

        fig_bar.update_traces(
            hovertemplate="<b>%{y}</b><br>Afvigelse: %{x:.2f}%<extra></extra>"
        )

        # 2. BUILD DUAL-LINE CHART: Actual vs Target Consumption
        if not selected_address:
            selected_address = str(df_all.iloc[-1][addr_col])

        fig_detail = go.Figure()

        # Try to get target from Energi Oversigt (Energimærke kWh pr m2)
        selected_base = extract_address_base(selected_address)
        df_ov['_base'] = df_ov[addr_col].apply(lambda x: extract_address_base(str(x)))
        addr_row = df_ov[df_ov['_base'] == selected_base]

        target_from_overview = None
        if not addr_row.empty:
            # Look for Energimærke kWh pr m2 column (flexible matching for encoding)
            target_col = None
            for c in df_ov.columns:
                c_lower = str(c).lower()
                # Match "Energimærke kWh pr m2" but not "beregnede" columns
                if ('energi' in c_lower and 'kwh' in c_lower and 'pr m2' in c_lower.replace('.', ' ')
                    and 'beregn' not in c_lower and 'forbrug' not in c_lower):
                    target_col = c
                    break
            if target_col:
                target_from_overview = pd.to_numeric(addr_row.iloc[0][target_col], errors='coerce')

        # Use existing data processing functions to get trend data
        try:
            # Get mapping of addresses to their individual sheets
            sheet_map = get_faaborg_sheet_map(file_path)

            # Find the matching sheet for selected address
            matched_sheet = None

            for addr, sheet in sheet_map.items():
                if extract_address_base(addr) == selected_base:
                    matched_sheet = sheet
                    break

            if matched_sheet:
                # Extract trend data from the individual address sheet
                years, actual_values, target_values = extract_trend_data(file_path, matched_sheet)

                if years and actual_values:
                    # Add actual consumption line (Graddagskorrigeret)
                    fig_detail.add_trace(go.Scatter(
                        x=years,
                        y=actual_values,
                        mode='lines+markers',
                        name='Faktisk Forbrug (Graddagskorr.)',
                        line=dict(color='#3b82f6', width=3),
                        marker=dict(size=10),
                        hovertemplate='%{x}: %{y:.1f} kWh<extra></extra>'
                    ))

                    # Use target from sheet if available, else fall back to Energi Oversigt
                    has_target = False
                    gap_text = ""
                    gap_color = "#666"

                    if target_values:
                        # Target from individual sheet (varies by year)
                        fig_detail.add_trace(go.Scatter(
                            x=years,
                            y=target_values,
                            mode='lines+markers',
                            name='Energimærke (Mål)',
                            line=dict(color='#10b981', width=2, dash='dash'),
                            marker=dict(size=6),
                            hovertemplate='Mål %{x}: %{y:.1f} kWh<extra></extra>'
                        ))

                        # Add shaded gap area
                        fig_detail.add_trace(go.Scatter(
                            x=years + years[::-1],
                            y=actual_values + target_values[::-1],
                            fill='toself',
                            fillcolor='rgba(239, 68, 68, 0.2)',
                            line=dict(color='rgba(0,0,0,0)'),
                            name='Ineffektivitets-gap',
                            hoverinfo='skip',
                            showlegend=True
                        ))

                        avg_gap = np.mean([a - t for a, t in zip(actual_values, target_values)])
                        gap_text = f"Gns. afvigelse: {avg_gap:+.1f} kWh"
                        gap_color = "#ef4444" if avg_gap > 0 else "#10b981"
                        has_target = True

                    elif target_from_overview and pd.notna(target_from_overview):
                        # Fall back to horizontal target line from Energi Oversigt
                        target_line = [target_from_overview] * len(years)

                        fig_detail.add_trace(go.Scatter(
                            x=years,
                            y=target_line,
                            mode='lines',
                            name=f'Energimærke ({target_from_overview:.0f} kWh/m²)',
                            line=dict(color='#10b981', width=2, dash='dash'),
                            hovertemplate='Mål: %{y:.1f} kWh/m²<extra></extra>'
                        ))

                        # Add shaded gap area
                        fig_detail.add_trace(go.Scatter(
                            x=years + years[::-1],
                            y=actual_values + target_line[::-1],
                            fill='toself',
                            fillcolor='rgba(239, 68, 68, 0.2)',
                            line=dict(color='rgba(0,0,0,0)'),
                            name='Ineffektivitets-gap',
                            hoverinfo='skip',
                            showlegend=True
                        ))

                        avg_gap = np.mean([a - target_from_overview for a in actual_values])
                        gap_text = f"Gns. afvigelse: {avg_gap:+.1f} kWh"
                        gap_color = "#ef4444" if avg_gap > 0 else "#10b981"
                        has_target = True

                    fig_detail.update_layout(
                        title=dict(text=f"Forbrugsudvikling: {selected_address}", font=dict(size=14)),
                        template="plotly_dark" if is_dark_mode else "plotly_white",
                        xaxis_title="År",
                        yaxis_title="kWh (Graddagskorrigeret)",
                        legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
                        margin=dict(t=80, b=80),
                        hovermode='x unified',
                        annotations=[
                            dict(
                                text=gap_text,
                                xref="paper", yref="paper",
                                x=0.5, y=1.06,
                                showarrow=False,
                                font=dict(size=12, color=gap_color),
                                xanchor="center"
                            )
                        ] if gap_text else []
                    )
                else:
                    # Fall back to Energi Oversigt if individual sheet has no data
                    years, actual_values = extract_from_energi_oversigt(df_ov, addr_row, selected_address)
                    if years and actual_values:
                        build_trend_chart_from_data(fig_detail, years, actual_values, target_from_overview, selected_address, is_dark_mode)
                    else:
                        fig_detail.add_annotation(text=f"Ingen forbrugsdata for:<br>{selected_address}", showarrow=False)
                        fig_detail.update_layout(template="plotly_dark" if is_dark_mode else "plotly_white")
            else:
                # No matching sheet found, try Energi Oversigt directly
                years, actual_values = extract_from_energi_oversigt(df_ov, addr_row, selected_address)
                if years and actual_values:
                    build_trend_chart_from_data(fig_detail, years, actual_values, target_from_overview, selected_address, is_dark_mode)
                else:
                    fig_detail.add_annotation(text=f"Ingen data for:<br>{selected_address}", showarrow=False)
                    fig_detail.update_layout(template="plotly_dark" if is_dark_mode else "plotly_white")

        except Exception as detail_err:
            print(f"Detail chart error: {detail_err}")
            fig_detail.add_annotation(text=f"Fejl ved indlæsning:<br>{str(detail_err)[:50]}", showarrow=False)
            fig_detail.update_layout(template="plotly_dark" if is_dark_mode else "plotly_white")

        return fig_bar, fig_detail

    except Exception as e:
        print(f"Error: {e}")
        return go.Figure(), go.Figure()
        


def create_faaborg_procurement_gap(muni_key, is_dark_mode=False):
    try:
        with open('mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        cfg = mapping[muni_key]["db5_procurement"]
        file_path = os.path.join(mapping[muni_key]["folder"], cfg["file"])

        # Load with no skips as the headers are at the top
        df = pd.read_excel(file_path, sheet_name="Priskatalog")

        # Force column names to be clean (no spaces)
        df.columns = [str(c).strip() for c in df.columns]

        # Use the EXACT names from your terminal: 'Pris1' and 'Pris3'
        col_std = 'Pris1'
        col_bulk = 'Pris3'

        if col_std not in df.columns:
            return px.scatter(title=f"Fejl: Fandt ikke {col_std}")

        # Convert to numeric
        df[col_std] = pd.to_numeric(df[col_std], errors='coerce').fillna(0)
        df[col_bulk] = pd.to_numeric(df[col_bulk], errors='coerce').fillna(0)

        std_sum = df[col_std].sum()
        bulk_sum = df[col_bulk].sum()
        savings = std_sum - bulk_sum
        savings_pct = (savings / std_sum * 100) if std_sum > 0 else 0

        # Create waterfall chart for better savings visualization
        fig = go.Figure(go.Waterfall(
            name="Budget",
            orientation="v",
            measure=["absolute", "relative", "total"],
            x=["Standard Pris", "Besparelse", "Udbuds Pris"],
            y=[std_sum, -savings, bulk_sum],
            text=[f"{std_sum:,.0f} DKK", f"-{savings:,.0f} DKK", f"{bulk_sum:,.0f} DKK"],
            textposition="outside",
            connector={"line": {"color": "rgba(100,100,100,0.4)"}},
            decreasing={"marker": {"color": "#10b981"}},  # Green for savings
            increasing={"marker": {"color": "#ef4444"}},
            totals={"marker": {"color": "#3b82f6"}}
        ))

        fig.update_layout(
            title=dict(
                text=f"Besparelse: {savings:,.0f} DKK ({savings_pct:.1f}%)",
                font=dict(size=16)
            ),
            template="plotly_dark" if is_dark_mode else "plotly_white",
            showlegend=False,
            yaxis_title="DKK",
            margin=dict(t=80)
        )
        return fig
    except Exception as e:
        return px.scatter(title=f"DB5 Fejl: {str(e)}")


def create_faaborg_ventilation_peaks(muni_key, is_dark_mode=False):
    try:
        with open('mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        cfg = mapping[muni_key]["db6_ventilation"]
        file_path = os.path.join(mapping[muni_key]["folder"], cfg["file"])

        xl = pd.ExcelFile(file_path)
        all_dates = []

        # Loop through 60+ sheets
        for sheet in xl.sheet_names:
            if sheet in ["NY", "Skabelon", "Forside"]:
                continue
            temp_df = pd.read_excel(file_path, sheet_name=sheet)
            if 'Dato for filterskifte' in temp_df.columns:
                all_dates.extend(temp_df['Dato for filterskifte'].dropna().tolist())

        df_dates = pd.DataFrame(all_dates, columns=['Dato'])
        df_dates['Dato'] = pd.to_datetime(df_dates['Dato'], errors='coerce')
        df_dates = df_dates.dropna(subset=['Dato'])
        df_dates['MånedNr'] = df_dates['Dato'].dt.month

        # Danish month names in chronological order
        danish_months = {
            1: 'Januar', 2: 'Februar', 3: 'Marts', 4: 'April',
            5: 'Maj', 6: 'Juni', 7: 'Juli', 8: 'August',
            9: 'September', 10: 'Oktober', 11: 'November', 12: 'December'
        }
        df_dates['Måned'] = df_dates['MånedNr'].map(danish_months)

        # Count per month and ensure all months are present
        month_counts = df_dates.groupby('MånedNr').size().reindex(range(1, 13), fill_value=0)
        month_labels = [danish_months[i] for i in range(1, 13)]

        # Calculate average for reference line
        avg_count = month_counts.mean()

        # Create area chart with gradient coloring based on intensity
        colors = ['#10b981' if v <= avg_count else '#f59e0b' if v <= avg_count * 1.5 else '#ef4444'
                  for v in month_counts.values]

        fig = go.Figure()

        # Add area fill
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=month_counts.values,
            fill='tozeroy',
            mode='lines+markers',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=10, color=colors, line=dict(color='white', width=2)),
            fillcolor='rgba(59, 130, 246, 0.2)',
            name='Filterskift',
            hovertemplate='<b>%{x}</b><br>Antal: %{y}<extra></extra>'
        ))

        # Add average line
        fig.add_hline(
            y=avg_count,
            line_dash="dash",
            line_color="#94a3b8",
            annotation_text=f"Gennemsnit: {avg_count:.1f}",
            annotation_position="right"
        )

        # Find peak month
        peak_month_idx = month_counts.idxmax()
        peak_month_name = danish_months[peak_month_idx]
        peak_count = month_counts.max()

        fig.update_layout(
            title=dict(
                text=f"Sæsonudsving i Vedligehold (Peak: {peak_month_name})",
                font=dict(size=16)
            ),
            template="plotly_dark" if is_dark_mode else "plotly_white",
            xaxis_title="Måned",
            yaxis_title="Antal Filterskift",
            showlegend=False,
            margin=dict(t=60, r=80),
            xaxis=dict(tickangle=-45)
        )
        return fig
    except Exception as e:
        return px.scatter(title=f"DB6 Fejl: {e}")