import dash
from dash import html

def _datakilde_box(items):
    """Helper: creates a styled 'Datakilde' info box with a list of items."""
    return html.Div(className="mt-6 bg-blue-50 dark:bg-blue-900/20 p-5 rounded-xl border border-blue-200 dark:border-blue-800", children=[
        html.H4(className="font-bold text-blue-800 dark:text-blue-300 mb-3 text-sm uppercase tracking-wider flex items-center gap-2", children=[
            html.Span("storage", className="material-icons-round text-base"),
            "Datakilde"
        ]),
        html.Ul(className="list-disc list-inside text-sm text-blue-700 dark:text-blue-400 space-y-1.5", children=items)
    ])


def get_randers_analysis():
    return html.Div(className="max-w-5xl mx-auto space-y-12 pb-20", children=[
        # Intro Section
        html.Div(className="text-center space-y-4", children=[
            html.H2("Dashboard Forklaring: Randers Kommune",
                    className="text-3xl font-extrabold text-slate-800 dark:text-white"),
        ]),

        # ROI Matrix Explanation
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("insights", className="material-icons-round text-primary text-3xl"),
                html.H3("1. ROI Matrix: Strategisk Prioritering", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Scatter-plot der visualiserer sammenhængen mellem investering og CO2-gevinst. Inkluderer trendlinje og kvadrant-opdeling for hurtig prioritering.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("X-aksen (Investering i DKK):", className="text-primary"),
                        html.P("Anlægsudgift pr. projekt. Den lodrette linje ved 0 separerer positive og negative værdier.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Y-aksen (CO2-besparelse):", className="text-primary"),
                        html.P("Årlig CO2-reduktion i tons. Punkter over 0-linjen giver positiv klimaeffekt.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Trendlinje:", className="text-primary"),
                        html.P("Den stiplede linje viser den generelle sammenhæng mellem investering og besparelse.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Kvadrant-guide:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Øverste venstre = Quick Wins (lav pris, høj besparelse). Nederste højre = Lav prioritet (høj pris, lav effekt). Brug dette til at prioritere budgettet.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Forbedringer.xlsx"]),
                html.Li([html.B("Ark: "), "Forbedringer"]),
                html.Li([html.B("Kolonner brugt: "), "Investering (DKK), Besparelse (CO2 tons/år), Besparelse.2 (boblestørrelse), Type, Bygninger (hover-label)"]),
                html.Li([html.B("Bemærk: "), "Første header-række springes over (skiprows=1). Trendlinjen beregnes via lineær regression på alle datapunkter."]),
            ])
        ]),

        # Building Characteristics Explanation
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("domain", className="material-icons-round text-primary text-3xl"),
                html.H3("2. Bygningsmasse: Energiprofil", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Stacked bar chart der viser bygningsporteføljens energimæssige sammensætning fordelt på opførelsesår.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Stablede søjler:", className="text-primary"),
                        html.P("Hver søjle viser det totale antal bygninger pr. årti, opdelt i energimærker med officielle farver (A=grøn til G=rød).", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Farvekodning:", className="text-primary"),
                        html.P("Følger den danske energimærke-standard. Grønne nuancer (A-B) er energieffektive, røde (F-G) kræver opmærksomhed.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Indsigt:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Identificér årtier med høj koncentration af røde mærker - disse bygninger har størst renoveringspotentiale og bør prioriteres i langtidsplanen.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Bygninger.xlsx"]),
                html.Li([html.B("Ark: "), "Bygninger"]),
                html.Li([html.B("Kolonner brugt: "), "Opførelsesår (X-akse, binned i 30 intervaller), Energimærke (farveopdeling), Adresse (hover-info)"]),
                html.Li([html.B("Bemærk: "), "Første header-række springes over (skiprows=1). Bygninger uden opførelsesår eller energimærke filtreres fra."]),
            ])
        ]),

        # Map Explanation
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("location_on", className="material-icons-round text-red-500 text-3xl"),
                html.H3("3. Ventilation Status: Geografisk Kort", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Interaktivt kort med clustering og statusfarver baseret på Timesafe-data.",
                className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Clustering:", className="text-red-600"),
                        html.P("Markører grupperes automatisk ved zoom-out for bedre overblik. Zoom ind for at se individuelle bygninger.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Hover & Klik:", className="text-red-600"),
                        html.P("Hold musen over en markør for bygningsnavn. Klik for fuld adresse og status.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Praktisk brug:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Brug legenden til at forstå farvekoderne. Planlæg teknikerruter baseret på geografiske klynger af fejl.",
                        className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil 1: "), "TIMESAFE-Export-Ventilationsanlæg.txt (UTF-16 encoded)"]),
                html.Li([html.B("Kolonner fra Timesafe: "), "LOKATION_NAVN (bygningsnavn), ENHED_TILSTAND (status: Rød/Gul/Grøn/Ukendt)"]),
                html.Li([html.B("Fil 2: "), "Alle_bygninger_DaluxFM.xlsx (Dalux bygningsliste)"]),
                html.Li([html.B("Kolonner fra Dalux: "), "Institutionsnavn (til matching), Adresse (til geokodning)"]),
                html.Li([html.B("Kombinering: "), "Timesafe-lokationer matches med Dalux-bygninger via LOKATION_NAVN \u2194 Institutionsnavn. Adresser geokodes derefter til lat/lon koordinater via Nominatim."]),
            ])
        ]),

        # Interaction Guide
        html.Div(className="p-6 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800", children=[
            html.H4("Interaktivitet", className="font-bold text-indigo-800 dark:text-indigo-300 mb-2"),
            html.Ul(className="list-disc list-inside text-sm text-indigo-700 dark:text-indigo-400 space-y-1", children=[
                html.Li("Scroll for at zoome i ROI-matricen. Træk for at panorere."),
                html.Li("Klik på energimærker i legenden for at filtrere bygningsgrafen."),
                html.Li("Brug kortets zoom og pan til at udforske specifikke områder.")
            ])
        ])

    ])



