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


def find_matching_domutech_rows(df_domu, selected_address, addr_column='Kolonne1'):
    """
    Find rows in Domutech data that match the selected address.
    Uses base address matching (street + number) for flexible matching.
    """
    selected_base = extract_address_base(selected_address)

    # Create a column with base addresses for matching
    domu_bases = df_domu[addr_column].apply(extract_address_base)

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

        df_ov = pd.read_excel(file_path, sheet_name='Energi Oversigt', skiprows=4)
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

        # 2. LOAD DOMUTECH FOR DETAILS
        df_domu = pd.read_excel(file_path, sheet_name='Beregnede forbrug Domutech')
        df_domu.columns = [str(c).strip() for c in df_domu.columns]

        if not selected_address:
            selected_address = str(df_all.iloc[-1][addr_col])

        # Use flexible base-address matching (street + number)
        b_data = find_matching_domutech_rows(df_domu, selected_address, addr_column='Kolonne1')
        
        fig_detail = go.Figure()
        if not b_data.empty:
            # Calculate total CO2
            total_co2 = b_data['Yearly CO2Emission [ton]'].sum()

            fig_detail = px.bar(
                b_data,
                x='Material',
                y='Yearly CO2Emission [ton]',
                color='Material',
                title=f"CO2 Kilde: {selected_address}",
                template="plotly_dark" if is_dark_mode else "plotly_white",
                text_auto='.2f'
            )

            # Hide legend (materials already shown on x-axis)
            fig_detail.update_layout(
                showlegend=False,
                margin=dict(t=80),
                # Add total CO2 as subtitle annotation
                annotations=[
                    dict(
                        text=f"Total: {total_co2:.2f} ton CO2/år",
                        xref="paper", yref="paper",
                        x=0.5, y=1.08,
                        showarrow=False,
                        font=dict(size=14, color="#10b981"),
                        xanchor="center"
                    )
                ]
            )
        else:
            fig_detail.add_annotation(text=f"Ingen audit-data for:<br>{selected_address}", showarrow=False)
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