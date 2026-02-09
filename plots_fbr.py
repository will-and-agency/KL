import pandas as pd
import numpy as np
import plotly.express as px
import json
import os
import traceback
import plotly.graph_objects as go
from data_processing_fbr import *
from plotly.subplots import make_subplots


## Dashboard 1
def create_frb_maintenance_budget(is_dark_mode=False):
    try:
        with open('frb_processed.json', 'r', encoding='utf-8') as f:
            data = json.load(f)["maintenance"]

        df = pd.DataFrame(data)
        if df.empty:
            return go.Figure().add_annotation(text="Ingen data fundet. Kør Sync.", showarrow=False)

        # Tjek om 'Category' findes, ellers brug 'Condition' som fallback til farve
        color_col = "Category" if "Category" in df.columns else "Condition"

        # Calculate total budget
        total_budget = df['Cost'].sum()

        # Calculate yearly totals for cumulative line
        yearly_totals = df.groupby('Year')['Cost'].sum().sort_index()
        cumulative = yearly_totals.cumsum()

        fig = px.bar(
            df, x="Year", y="Cost", color=color_col,
            title="Vedligeholdelsesplan (10 år)",
            labels={"Cost": "Budget (DKK)", "Year": "År", "Category": "Område"},
            template="plotly_dark" if is_dark_mode else "plotly_white",
            barmode="stack"
        )

        # Remove gap lines between stacked segments
        fig.update_traces(marker_line_width=0, selector=dict(type="bar"))

        # Add cumulative line
        fig.add_trace(go.Scatter(
            x=cumulative.index,
            y=cumulative.values,
            mode='lines+markers',
            name='Kumulativ',
            line=dict(color='#3b82f6', width=3, dash='dot'),
            marker=dict(size=8),
            yaxis='y2'
        ))

        fig.update_xaxes(type='category', categoryorder='category ascending')

        # Format y-axis and add secondary axis for cumulative
        fig.update_layout(
            yaxis=dict(
                title="Årligt Budget (DKK)",
                tickformat=",.0f",
                ticksuffix=" DKK"
            ),
            yaxis2=dict(
                title="Kumulativ (DKK)",
                overlaying='y',
                side='right',
                tickformat=",.0f",
                showgrid=False
            ),
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
            margin=dict(t=80, b=80),
            # Add total budget annotation
            annotations=[
                dict(
                    text=f"Total: {total_budget:,.0f} DKK",
                    xref="paper", yref="paper",
                    x=0.5, y=1.06,
                    showarrow=False,
                    font=dict(size=14, color="#10b981"),
                    xanchor="center"
                )
            ]
        )
        return fig
    except Exception as e:
        return go.Figure().add_annotation(text=f"Fejl i D1: {str(e)}", showarrow=False)

