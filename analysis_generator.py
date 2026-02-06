import dash
from dash import html

def get_randers_analysis():
    return html.Div(className="max-w-5xl mx-auto space-y-12 pb-20", children=[
        # Intro Section
        html.Div(className="text-center space-y-4", children=[
            html.H2("Dashboard Forklaring: Randers Kommune", 
                    className="text-3xl font-extrabold text-slate-800 dark:text-white"),
            html.P("Denne sektion giver en dybdegående gennemgang af, hvordan de visuelle grafer skal læses, og hvilke datapunkter der præsenteres.",
                   className="text-lg text-slate-600 dark:text-slate-400"),
        ]),

        # ROI Matrix Explanation
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("insights", className="material-icons-round text-primary text-3xl"),
                html.H3("1. ROI Matrix: Strategisk Prioritering", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Dette scatter-plot (punktdiagram) visualiserer sammenhængen mellem økonomisk investering og miljømæssig gevinst for foreslåede energiprojekter.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),
            
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("X-aksen (Investering):", className="text-primary"),
                        html.P("Viser den samlede anlægsudgift i DKK for det enkelte projekt. Jo længere til højre et punkt er, jo dyrere er projektet at etablere.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Y-aksen (CO2-besparelse):", className="text-primary"),
                        html.P("Viser den årlige estimerede reduktion i CO2-udledning. Jo højere et punkt er placeret, jo større er klimaeffekten.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Farvekodning:", className="text-primary"),
                        html.P("Projekterne er kategoriseret efter type (f.eks. belysning eller ventilation), hvilket gør det muligt at se tekniske mønstre.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Ved at kigge i øverste venstre kvadrant finder man de mest effektive projekter (lav pris, høj besparelse). Punkter i nederste højre kvadrant repræsenterer projekter med en længere tilbagebetalingstid.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Building Characteristics Explanation
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("domain", className="material-icons-round text-primary text-3xl"),
                html.H3("2. Bygningsmasse: Karakteristika", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Dette histogram (søjlediagram) giver et overblik over den fysiske porteføljes sammensætning og energimæssige sundhedstilstand.",
                   className="text-slate-600 dark:text-slate-400 mb-6"),
            
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("X-aksen (Opførelsesår):", className="text-primary"),
                        html.P("Inddeler kommunens bygninger i tidsintervaller. Dette afslører trends relateret til historiske bygningsreglementer.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Y-aksen (Antal/Areal):", className="text-primary"),
                        html.P("Viser mængden af bygninger eller kvadratmeter inden for hvert tidsinterval.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Farve-lag (Energimærke):", className="text-primary"),
                        html.P("Hver søjle er opdelt i farver, der repræsenterer energimærker fra A (grøn) til G (rød).", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Man kan direkte aflæse, om ældre bygninger systematisk har dårligere energimærker end nyere. Hvis en søjle for f.eks. 1960'erne er domineret af røde farver, indikerer det et stort behov for tekniske opgraderinger.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Add this inside get_randers_analysis() in app.py
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("location_on", className="material-icons-round text-red-500 text-3xl"),
                html.H3("3. Ventilation Status: Geografisk Oversigt", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.P("Dette kort visualiserer sundhedstilstanden af kommunens ventilationsanlæg baseret på data fra Timesafe.", 
                className="text-slate-600 dark:text-slate-400 mb-6"),
            
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.P([
                        html.B("Kort-markører: ", className="text-red-600"),
                        "Hver cirkel repræsenterer en institution. Farven skifter automatisk baseret på den mest kritiske status fundet i ventilations-tekstfilen."
                    ], className="text-sm"),
                    html.P([
                        html.B("Data-sammenkobling: ", className="text-red-600"),
                        "Systemet parrer automatisk lokationsnavne fra Timesafe med de officielle adresser fra bygningslisten for at placere markøren præcist."
                    ], className="text-sm"),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Anvendelse:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Ved at se fejlene geografisk kan driftsafdelingen optimere kørsel for teknikerne og se, om der er geografiske klynger af problemer (f.eks. pga. lokale strømudfald eller vejrforhold).",
                        className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Interaction Guide
        html.Div(className="p-6 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-100 dark:border-indigo-800", children=[
            html.H4("💡 Interaktivitetsguide", className="font-bold text-indigo-800 dark:text-indigo-300 mb-2"),
            html.Ul(className="list-disc list-inside text-sm text-indigo-700 dark:text-indigo-400 space-y-1", children=[
                html.Li("Hold musen over datapunkter for at se specifikke projektbeskrivelser."),
                html.Li("Brug musen til at tegne en firkant i ROI-matricen for at zoome ind."),
                html.Li("Klik på kategorierne i legenden for at isolere specifikke bygningstyper.")
            ])
        ])
        
    ])



def get_faaborg_analysis():
    return html.Div(className="max-w-5xl mx-auto space-y-12 pb-20", children=[
        # Intro Section
        html.Div(className="text-center space-y-4", children=[
            html.H2(" Dashboard Forklaring: Faaborg-Midtfyn Kommune", 
                    className="text-3xl font-extrabold text-slate-800 dark:text-white"),
            html.P("Denne sektion forklarer sammenhængen mellem energiforbrug, CO2-udledning og optimering af drift og indkøb.",
                   className="text-lg text-slate-600 dark:text-slate-400"),
        ]),

        # Energy Performance & Carbon Footprint
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("co2", className="material-icons-round text-emerald-500 text-3xl"),
                html.H3("1. Energi-afvigelse & Carbon Footprint", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Afvigelses-oversigt (Bar Chart):", className="text-emerald-600"),
                        html.P("Viser forskellen mellem det budgetterede og det faktiske energiforbrug pr. bygning. En lang bjælke til højre indikerer et merforbrug, der kræver teknisk gennemgang.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Carbon Trend (Stacked Area):", className="text-emerald-600"),
                        html.P("Visualiserer den historiske udvikling i CO2-aftrykket fordelt på brændselstyper (Gas, El, Varme, Vand). Den stiplede linje viser det samlede CO2-aftryk over tid.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Her kan man identificere, om en bygnings CO2-reduktion skyldes fald i én specifik energikilde (f.eks. gas ved konvertering til fjernvarme), eller om der er et generelt fald i alle kategorier.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Procurement Gap (Udbud vs Standard)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("savings", className="material-icons-round text-blue-500 text-3xl"),
                html.H3("2. Udbudsoptimering (Procurement Gap)", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Standard Pris vs. Udbuds Pris:", className="text-blue-600"),
                        html.P("Sammenligner de gængse markedspriser (Standard) med de faktiske priser opnået gennem udbudsaftaler.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("Besparelses-titel:", className="text-blue-600"),
                        html.P("Overskriften beregner automatisk den samlede økonomiske gevinst opnået ved effektiv indkøbsstyring.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Denne graf dokumenterer værdien af udbudsstyring. Forskellen mellem de to søjler repræsenterer den likviditet, der frigøres til andre energiforbedrende tiltag.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Ventilation Peaks (Seasonality)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("air", className="material-icons-round text-sky-400 text-3xl"),
                html.H3("3. Sæsonudsving i Vedligehold (Ventilation)", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("Månedlig fordeling:", className="text-sky-500"),
                        html.P("Histogrammet tæller antallet af filterskift i ventilationsanlæg på tværs af kommunens 60+ ejendomme, fordelt på årets måneder.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Grafen afslører spidsbelastninger i driftsafdelingen. Hvis mange filtre skiftes i samme måned, kan det indikere et behov for at jævne vedligeholdelsesplanen ud for at undgå overbelastning af personalet.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Navigation Helper
        html.Div(className="p-6 bg-slate-100 dark:bg-slate-900/40 rounded-xl border border-slate-200 dark:border-slate-700", children=[
            html.H4("💡 Tips til navigation", className="font-bold text-slate-800 dark:text-white mb-2"),
            html.P("I CO2-oversigten kan du klikke på en bygning i venstre side for at opdatere trend-grafen til højre. Dette giver dig mulighed for at dykke ned i specifikke ejendommes historik.", 
                   className="text-sm text-slate-600 dark:text-slate-400")
        ])
    ])



def get_frederiksberg_analysis():
    return html.Div(className="max-w-5xl mx-auto space-y-12 pb-20", children=[
        # Intro Section
        html.Div(className="text-center space-y-4", children=[
            html.H2("Dashboard Forklaring: Frederiksberg Kommune", 
                    className="text-3xl font-extrabold text-slate-800 dark:text-white"),
            html.P("Denne analyse gennemgår sammenhængen mellem vedligeholdelse, investeringsprojekter og bygningsmassens energipotentiale.",
                   className="text-lg text-slate-600 dark:text-slate-400"),
        ]),

        # Maintenance Budget & Risk (D1 & D7)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("warning", className="material-icons-round text-amber-500 text-3xl"),
                html.H3("1. Vedligeholdelse & Risikostyring", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("D1: Vedligeholdelsesplan (10 år):", className="text-amber-600"),
                        html.P("Et søjlediagram der viser det planlagte budget fordelt på år og kategorier. Det giver overblik over, hvornår de store investeringer i bygningens drift rammer.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("D7: Vedligeholdelsesrisiko (Heatmap):", className="text-amber-600"),
                        html.P("Et heatmap der krydser tid (år) med bygningens tilstand (Grad 1-4). Røde felter indikerer dyre reparationer på bygninger i dårlig stand.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Ved at sammenligne D1 og D7 kan man se, om budgettet er allokeret korrekt til de mest kritiske opgaver (Grad 4). Heatmap'et afslører 'risiko-bølger', hvor mange bygninger forfalder samtidigt.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Projects & ROI (D2 & D8)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("trending_up", className="material-icons-round text-blue-500 text-3xl"),
                html.H3("2. Projektprioritering & CO2 Gevinst", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("D2: Investering vs. CO2 Reduktion:", className="text-blue-600"),
                        html.P("Et scatter-plot der viser, hvor meget CO2 man sparer i forhold til projektets pris.", className="text-sm mt-1")
                    ]),
                    html.Div([
                        html.B("D8: Strategisk ROI:", className="text-blue-600"),
                        html.P("Fokuserer på tilbagebetalingstid (TBT) mod CO2-gevinst. Boblernes størrelse indikerer investeringens samlede størrelse (DDK).", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Det grønne område i D8 markerer 'Quick Wins' — projekter der tjener sig selv hjem på under 10 år og samtidigt giver en høj CO2-reduktion.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Property Characteristics (D3)
        html.Div(className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-sm border border-slate-200 dark:border-slate-700", children=[
            html.Div(className="flex items-center gap-4 mb-6", children=[
                html.Span("analytics", className="material-icons-round text-indigo-500 text-3xl"),
                html.H3("3. Bygningskarakteristika & Besparelsespotentiale", className="text-2xl font-bold text-slate-800 dark:text-white"),
            ]),
            html.Div(className="grid grid-cols-1 md:grid-cols-2 gap-8", children=[
                html.Div(className="space-y-4", children=[
                    html.Div([
                        html.B("D3: Besparelse pr. Byggeår:", className="text-indigo-600"),
                        html.P("Viser det gennemsnitlige besparelsespotentiale i procent for bygninger opdelt efter deres opførelsesår.", className="text-sm mt-1")
                    ]),
                ]),
                html.Div(className="bg-slate-50 dark:bg-slate-900/50 p-6 rounded-xl border border-dashed border-slate-300 dark:border-slate-600", children=[
                    html.H4("Hvad man kan se:", className="font-bold mb-2 text-slate-800 dark:text-white text-sm uppercase tracking-wider"),
                    html.P("Her kan man identificere specifikke årgange af byggerier, der er særligt energi-ineffektive. Det hjælper med at målrette renoveringsindsatsen mod de mest 'lønsomme' byggeperioder.",
                           className="text-sm leading-relaxed text-slate-600 dark:text-slate-400")
                ])
            ])
        ]),

        # Interaction Guide (The missing piece)
        html.Div(className="p-6 bg-slate-100 dark:bg-slate-900/40 rounded-xl border border-slate-200 dark:border-slate-700", children=[
            html.H4("💡 Interaktivitetsguide", className="font-bold text-slate-800 dark:text-white mb-2"),
            html.Ul(className="list-disc list-inside text-sm text-slate-600 dark:text-slate-400 space-y-1", children=[
                html.Li("Hold musen over heatmap'et (D7) for at se de præcise budgetbeløb for hver tilstandsgrad."),
                html.Li("Brug legenden i D1 til at isolere specifikke vedligeholdelseskategorier som f.eks. 'Tag' eller 'VVS'."),
                html.Li("I ROI-matricen (D8) kan du klikke og trække for at zoome ind på projekter med kort tilbagebetalingstid.")
            ])
        ])
    ])