import dash
from dash import dcc, html, Input, Output, State, clientside_callback
from plots import *
from data_processing import rearrange_carbon_data
from data_processing_fbr import *
from plots_fbr import *
from analysis_generator import *
from data_processing_randers import *


# Use high-reliability CDN links
external_scripts = [
    {"src": "https://cdn.tailwindcss.com?plugins=forms,typography"}
]
external_stylesheets = [
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    "https://fonts.googleapis.com/icon?family=Material+Icons+Round"
]

app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True
)

# Simplified index string - no inline JS to crash the renderer
app.index_string = '''
<!DOCTYPE html>
<html lang="da">
    <head>
        {%metas%}
        <title>KL Portal</title>
        {%favicon%}
        {%css%}
    </head>
    <body class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-slate-100 transition-colors duration-200">
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --- UI COMPONENTS ---

def create_sidebar():
    return html.Aside(
        id="sidebar",
        className="fixed inset-y-0 left-0 z-40 w-72 bg-sidebar-light dark:bg-sidebar-dark border-r border-slate-200 dark:border-slate-800 lg:static lg:block",
        children=[
            html.Div(className="p-6", children=[
                html.Div(className="flex items-center gap-2 mb-10", children=[
                    html.Span("analytics", className="material-icons-round text-primary text-3xl"),
                    html.H2("KL Portal", className="text-2xl font-bold tracking-tight uppercase")
                ]),
                
                html.Div(className="space-y-6", children=[
                    html.Div([
                        html.Label("Vælg kommune", className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 block"),
                        dcc.Dropdown(
                            id="muni-selector",
                            options=[
                                {"label": "Randers Kommune", "value": "randers"},
                                {"label": "Faaborg-Midtfyn Kommune", "value": "faaborg"},
                                {"label": "Frederiksberg Kommune", "value": "frederiksberg"}
                            ],
                            value="randers",
                            placeholder="Søg kommune...",
                            clearable=False,
                            searchable=True,
                            style={
                                "backgroundColor": "transparent",
                                "color": "#1e293b", # Dark text for visibility when box is open
                                "border": "none",
                            },
                            className="text-sm custom-dropdown"
                        )
                    ]),
                    
                    html.Nav(className="space-y-1", children=[
                        dcc.Link(
                            id="link-overblik",
                            href="/",
                            className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                            children=[
                                html.Span("dashboard", className="material-icons-round"),
                                html.Span("Overblik")
                            ]
                        ),
                        dcc.Link(
                            id="link-forklaring",
                            href="/forklaring",
                            className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                            children=[
                                html.Span("insights", className="material-icons-round"),
                                html.Span("Forklaring")
                            ]
                        ),
                    ])
                ])
            ]),
            
        ]
    )


# --- UPDATED APP LAYOUT ---
app.layout = html.Div(className="flex min-h-screen", children=[
    dcc.Location(id="url", refresh=False), # CRITICAL: This was missing
    create_sidebar(),
    
    # --- UPDATED HEADER IN APP.LAYOUT ---
    html.Main(className="flex-1 lg:p-8 p-4 bg-background-light dark:bg-background-dark min-h-screen", children=[
        # Main Header Area
        html.Div(className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4", children=[
            html.Div([
                html.H2(id="muni-header", className="text-3xl font-extrabold text-slate-800 dark:text-white uppercase tracking-tight")
            ]),
            
            # Action Buttons + Theme Toggle (Top Right)
            html.Div(className="flex items-center gap-3", children=[
                # NEW: Theme Toggle placed here
                html.Button(id="theme-toggle", className="p-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-600 dark:text-slate-300 shadow-sm hover:bg-slate-50 transition-colors", children=[
                    html.Span("dark_mode", className="material-icons-round block dark:hidden"),
                    html.Span("light_mode", className="material-icons-round hidden dark:block")
                ]),
                
                html.Button("Eksportér PDF", id="btn-pdf", className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium shadow-sm hover:bg-slate-50 transition-colors"),

                
                html.Button("Opdater Data (Sync JSON)", id="sync-button", className="px-4 py-2 bg-blue-500 text-white rounded")
            ])
        ]),
        
        # Grid for Dashboards
        html.Div(id="dashboard-content", className="flex flex-col gap-8 w-full pb-20"),
        
        # Hidden dummy outputs
        html.Div(id="dummy-output", style={"display": "none"})
    ])
])

# --- DANISH DASHBOARD CARD FACTORY ---
def make_card(title, desc, kpi1_label, kpi1_val, kpi2_label, kpi2_val, plot=None):
    return html.Div(className="bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col w-full mb-8", children=[
        # Overskrift
        html.Div(className="px-6 py-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center", children=[
            html.H3(title, className="font-bold text-slate-800 dark:text-slate-100 uppercase text-sm tracking-widest"),
            html.Span("analytics", className="material-icons-round text-primary text-lg")
        ]),
        
        # Indhold
        html.Div(className="p-8 flex flex-col lg:flex-row gap-8", children=[
            # Graf-område
            html.Div(className="w-full lg:w-3/4 h-[500px] bg-slate-50 dark:bg-slate-900 rounded-xl relative border border-slate-100 dark:border-slate-800", children=[
                plot if plot is not None else html.Div("Data indlæses...", className="flex items-center justify-center h-full text-slate-400")
            ]),
            
            # Info Sidebar
            html.Div(className="w-full lg:w-1/4 flex flex-col justify-between py-2", children=[
                html.Div([
                    html.Label("BESKRIVELSE", className="text-[10px] font-black text-slate-400 uppercase tracking-tighter mb-2 block"),
                    html.P(desc, className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-6"),
                ]),
                
                # KPI Blokke
                html.Div(className="grid grid-cols-1 gap-4 p-4 bg-slate-50 dark:bg-slate-700/30 rounded-lg", children=[
                    html.Div([
                        html.Span(kpi1_label, className="text-[10px] text-slate-400 uppercase font-bold block mb-1"),
                        html.Span(kpi1_val, className="font-bold text-xl text-slate-800 dark:text-white")
                    ]),
                    html.Div([
                        html.Span(kpi2_label, className="text-[10px] text-slate-400 uppercase font-bold block mb-1"),
                        html.Span(kpi2_val, className="font-bold text-xl text-emerald-500")
                    ])
                ])
            ])
        ])
    ])

# --- DANISH CALLBACK ---
@app.callback(
    [Output("muni-header", "children"), 
     Output("dashboard-content", "children")],
    [Input("url", "pathname"), 
     Input("muni-selector", "value"),
     Input("dummy-output", "children")]
)
def update_dynamic_content(pathname, muni_value, theme_trigger):
    # Standard header formatting
    header_text = f"{muni_value.replace('-', ' ')} KOMMUNE".upper()
    
    # Global check for the Analysis page
    if pathname == "/forklaring":
        if muni_value == "randers":
            return header_text, get_randers_analysis()
        elif muni_value == "faaborg":
            return header_text, get_faaborg_analysis()
        elif muni_value == "frederiksberg":
            return header_text, get_frederiksberg_analysis()
        else:
            return header_text, html.Div("Analyse for denne kommune er under udarbejdelse...", className="p-10 text-slate-500 text-center")


    # --- MODE 1: RANDERS ---
    if muni_value == "randers":
        # Generate Randers specific figures
        fig_roi = create_roi_matrix(muni_value)
        fig_char = create_building_characteristics(muni_value)

        map_html = create_randers_map()

        return header_text, [
            make_card(
                "ROI Matrix: Strategisk Prioritering", 
                "Prioritering af energiprojekter baseret på CO2-besparelse og investering. Scroll for at zoome i data.", 
                "KOMMUNE", "RANDERS", 
                "STATUS", "VERIFICERET", 
                plot=dcc.Graph(
                    id={'type': 'dynamic-graph', 'index': 1},
                    figure=fig_roi, 
                    config={'displayModeBar': True, 'scrollZoom': True, 'responsive': True},
                    style={'height': '100%', 'width': '100%'}
                )
            ),
            make_card(
                "Bygningsmasse: Karakteristika", 
                "Fordeling af ejendomme baseret på opførelsesår og energimærke.", 
                "BYGNINGER", "TOTAL OVERSIGT", 
                "ANALYSE", "KLAR", 
                plot=dcc.Graph(
                    id={'type': 'dynamic-graph', 'index': 2},
                    figure=fig_char, 
                    config={'displayModeBar': True, 'scrollZoom': True, 'responsive': True},
                    style={'height': '100%', 'width': '100%'}
                )
            ),

            make_card(
                "Ventilation Status Kort", 
                "Geografisk overblik over kritiske fejl og vedligeholdelsesbehov fra Timesafe data.", 
                "KILDE", "TIMESAFE", 
                "REGION", "RANDERS", 
                plot=html.Iframe(
                    id="randers-ventilation-map",
                    srcDoc=map_html,
                    style={
                        "width": "100%", 
                        "height": "500px", # Matches the height of your other graphs
                        "border": "none",
                        "border-radius": "8px"
                    }
                )
            )
            
        ]

    # --- MODE 2: FAABORG-MIDTFYN ---
    elif muni_value == "faaborg":
        
        res2 = create_faaborg_energy_performance(muni_value)
        fig2_bar, fig2_detail = res2

        fig5 = create_faaborg_procurement_gap(muni_value)
        fig6 = create_faaborg_ventilation_peaks(muni_value)

        building_list = []
        if fig2_bar and hasattr(fig2_bar, 'data') and len(fig2_bar.data) > 0:
            building_list = list(fig2_bar.data[0].y)

        # 3. Build UI
        if not building_list:
            db2_display = html.Div("Ingen data fundet i 'Beregnede forbrug Domutech' arket.", className="p-10 text-red-500")
        else:
            db2_display = html.Div([
                # Dropdown
                html.Div(className="mb-4", children=[
                    html.Label("Vælg Adresse:", className="text-xs font-bold text-gray-500 mb-2 block"),
                    dcc.Dropdown(
                        id="address-selector",
                        options=[{"label": str(addr), "value": str(addr)} for addr in building_list],
                        value=building_list[0] if building_list else None,
                        className="w-full"
                    ),
                ]),

                # Split View
                html.Div(className="flex flex-col lg:flex-row gap-4", children=[
                    # LEFT SIDE: The Scrollable Container
                    html.Div(
                        style={
                            'flex': '1', 
                            'height': '650px', 
                            'overflow-y': 'auto', # Changed to auto for better scrollbar behavior
                            'border': '1px solid #e2e8f0', 
                            'border-radius': '8px',
                            'padding': '0px', # Ensure no internal padding shifts the chart
                            'display': 'block'
                        }, 
                        children=[
                            dcc.Graph(
                                id="db2-bar-chart", 
                                figure=fig2_bar, 
                                config={'displayModeBar': False},
                                # Remove any default style padding/margin from the Graph object itself
                                style={'margin': '0', 'padding': '0'} 
                            )
                        ]
                    ),
                    
                    # RIGHT SIDE: Fixed Breakdown
                    html.Div(
                        style={
                            'flex': '1', 
                            'height': '600px', 
                            'border': '1px solid #e2e8f0', 
                            'border-radius': '8px'
                        }, 
                        children=[
                            dcc.Graph(id="db2-trend-graph", figure=fig2_detail)
                        ]
                    )
                ])
            ])


        return header_text, [
            make_card(
                "Forbrug & Bæredygtighed", 
                "Sammenligning af faktiske regninger mod energimærker. Det røde område viser 'skjulte omkostninger'.", 
                "ADRESSER", "170+", 
                "STATUS", "KLAR", 
                plot=db2_display # PASS THE COMBINED DIV HERE
            ),
            make_card(
                "Indkøb & Prisfølsomhed", 
                "Visualisering af besparelsespotentialet ved at samle vedligeholdelsesopgaver i 'Bulk' ordrer (Pris 1 vs Pris 3).",
                "POTENTIALE", "HØJT", "STRATEGI", "INDLYSENDE",
                plot=dcc.Graph(figure=fig5, style={'height': '500px'})
            ),
            make_card(
                "Vedligeholdelses-Peak (Sæson)", 
                "Histogram over hvornår filtre skiftes på tværs af 60 lokationer. Bruges til at undgå 'burnout' i Team 6.",
                "PEAK MÅNED", "JANUAR", "ENHEDER", "50+",
                plot=dcc.Graph(figure=fig6, style={'height': '500px'})
            )
        ]
    # --- Frederiksberg --- 
    elif muni_value == "frederiksberg":
        # Load mapping locally within the function to avoid NameError
        with open('mapping.json', 'r', encoding='utf-8') as f:
            mapping = json.load(f)
            
        muni_cfg = mapping.get("frederiksberg")
        folder = muni_cfg["folder"]
        files = muni_cfg["files"]

        return header_text, [
            #html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-6", children=[
                make_card(
                    "Vedligeholdelsesplan", "10-årigt budget.", 
                    "TYPE", "DALUX", "PRIORITET", "HØJ", # Added missing 2
                    plot=dcc.Graph(figure=create_frb_maintenance_budget())
                ),
                make_card(
                    "Potentiale", "DKK vs CO2.", 
                    "UNIT", "TONS", "STATUS", "ANALYSERET", # Added missing 2
                    plot=dcc.Graph(figure=create_frb_project_scatter())
                ),
                make_card(
                    "Portefølje Analyse", "Energimærke vs Byggeår", 
                    "KILDE", "ESG", "BYGNINGER", "ALLE", # Added missing 2
                    plot=dcc.Graph(figure=create_frb_property_characteristics())
                ),
                make_card(
                    "Risiko Heatmap", "Tilstand vs Pris.", 
                    "LEVEL", "GRAD 1 (GOD) - 5 (Kritisk)", "RISIKO", "SYNLIG", # Added missing 2
                    plot=dcc.Graph(figure=create_frb_risk_heatmap())
                ),
                make_card(
                    "ROI Bubble", "Investering vs TBT.", 
                    "FOCUS", "ROI", "OPTIMAL", "JA", # Added missing 2
                    plot=dcc.Graph(figure=create_frb_roi_chart())
                )
                
            #])
        ]

    # --- DEFAULT / FALLBACK ---
    else:
        return header_text, html.Div("Vælg en kommune for at se data.", className="p-20 text-center text-slate-400")

@app.callback(
    [Output("link-overblik", "className"),
     Output("link-forklaring", "className")],
    [Input("url", "pathname")]
)
def update_sidebar_shading(pathname):
    # This is the 'inactive' look: gray text, no background
    inactive = "w-full flex items-center gap-3 px-3 py-2 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors"
    
    # This is the 'active' look: indigo background with bold purple text
    active = "w-full flex items-center gap-3 px-3 py-2 text-primary font-semibold bg-indigo-50 dark:bg-indigo-900/20 rounded-lg shadow-sm"
    
    # Logic: if URL is /analyse, highlight Forklaringr. Otherwise highlight Overblik.
    if pathname == "/forklaring":
        return inactive, active
    else:
        return active, inactive

@app.callback(
    Output("db2-trend-graph", "figure"),
    [Input("address-selector", "value")],
    [State("muni-selector", "value")]
)
def update_trend_on_selection(selected_address, muni):
    # If no address is selected or we aren't in Faaborg, return empty
    if not selected_address or muni != "faaborg":
        return go.Figure()
    
    # We call the function again, but this time we pass the 'selected_address'
    # The '_' ignores the bar chart (since we don't need to re-render that)
    _, fig_trend = create_faaborg_energy_performance(muni, selected_address=selected_address)
    
    return fig_trend



@app.callback(
    Output("sync-button", "children"),
    Input("sync-button", "n_clicks"),
    State("muni-selector", "value"), # We need to know which muni is active
    prevent_initial_call=True
)
def sync_data(n_clicks, selected_muni):
    if not selected_muni:
        return "Vælg kommune først! ⚠️"

    # Load mapping to get paths
    with open('mapping.json', 'r', encoding='utf-8') as f:
        mapping = json.load(f)

    try:
        if selected_muni == "randers":
            timesafe_path = "data/randers/TIMESAFE-Export-Ventilationsanlæg.txt"
            buildings_path = "data/randers/Dalux/Alle_bygninger_DaluxFM_20251114_1159_6838.xlsx"

            process_randers_map_data(timesafe_path, buildings_path)
            return f"Randers Synced! ({n_clicks})"
            
        elif selected_muni == "faaborg":
            # Path from your latest message
            excel_path = "data/faaborg&midtfyn/Forbrugsoplysninger FM.xlsx"
            rearrange_carbon_data(excel_path)
            return f"Faaborg Synced! ✅ ({n_clicks})"

        elif selected_muni == "frederiksberg":
            muni_cfg = mapping["frederiksberg"]
            # Runs the Frederiksberg logic using the folder and file map
            process_frederiksberg_data(muni_cfg["folder"], muni_cfg["files"])
            return f"Frb. Synced! ✅ ({n_clicks})"

    except Exception as e:
        print(f"Sync Error: {e}")
        return "Sync Fejl! ❌"

    return "Sync Data"


app.clientside_callback(
    """function(n){ if(n>0) document.documentElement.classList.toggle('dark'); return ''; }""",
    Output("dummy-output", "children"), Input("theme-toggle", "n_clicks")
)

app.clientside_callback(
    """function(n){ if(n>0) window.print(); return ''; }""",
    Output("dummy-output", "id"), Input("btn-pdf", "n_clicks")
)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8050)