def get_faaborg_analysis():
    return html.Div(className="max-w-5xl mx-auto space-y-12 pb-20", children=[
        # Intro Section
        html.Div(className="text-center space-y-4", children=[
            html.H2("Dashboard Forklaring: Faaborg-Midtfyn Kommune",
                    className="text-3xl font-extrabold text-slate-800 dark:text-white"),
        ]),

        # Energy Performance
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("electric_bolt", className="material-icons-round text-emerald-500 text-3xl"),
                html.H3("1. Energiperformance: Faktisk vs. Forventet", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Split-view med afvigelsesoversigt og forbrugsudvikling over tid.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Venstre: Afvigelsesbar:", className="text-emerald-600"),
                        html.P("Horisontalt søjlediagram med alle adresser. Rød = overforbrug, grøn = underforbrug. Den lodrette linje ved 0 adskiller over/under budget.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Højre: Forbrugsudvikling:", className="text-emerald-600"),
                        html.P("Dual-line chart der sammenligner faktisk forbrug (blå) med energimærkets forventning (grøn stiplet). Det røde område viser ineffektivitets-gabet.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Sådan bruges det:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Vælg en adresse i dropdown'en for at se dens forbrugshistorik. Gabet mellem linjerne viser de 'skjulte omkostninger' ved dårlig drift.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Forbrugsoplysninger FM.xlsx"]),
                html.Li([html.B("Ark 1: "), "Energi Oversigt \u2014 masterark med alle adresser, afvigelsesprocent (Forskel/Afvigelse-kolonne), kWh pr. m\u00b2, Varmeforbrug, Elforbrug og Energimærke kWh pr. m\u00b2 (target)."]),
                html.Li([html.B("Ark 2: "), "Individuelle adresseark (60+ ark, \u00e9t pr. bygning) \u2014 indeholder Graddagskorrigeret forbrug (faktisk) og Mærke/Mål (target) for hvert år 2019\u20132024."]),
                html.Li([html.B("Kombinering: "), "Afvigelsesbarren henter data fra Energi Oversigt. Trend-grafen matcher den valgte adresse til sit individuelle ark via fuzzy navnematching, og henter års-data derfra. Hvis arket mangler, falder den tilbage til Energi Oversigt."]),
            ])
        ]),

        # Procurement Gap
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("savings", className="material-icons-round text-blue-500 text-3xl"),
                html.H3("2. Indkøbsoptimering: Waterfall", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Waterfall-diagram der visualiserer besparelsesflow fra standardpris til udbudspris.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Tre kolonner:", className="text-blue-600"),
                        html.P("Standard Pris \u2192 Besparelse (grøn) \u2192 Udbuds Pris. Overskriften viser både DKK og procentuel besparelse.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Data-labels:", className="text-blue-600"),
                        html.P("Hver søjle har påtrykt værdi i DKK for nem aflæsning.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Indsigt:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Dokumenterer værdien af strategisk indkøb. Besparelsen kan reinvesteres i energiforbedringer.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Vedligeholdelsesplaner 2024.xlsx"]),
                html.Li([html.B("Ark: "), "Priskatalog"]),
                html.Li([html.B("Kolonner brugt: "), "Pris1 (standardpris pr. enhed) og Pris3 (udbudspris/bulkpris). Alle rækker summeres for at beregne totalbesparelsen."]),
                html.Li([html.B("Beregning: "), "Besparelse = Sum(Pris1) \u2212 Sum(Pris3). Procent = Besparelse / Sum(Pris1) \u00d7 100."]),
            ])
        ]),

        # Ventilation Peaks
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("air", className="material-icons-round text-sky-400 text-3xl"),
                html.H3("3. Vedligeholdelsesmønster: Sæsonanalyse", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Area chart der viser filterskift fordelt på måneder med gennemsnits-reference.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Månedsoversigt:", className="text-sky-500"),
                        html.P("Danske månedsnavne i kronologisk rækkefølge. Datapunkter er farvekodede: grøn=under gns., orange=over gns., rød=peak.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Gennemsnitslinje:", className="text-sky-500"),
                        html.P("Den stiplede linje viser det månedlige gennemsnit. Peak-måneden fremhæves i titlen.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Praktisk brug:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Brug grafen til at sprede vedligeholdelsesopgaver jævnt over året og undgå overbelastning i peak-måneder.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Ventilation registrering.xlsx"]),
                html.Li([html.B("Ark: "), "60+ individuelle lokationsark (\u00e9t pr. bygning). Ark med navnene 'NY', 'Skabelon' og 'Forside' springes over."]),
                html.Li([html.B("Kolonne brugt: "), "Dato for filterskifte \u2014 dato-værdier hentes fra samtlige ark og samles i \u00e9n samlet tidsserie."]),
                html.Li([html.B("Beregning: "), "Alle datoer grupperes efter måned (1\u201312) og tælles op. Gennemsnittet beregnes for reference-linjen. Peak-måneden identificeres automatisk."]),
            ])
        ]),

        # Navigation Helper
        html.Div(className="p-6 bg-slate-100 dark:bg-slate-900/40 rounded-xl border border-slate-200 dark:border-slate-700", children=[
            html.H4("Navigation", className="font-bold text-slate-800 dark:text-white mb-2"),
            html.Ul(className="list-disc list-inside text-sm text-slate-600 dark:text-slate-400 space-y-1", children=[
                html.Li("Brug dropdown'en til at skifte mellem adresser i energioversigten."),
                html.Li("Hover over søjler for at se detaljerede værdier."),
                html.Li("Peak-måneden vises automatisk i graf-titlen.")
            ])
        ])
    ])



