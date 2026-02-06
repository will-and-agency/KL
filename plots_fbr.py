import pandas as pd
import numpy as np
import plotly.express as px
import json
import os
import traceback
import plotly.graph_objects as go
from data_processing_fbr import *


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
        title="DDK vs CO2 Reduktion per Projekt",
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

    # Filtering out zero values to see where the real potential is
    df_filtered = df[df['SavingPct'] > 0]

    if df_filtered.empty:
        return go.Figure().add_annotation(text="Ingen besparelsespotentiale fundet.", showarrow=False)

    # Group by Year for the X-axis
    df_plot = df_filtered.groupby('Year')['SavingPct'].mean().reset_index()
    df_plot = df_plot.sort_values('Year')

    # Calculate average and find peak year
    avg_saving = df_plot['SavingPct'].mean()
    peak_year = df_plot.loc[df_plot['SavingPct'].idxmax(), 'Year']
    peak_value = df_plot['SavingPct'].max()

    fig = px.bar(
        df_plot, x="Year", y="SavingPct",
        title=f"Besparelsespotentiale pr. Byggeår (Højest: {int(peak_year)})",
        labels={"SavingPct": "Gns. Besparelse %", "Year": "Opførelsesår"},
        template="plotly_dark" if is_dark_mode else "plotly_white",
        color="SavingPct",
        color_continuous_scale="RdYlGn",  # Red-Yellow-Green makes more sense for savings
        text_auto='.1f'
    )

    # Add average line
    fig.add_hline(
        y=avg_saving,
        line_dash="dash",
        line_color="#3b82f6",
        annotation_text=f"Gennemsnit: {avg_saving:.1f}%",
        annotation_position="right"
    )

    fig.update_traces(textposition='outside', texttemplate='%{y:.1f}%')

    fig.update_layout(
        yaxis_ticksuffix="%",
        margin=dict(t=80, b=50, l=50, r=80),
        coloraxis_showscale=False,
        xaxis=dict(type='category', categoryorder='category ascending')
    )
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