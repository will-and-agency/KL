import dash
from dash import dcc, html, Input, Output, State, clientside_callback

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
                            id="link-analyser",
                            href="/analyse",
                            className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors",
                            children=[
                                html.Span("insights", className="material-icons-round"),
                                html.Span("Analyser")
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
                html.H2(id="muni-header", className="text-3xl font-extrabold text-slate-800 dark:text-white uppercase tracking-tight"),
                html.P("Velkommen til dashboard-portalen. Monitorér energi og ESG.", className="text-slate-500 dark:text-slate-400 mt-1")
            ]),
            
            # Action Buttons + Theme Toggle (Top Right)
            html.Div(className="flex items-center gap-3", children=[
                # NEW: Theme Toggle placed here
                html.Button(id="theme-toggle", className="p-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-600 dark:text-slate-300 shadow-sm hover:bg-slate-50 transition-colors", children=[
                    html.Span("dark_mode", className="material-icons-round block dark:hidden"),
                    html.Span("light_mode", className="material-icons-round hidden dark:block")
                ]),
                
                html.Button("Eksportér PDF", id="btn-pdf", className="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium shadow-sm hover:bg-slate-50 transition-colors"),
                
                html.Button([
                    html.Span("filter_alt", className="material-icons-round text-sm"), 
                    " Filtre"
                ], className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium shadow-sm hover:opacity-90 transition-opacity flex items-center gap-2")
            ])
        ]),
        
        # Grid for Dashboards
        html.Div(id="dashboard-content", className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-2 gap-6"),
        
        # Hidden dummy outputs
        html.Div(id="dummy-output", style={"display": "none"})
    ])
])

# --- DASHBOARD CARD FACTORY ---
def make_card(title, desc, kpi1_label, kpi1_val, kpi2_label, kpi2_val):
    return html.Div(className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col transition-all hover:shadow-md", children=[
        # Header section
        html.Div(className="px-6 py-4 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center", children=[
            html.H3(title, className="font-semibold text-slate-800 dark:text-slate-100 uppercase text-sm tracking-wide"),
            html.Span("info", className="material-icons-round text-slate-400 cursor-pointer")
        ]),
        
        # Body section
        html.Div(className="p-6 flex-1 flex flex-col", children=[
            # Plot Placeholder
            html.Div(className="aspect-video bg-slate-50 dark:bg-slate-900 rounded-lg mb-6 flex items-center justify-center relative overflow-hidden group", children=[
                html.Span("INTERAKTIVT PLOT", className="text-xs font-medium text-slate-400 dark:text-slate-500 uppercase tracking-widest")
            ]),
            
            # Text and KPIs
            html.Div(className="space-y-4", children=[
                html.P(desc, className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed"),
                
                # KPI Footer
                html.Div(className="flex items-center gap-4 pt-4 border-t border-slate-100 dark:border-slate-700", children=[
                    html.Div(className="flex flex-col", children=[
                        html.Span(kpi1_label, className="text-[10px] text-slate-400 uppercase font-bold"),
                        html.Span(kpi1_val, className="font-bold text-lg")
                    ]),
                    html.Div(className="flex flex-col", children=[
                        html.Span(kpi2_label, className="text-[10px] text-slate-400 uppercase font-bold"),
                        html.Span(kpi2_val, className="font-bold text-lg text-emerald-500")
                    ])
                ])
            ])
        ])
    ])

# --- CALLBACKS ---

@app.callback(
    [Output("muni-header", "children"), 
     Output("dashboard-content", "children")],
    [Input("url", "pathname"), 
     Input("muni-selector", "value")]
)
def update_dynamic_content(pathname, muni_value):
    # 1. Update the Header Title
    header_text = f"{muni_value.replace('-', ' ')} KOMMUNE".upper()
    
    # 2. Render Content based on Pathname
    if pathname == "/analyse":
        # ANALYSER PAGE CONTENT
        content = html.Div(className="col-span-2 p-8 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm", children=[
            html.H3("Dybdegående Analyse", className="text-xl font-bold mb-4"),
            html.P(f"Her vises avancerede filtreringsmuligheder og tekniske tabeller for {muni_value.title()}."),
            # Add placeholders or real analysis components here
        ])
    else:
        # OVERBLIK PAGE CONTENT (Default Dashboard Grid)
        content = [
            make_card(
                "Dashboard 5: Strategisk ROI Matrix", 
                f"Prioritering af renoveringer for {muni_value} baseret på CO2-reduktion per investeret krone.",
                "INVESTERING", "12.4M DKK", "REDUKTION", "24%"
            ),
            make_card(
                "Dashboard 6: Ejendomskarakteristika", 
                f"Visualisering af bygningsmassen i {muni_value} baseret på opførelsesår og energimærke.",
                "TOTALAREAL", "450.000 m²", "GNSN. ALDER", "42 år"
            ),
            make_card(
                "Dashboard 7: Energiintensitet", 
                f"Detaljeret overblik over el- og varmeforbrug pr. kvadratmeter i {muni_value}.",
                "HØJESTE", "182 kWh/m²", "GNSN.", "78 kWh/m²"
            )
        ]
        
    return header_text, content

@app.callback(
    [Output("link-overblik", "className"),
     Output("link-analyser", "className")],
    [Input("url", "pathname")]
)
def update_sidebar_shading(pathname):
    # This is the 'inactive' look: gray text, no background
    inactive = "w-full flex items-center gap-3 px-3 py-2 text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors"
    
    # This is the 'active' look: indigo background with bold purple text
    active = "w-full flex items-center gap-3 px-3 py-2 text-primary font-semibold bg-indigo-50 dark:bg-indigo-900/20 rounded-lg shadow-sm"
    
    # Logic: if URL is /analyse, highlight Analyser. Otherwise highlight Overblik.
    if pathname == "/analyse":
        return inactive, active
    else:
        return active, inactive
    
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