def get_frederiksberg_analysis():
    return html.Div(className="max-w-5xl mx-auto space-y-12 pb-20", children=[
        # Intro Section
        html.Div(className="text-center space-y-4", children=[
            html.H2("Dashboard Forklaring: Frederiksberg Kommune",
                    className="text-3xl font-extrabold text-slate-800 dark:text-white"),
        ]),

        # 1. Maintenance Budget
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("account_balance", className="material-icons-round text-amber-500 text-3xl"),
                html.H3("1. Vedligeholdelsesplan: 10-\u00e5rigt Budget", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Stacked bar chart der viser planlagt vedligeholdelsesbudget fordelt på år og kategorier.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Stablede søjler:", className="text-amber-600"),
                        html.P("Hver søjle repræsenterer \u00e9t år og viser det samlede budget opdelt i kategorier (VVS, El, Tag osv.).", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Farvekodning:", className="text-amber-600"),
                        html.P("Hver kategori har sin egen farve. Brug legenden til at isolere specifikke områder.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Indsigt:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Identificér 'peak years' hvor budgettet er højest. Brug dette til likviditetsplanlægning og til at sprede store udgifter.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Skolen p\u00e5 duevej vedligeholdelsesplan.xlsx"]),
                html.Li([html.B("Ark: "), "Hovedark (header r\u00e6kke 0, r\u00e6kke 2 springes over)"]),
                html.Li([html.B("Kolonner brugt: "), "Hovedomkostningsomr\u00e5de (kategori/farveopdeling), Tilstand (tilstandsgrad 1\u20134), \u00e5rskolonner 2023\u20132033 (budget i DKK)"]),
                html.Li([html.B("Beregning: "), "Hver r\u00e6kke repr\u00e6senterer en vedligeholdelsespost. Kumulativ linje beregnes som l\u00f8bende sum af \u00e5rlige totaler."]),
            ])
        ]),

        # 2. Project Scatter (DKK vs CO2)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("scatter_plot", className="material-icons-round text-emerald-500 text-3xl"),
                html.H3("2. Projektpotentiale: Investering vs. CO2", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Scatter plot der visualiserer forholdet mellem investeringsomkostning og CO2-besparelse.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("X-aksen (Investering i DKK):", className="text-emerald-600"),
                        html.P("Projektets samlede anlægsudgift. Højere = dyrere projekt.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Y-aksen (CO2-besparelse):", className="text-emerald-600"),
                        html.P("Årlig CO2-reduktion i tons. Punkter højt oppe giver mest klimaeffekt.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Kvadrant-guide:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Øverste venstre = Quick Wins (lav pris, høj besparelse). Hover over punkter for projektdetaljer.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Forbedringer energimærker skolen p\u00e5 duevej.xlsx"]),
                html.Li([html.B("Ark: "), "Forbedringer (header p\u00e5 r\u00e6kke 2)"]),
                html.Li([html.B("Kolonner brugt: "), "Investering (DKK, X-akse), Besparelse (CO2 tons/\u00e5r, Y-akse), TBT (tilbagebetalingstid), Type (farvekategori), Titel + Bygninger (hover-label)"]),
                html.Li([html.B("Beregning: "), "Median-linjer beregnes for b\u00e5de DKK og CO2 som referencelinjer. Trendlinje via line\u00e6r regression."]),
            ])
        ]),

        # 3. Property Characteristics (3 subplots)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("domain", className="material-icons-round text-indigo-500 text-3xl"),
                html.H3("3. Porteføljeanalyse: Bygningskarakteristika", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Tre subplots der viser besparelsespotentiale fordelt på areal, energimærke og byggeår.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Areal (m\u00b2):", className="text-indigo-600"),
                        html.P("Gennemsnitlig besparelse grupperet efter bygningsstørrelse. Større bygninger har ofte andet potentiale end små.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Energimærke:", className="text-indigo-600"),
                        html.P("Besparelse pr. energimærke med officielle farver (A=grøn til G=rød). Dårlige mærker har typisk størst potentiale.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Byggeår:", className="text-indigo-600"),
                        html.P("Besparelse pr. årti. Ældre bygninger fra 60-70'erne har ofte højere besparelsespotentiale.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hover-info:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Hold musen over søjlerne for at se hvilke bygninger der indgår, antal bygninger og gennemsnitlig besparelse.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Oplysninger bygninger skolen p\u00e5 duevej.xlsx"]),
                html.Li([html.B("Ark 1: "), "Bygninger (header p\u00e5 r\u00e6kke 2) \u2014 indeholder Bygningsnavn, Opvarmet areal (m\u00b2), Opf\u00f8relses\u00e5r og Energimærke."]),
                html.Li([html.B("Ark 2: "), "Teoretisk forbrug (header p\u00e5 r\u00e6kke 2) \u2014 indeholder Ejendomsnavn og Besparelse % (kWh)."]),
                html.Li([html.B("Kombinering: "), "De to ark sammenkobles (merge) via Bygningsnavn \u2194 Ejendomsnavn. Resultatet giver besparelsesprocent koblet med bygningskarakteristika for alle matchede bygninger."]),
                html.Li([html.B("Beregning: "), "Besparelsesprocent grupperes i 3 dimensioner: arealintervaller (<500, 500\u20131000, osv.), energimærke (A\u2013G) og \u00e5rti (1960s, 1970s, osv.). Gennemsnittet vises pr. gruppe."]),
            ])
        ]),

        # 4. Risk Heatmap
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("warning", className="material-icons-round text-red-500 text-3xl"),
                html.H3("4. Risiko-Heatmap: Tilstand vs. Tid", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Heatmap der krydser bygningens tilstandsgrad (1-4) med årstal for at afsløre risikomønstre.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Tilstandsgrader:", className="text-red-600"),
                        html.P("Grad 1 = God stand, Grad 5 = Kritisk. Røde felter indikerer høje omkostninger på bygninger i dårlig stand.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Farveskala:", className="text-red-600"),
                        html.P("Lysere = lavere omkostninger. Mørkere rød = højere omkostninger. Hvide felter = ingen data.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Risikobølger:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Se efter lodrette mønstre (mange bygninger forfalder samme år) eller vandrette (én tilstandsgrad koster meget over tid).",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Skolen p\u00e5 duevej vedligeholdelsesplan.xlsx (samme fil som Dashboard 1)"]),
                html.Li([html.B("Kolonner brugt: "), "Tilstand (tilstandsgrad, Y-akse), \u00e5rskolonner 2023\u20132033 (budget i DKK, cellefarve)"]),
                html.Li([html.B("Beregning: "), "Samme vedligeholdelsesdata pivoteres: r\u00e6kker grupperes efter Tilstandsgrad, kolonner er \u00e5rstal, og cellev\u00e6rdier er summeret budget (DKK). Dette giver en anden vinkel p\u00e5 det samme datas\u00e6t."]),
            ])
        ]),

        # 5. ROI Bubble Chart
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("bubble_chart", className="material-icons-round text-blue-500 text-3xl"),
                html.H3("5. ROI Bubble: Tilbagebetalingstid vs. CO2", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Bubble chart der kombinerer tilbagebetalingstid, CO2-besparelse og investeringsstørrelse.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),

            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("X-aksen (TBT i år):", className="text-blue-600"),
                        html.P("Tilbagebetalingstid. Projekter til venstre tjener sig hurtigere hjem.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Y-aksen (CO2):", className="text-blue-600"),
                        html.P("CO2-besparelse. Højere = større klimaeffekt.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Boblestørrelse:", className="text-blue-600"),
                        html.P("Større bobler = større investering (DDK). Små bobler kan være 'low-hanging fruit'.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Quick Wins zone:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Fokusér på det grønne område: Projekter med kort TBT og høj CO2-gevinst. Disse bør prioriteres i budgettet.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ]),

            _datakilde_box([
                html.Li([html.B("Fil: "), "Forbedringer energimærker skolen p\u00e5 duevej.xlsx (samme fil som Dashboard 2)"]),
                html.Li([html.B("Ark: "), "Forbedringer"]),
                html.Li([html.B("Kolonner brugt: "), "TBT (tilbagebetalingstid i \u00e5r, X-akse), Besparelse (CO2 tons/\u00e5r, Y-akse), Investering (DKK, boblest\u00f8rrelse), Type (farvekategori)"]),
                html.Li([html.B("Beregning: "), "Samme projektdata som Dashboard 2, men visualiseret med TBT p\u00e5 X-aksen i stedet for DKK. Quick Wins-zonen markerer projekter med TBT \u2264 10 \u00e5r og CO2 over gennemsnittet."]),
            ])
        ]),

        # Interaction Guide
        html.Div(className="p-6 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800", children=[
            html.H4("Interaktivitet", className="font-bold text-indigo-800 dark:text-indigo-300 mb-2"),
            html.Ul(className="list-disc list-inside text-sm text-indigo-700 dark:text-indigo-400 space-y-1", children=[
                html.Li("Hover over heatmap-celler for præcise budgetbeløb."),
                html.Li("Klik på legenden i vedligeholdelsesplanen for at isolere kategorier."),
                html.Li("Hover over porteføljeanalysen for at se bygningsnavne i hver gruppe."),
                html.Li("Zoom i ROI-diagrammerne ved at trække et område.")
            ])
        ])
    ])