## Dashboard 2
def create_frb_project_scatter(is_dark_mode=False):
    with open('frb_processed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)["projects"]
    df = pd.DataFrame(data)

    if df.empty:
        return go.Figure().add_annotation(text="Ingen projektdata fundet", showarrow=False)

    # Calculate medians for reference lines
    median_ddk = df['DDK'].median()
    median_co2 = df['CO2'].median()

    fig = px.scatter(
        df, x="DDK", y="CO2", color="Type",
        hover_name="Description",
        title="DKK vs CO2 Reduktion per Projekt",
        labels={"DDK": "Investering (DKK)", "CO2": "CO2 Reduktion (Tons/år)"},
        template="plotly_dark" if is_dark_mode else "plotly_white"
    )

    fig.update_traces(marker=dict(size=14, opacity=0.8, line=dict(width=1, color='white')))

    # Add median reference lines
    fig.add_hline(y=median_co2, line_dash="dash", line_color="rgba(100,100,100,0.5)",
                  annotation_text=f"Median CO2: {median_co2:.1f}", annotation_position="right")
    fig.add_vline(x=median_ddk, line_dash="dash", line_color="rgba(100,100,100,0.5)",
                  annotation_text=f"Median DKK: {median_ddk:,.0f}", annotation_position="top")

    # Add quadrant labels
    text_color = 'rgba(255,255,255,0.4)' if is_dark_mode else 'rgba(0,0,0,0.2)'
    x_max = df['DDK'].max()
    y_max = df['CO2'].max()

    fig.update_layout(
        margin=dict(t=80, b=50, l=60, r=60),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        annotations=[
            dict(x=x_max * 0.15, y=y_max * 0.85, text="Lav Investering<br>Høj CO2 ✓",
                 showarrow=False, font=dict(size=10, color="#10b981")),
            dict(x=x_max * 0.85, y=y_max * 0.85, text="Høj Investering<br>Høj CO2",
                 showarrow=False, font=dict(size=10, color=text_color)),
            dict(x=x_max * 0.15, y=y_max * 0.15, text="Lav Investering<br>Lav CO2",
                 showarrow=False, font=dict(size=10, color=text_color)),
            dict(x=x_max * 0.85, y=y_max * 0.15, text="Høj Investering<br>Lav CO2 ✗",
                 showarrow=False, font=dict(size=10, color="#ef4444"))
        ]
    )

    # Add trendline
    if len(df) > 2:
        z = np.polyfit(df['DDK'], df['CO2'], 1)
        x_trend = [df['DDK'].min(), df['DDK'].max()]
        y_trend = [z[0] * x + z[1] for x in x_trend]
        fig.add_trace(go.Scatter(
            x=x_trend, y=y_trend, mode='lines',
            line=dict(color='rgba(100,100,100,0.4)', dash='dot', width=2),
            name='Tendens', showlegend=True
        ))

    return fig

## Dashboard 3

def create_frb_property_characteristics(is_dark_mode=False):
    

    with open('frb_processed.json', 'r', encoding='utf-8') as f:
        data = json.load(f).get("compliance", [])

    df = pd.DataFrame(data)
    if df.empty:
        return go.Figure().add_annotation(text="Ingen data fundet. Kør Sync.", showarrow=False)

    # Filter out zero/invalid values
    df = df[(df['SavingPct'] > 0) & (df['Area'] > 0) & (df['Year'] > 1800)]

    if df.empty:
        return go.Figure().add_annotation(text="Ingen besparelsespotentiale fundet.", showarrow=False)

    template = "plotly_dark" if is_dark_mode else "plotly_white"

    # Create subplots: 1 row, 3 columns
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=("Areal (m²)", "Energimærke", "Byggeår"),
        horizontal_spacing=0.08
    )

    # --- Chart 1: Area (m²) vs Saving % ---
    # Create area bins for grouping
    df['AreaBin'] = pd.cut(df['Area'], bins=[0, 500, 1000, 2000, 5000, float('inf')],
                           labels=['<500', '500-1000', '1000-2000', '2000-5000', '>5000'])
    area_grouped = df.groupby('AreaBin', observed=True).agg({
        'SavingPct': 'mean',
        'Building': lambda x: list(x),
        'Area': 'count'
    }).reset_index()
    area_grouped.columns = ['AreaBin', 'SavingPct', 'Buildings', 'Count']

    # Create hover text with building names (max 5)
    area_hover = []
    for _, row in area_grouped.iterrows():
        buildings = row['Buildings'][:5]
        more = f"<br>+{len(row['Buildings']) - 5} flere..." if len(row['Buildings']) > 5 else ""
        area_hover.append(f"<b>Areal: {row['AreaBin']} m²</b><br>Gns. besparelse: {row['SavingPct']:.1f}%<br>Antal: {row['Count']}<br><br><b>Bygninger:</b><br>" + "<br>".join(buildings) + more)

    fig.add_trace(
        go.Bar(x=area_grouped['AreaBin'].astype(str), y=area_grouped['SavingPct'],
               marker_color='#3b82f6', name='m²',
               text=[f'{v:.1f}%' for v in area_grouped['SavingPct']], textposition='outside',
               hovertext=area_hover, hoverinfo='text'),
        row=1, col=1
    )

    # --- Chart 2: Energy Mark vs Saving % ---
    energy_order = ['A2020', 'A2015', 'A2010', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
    df['EnergyMark'] = pd.Categorical(df['EnergyMark'], categories=energy_order, ordered=True)
    energy_grouped = df.groupby('EnergyMark', observed=True).agg({
        'SavingPct': 'mean',
        'Building': lambda x: list(x),
        'Area': 'count'
    }).reset_index()
    energy_grouped.columns = ['EnergyMark', 'SavingPct', 'Buildings', 'Count']
    energy_grouped = energy_grouped.sort_values('EnergyMark')

    # Create hover text
    energy_hover = []
    for _, row in energy_grouped.iterrows():
        buildings = row['Buildings'][:5]
        more = f"<br>+{len(row['Buildings']) - 5} flere..." if len(row['Buildings']) > 5 else ""
        energy_hover.append(f"<b>Energimærke: {row['EnergyMark']}</b><br>Gns. besparelse: {row['SavingPct']:.1f}%<br>Antal: {row['Count']}<br><br><b>Bygninger:</b><br>" + "<br>".join(buildings) + more)

    # Color based on energy label (green=good, red=bad)
    energy_colors = {'A2020': '#00a651', 'A2015': '#00a651', 'A2010': '#00a651', 'A': '#00a651',
                     'B': '#50b848', 'C': '#b5d333', 'D': '#fff200', 'E': '#f7941d', 'F': '#ed1c24', 'G': '#be1e2d'}
    colors = [energy_colors.get(m, '#94a3b8') for m in energy_grouped['EnergyMark']]

    fig.add_trace(
        go.Bar(x=energy_grouped['EnergyMark'].astype(str), y=energy_grouped['SavingPct'],
               marker_color=colors, name='Energimærke',
               text=[f'{v:.1f}%' for v in energy_grouped['SavingPct']], textposition='outside',
               hovertext=energy_hover, hoverinfo='text'),
        row=1, col=2
    )

    # --- Chart 3: Year vs Saving % ---
    # Create decade bins
    df['Decade'] = (df['Year'] // 10) * 10
    year_grouped = df.groupby('Decade').agg({
        'SavingPct': 'mean',
        'Building': lambda x: list(x),
        'Area': 'count'
    }).reset_index()
    year_grouped.columns = ['Decade', 'SavingPct', 'Buildings', 'Count']
    year_grouped = year_grouped.sort_values('Decade')
    year_grouped['DecadeLabel'] = year_grouped['Decade'].astype(int).astype(str) + 's'

    # Create hover text
    year_hover = []
    for _, row in year_grouped.iterrows():
        buildings = row['Buildings'][:5]
        more = f"<br>+{len(row['Buildings']) - 5} flere..." if len(row['Buildings']) > 5 else ""
        year_hover.append(f"<b>Årti: {row['DecadeLabel']}</b><br>Gns. besparelse: {row['SavingPct']:.1f}%<br>Antal: {row['Count']}<br><br><b>Bygninger:</b><br>" + "<br>".join(buildings) + more)

    fig.add_trace(
        go.Bar(x=year_grouped['DecadeLabel'], y=year_grouped['SavingPct'],
               marker_color='#10b981', name='Byggeår',
               text=[f'{v:.1f}%' for v in year_grouped['SavingPct']], textposition='outside',
               hovertext=year_hover, hoverinfo='text'),
        row=1, col=3
    )

    # Update layout
    fig.update_layout(
        title=dict(text="Besparelsespotentiale (%) efter Bygningskarakteristika", font=dict(size=16)),
        template=template,
        showlegend=False,
        height=450,
        margin=dict(t=80, b=50, l=50, r=30)
    )

    # Update all y-axes
    fig.update_yaxes(title_text="Besparelse %", ticksuffix="%", row=1, col=1)
    fig.update_yaxes(ticksuffix="%", row=1, col=2)
    fig.update_yaxes(ticksuffix="%", row=1, col=3)

    # Update x-axes
    fig.update_xaxes(title_text="m²", row=1, col=1)
    fig.update_xaxes(title_text="Energimærke", row=1, col=2)
    fig.update_xaxes(title_text="År", row=1, col=3)

    return fig

### Dashboard 7

def create_frb_risk_heatmap(is_dark_mode=False):
    if not os.path.exists('frb_processed.json'):
        return go.Figure().add_annotation(text="JSON-fil mangler. Tryk på Sync.", showarrow=False)

    with open('frb_processed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)["maintenance"]

    df = pd.DataFrame(data)

    # CRITICAL: Prevent the 'Expected one of []' error
    if df.empty:
        return go.Figure().add_annotation(text="Ingen data fundet i JSON.<br>Tjek om Excel-formatet er korrekt.", showarrow=False)

    # Pivot the data
    pivot = df.pivot_table(index="Condition", columns="Year", values="Cost", aggfunc='sum').fillna(0)

    # Ensure full 2023-2033 timeline
    for y in range(2023, 2034):
        if y not in pivot.columns:
            pivot[y] = 0.0

    pivot = pivot.reindex(sorted(pivot.columns), axis=1).sort_index(ascending=False)

    # Calculate row and column totals
    row_totals = pivot.sum(axis=1)
    col_totals = pivot.sum(axis=0)
    total_budget = pivot.values.sum()

    # Find the highest risk cell
    max_val = pivot.values.max()
    max_idx = np.unravel_index(pivot.values.argmax(), pivot.values.shape)
    max_condition = pivot.index[max_idx[0]]
    max_year = pivot.columns[max_idx[1]]

    # Format text for cells
    def format_value(x):
        if x >= 1e6:
            return f"{x/1e6:.1f}M"
        elif x >= 1e3:
            return f"{x/1e3:.0f}k"
        elif x > 0:
            return f"{x:.0f}"
        return ""

    text_matrix = pivot.apply(lambda col: col.map(format_value))

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=pivot.columns,
        y=pivot.index,
        colorscale="YlOrRd",
        text=text_matrix.values,
        texttemplate="%{text}",
        textfont=dict(size=11),
        showscale=True,
        colorbar=dict(title="DKK", tickformat=",.0f"),
        hovertemplate="År: %{x}<br>Tilstand: %{y}<br>Budget: %{z:,.0f} DKK<extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=f"Vedligeholdelsesrisiko (Total: {total_budget/1e6:.1f}M DKK)",
            font=dict(size=16)
        ),
        xaxis=dict(title="År", tickmode='linear', dtick=1, side='bottom'),
        yaxis_title="Tilstandsgrad",
        template="plotly_dark" if is_dark_mode else "plotly_white",
        margin=dict(t=80, b=50, l=80, r=50),
        # Add annotation for highest risk
        annotations=[
            dict(
                text=f"Højeste risiko: {max_condition} i {max_year}",
                xref="paper", yref="paper",
                x=0.5, y=1.08,
                showarrow=False,
                font=dict(size=12, color="#ef4444"),
                xanchor="center"
            )
        ]
    )
    return fig



## Dashboard 8
def create_frb_roi_chart(is_dark_mode=False):
    # Load the JSON we processed earlier
    with open('frb_processed.json', 'r', encoding='utf-8') as f:
        data = json.load(f)["projects"]

    df = pd.DataFrame(data)

    if df.empty:
        return go.Figure().add_annotation(text="Ingen projektdata fundet", showarrow=False)

    # Calculate metrics for insights
    avg_tbt = df['TBT'].mean()
    avg_co2 = df['CO2'].mean()

    # Count quick wins (low TBT, high CO2)
    quick_wins = df[(df['TBT'] <= 10) & (df['CO2'] >= avg_co2)]
    num_quick_wins = len(quick_wins)

    # We match the names from your JSON: 'TBT', 'CO2', 'DDK'
    fig = px.scatter(
        df,
        x="TBT",
        y="CO2",
        size="DDK",
        size_max=40,
        color="Type",
        hover_name="Description",
        title="Strategisk ROI: Tilbagebetaling vs CO2 Gevinst",
        labels={
            "TBT": "Tilbagebetalingstid (År)",
            "CO2": "Tons CO2 sparet/år",
            "DDK": "Investering (DKK)"
        },
        template="plotly_dark" if is_dark_mode else "plotly_white"
    )

    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color='white')))

    # Highlight the "Quick Wins" area (Low TBT, High CO2)
    fig.add_vrect(
        x0=0, x1=10,
        fillcolor="rgba(16, 185, 129, 0.1)",
        line_width=0,
        annotation_text="",
    )

    # Add average reference lines
    fig.add_hline(
        y=avg_co2,
        line_dash="dash",
        line_color="rgba(100,100,100,0.5)",
        annotation_text=f"Gns. CO2: {avg_co2:.1f}",
        annotation_position="right"
    )
    fig.add_vline(
        x=avg_tbt,
        line_dash="dash",
        line_color="rgba(100,100,100,0.5)",
        annotation_text=f"Gns. TBT: {avg_tbt:.1f} år",
        annotation_position="top"
    )

    # Add quadrant annotations
    y_max = df['CO2'].max()
    x_max = df['TBT'].max()

    fig.update_layout(
        margin=dict(t=100, b=60, l=60, r=60),
        legend=dict(orientation="h", y=-0.18, x=0.5, xanchor="center"),
        annotations=[
            # Quick wins label
            dict(
                x=5, y=y_max * 0.9,
                text=f"<b>Quick Wins</b><br>{num_quick_wins} projekter",
                showarrow=False,
                font=dict(size=12, color="#10b981"),
                bgcolor="rgba(16, 185, 129, 0.15)",
                borderpad=6
            ),
            # Low priority label
            dict(
                x=x_max * 0.85, y=y_max * 0.1,
                text="Lav Prioritet",
                showarrow=False,
                font=dict(size=10, color="#ef4444")
            )
        ]
    )

    return fig