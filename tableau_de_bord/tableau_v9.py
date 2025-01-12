import os
import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from lrs_request import fetch_lrs_data, process_data, calculate_time_per_level
from score import extract_scores

app = dash.Dash(__name__, external_stylesheets=["/assets/style.css"])

app.layout = html.Div(
    children=[
        html.H1(
            children="Tableau de Bord des métriques essentielles du joueur par niveau"
        ),
        dcc.Store(id="data-store"),
        html.Div(
            children=[
                dcc.Input(
                    id="username-input",
                    type="text",
                    placeholder="Entrer un nom d'utilisateur",
                    style={"margin-right": "10px"},
                ),
                html.Button("Entrer", id="submit-button", n_clicks=0),
                dcc.Dropdown(
                    id="menu-deroulant-scenario",
                    options=[],  # Les options seront mises à jour dynamiquement
                    placeholder="Sélectionner un scénario",
                    style={"width": "50%", "margin-top": "20px"},
                ),
            ],
            style={"text-align": "center", "margin-bottom": "20px"},
        ),
        html.Div(
            id="output-container",
            children=[
                html.Div(
                    className="graph-container",
                    children=[
                        dcc.Graph(id="graph-avg-score"),
                        dcc.Graph(id="graph-max-score"),
                        dcc.Graph(id="graph-completed-counts"),
                        # dcc.Graph(id='graph-2stars'),
                        # dcc.Graph(id='graph-3stars'),
                        dcc.Graph(id="graph-player-stars"),
                        dcc.Graph(
                            id="graph-total-stars"
                        ),  # New graph for Nombre d\'étoiles du joueur par scénario
                        html.Div(
                            className="dropdown-container",
                            children=[
                                dcc.Dropdown(
                                    id="menu-deroulant-time-spent",
                                    options=[
                                        {
                                            "label": "Temps passé maximum par niveau",
                                            "value": "Max Time Spent",
                                        },
                                        {
                                            "label": "Temps passé minimum par niveau",
                                            "value": "Min Time Spent",
                                        },
                                        {
                                            "label": "Temps moyen passé par niveau",
                                            "value": "Average Duration",
                                        },
                                    ],
                                    value="Max Time Spent",  # Par défaut, afficher le temps passé maximum par niveau
                                    style={"width": "50%"},
                                )
                            ],
                        ),
                        dcc.Graph(id="graph-time-spent"),
                    ],
                    style={"display": "flex", "flex-direction": "column"},
                )
            ],
        ),
        html.Script(src="/assets/script.js"),
    ]
)


@app.callback(
    [Output("menu-deroulant-scenario", "options"), Output("data-store", "data")],
    [Input("submit-button", "n_clicks")],
    [State("username-input", "value")],
)
def update_scenario_options(n_clicks, username):
    # Si le champ utilisateur est vide
    if not username:
        return [], None  # Deux valeurs : une liste vide et None pour le stockage

    # Si le bouton est cliqué et qu'un nom d'utilisateur est fourni
    if n_clicks > 0:
        data = fetch_lrs_data(username)  # Récupération des données LRS
        (
            df,
            all_mission_levels,
            completed_counts,
            avg_score_by_level,
            max_score_by_level,
        ) = process_data(data)

        # Stockage des données dans le data-store
        store_data = {
            "df": df.to_dict("records"),
            "all_mission_levels": all_mission_levels,
            "completed_counts": completed_counts,
            "avg_score_by_level": avg_score_by_level,
            "max_score_by_level": max_score_by_level,
        }

        # Générer les options pour le menu déroulant des scénarios
        scenarios = df["Scenario"].dropna().unique()
        scenarios = [
            scenario
            for scenario in scenarios
            if not scenario.startswith(("erty", "plok"))
        ]
        scenario_options = [
            {"label": scenario, "value": scenario} for scenario in scenarios
        ]

        return scenario_options, store_data  # Deux valeurs retournées

    # Si aucune action n'est effectuée
    return [], None  # Deux valeurs par défaut


@app.callback(
    [
        Output("graph-avg-score", "figure"),
        Output("graph-max-score", "figure"),
        Output("graph-completed-counts", "figure"),
        Output("graph-time-spent", "figure"),
    ],
    # Output('graph-2stars', 'figure'),
    # Output('graph-3stars', 'figure'),
    # Output('graph-combined1', 'figure'),
    # Output('graph-combined2', 'figure'),
    Output(
        "graph-total-stars", "figure"
    ),  # New output for Nombre d\'étoiles total par scénario graph
    Output(
        "graph-player-stars", "figure"
    ),  # New output for Nombre d\'étoiles du joueur par scénario graph
    [
        Input("menu-deroulant-scenario", "value"),
        Input("menu-deroulant-time-spent", "value"),
        Input("data-store", "data"),
    ],
    [State("username-input", "value")],
)
def update_graphs(selected_scenario, selected_time_spent, data, username):
    if not username or not selected_scenario:
        return {}, {}, {}, {}, {}, {}

    # data = fetch_lrs_data(username)
    # df, all_mission_levels, completed_counts, avg_score_by_level, max_score_by_level = (
    #     process_data(data)
    # )

    print(f"Type de data : {type(data)}")
    print(f"Valeur de data : {data}")

    df = pd.DataFrame(data["df"])
    all_mission_levels = data["all_mission_levels"]
    completed_counts = data["completed_counts"]
    avg_score_by_level = data["avg_score_by_level"]
    max_score_by_level = data["max_score_by_level"]

    df = df[df["Scenario"] == selected_scenario]
    # print(f"df colmuns : {df.columns}")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    time_spent_max, time_spent_min, time_spent_avg = calculate_time_per_level(df)

    # Arrondir les valeurs des dictionnaires à 3 décimales
    time_spent_max = {k: round(v, 3) for k, v in time_spent_max.items()}
    time_spent_min = {k: round(v, 3) for k, v in time_spent_min.items()}
    time_spent_avg = {k: round(v, 3) for k, v in time_spent_avg.items()}

    df_time_spent_max = pd.DataFrame(
        list(time_spent_max.items()), columns=["Mission Level", "Max Time Spent"]
    )
    df_time_spent_min = pd.DataFrame(
        list(time_spent_min.items()), columns=["Mission Level", "Min Time Spent"]
    )
    df_time_spent_avg = pd.DataFrame(
        list(time_spent_avg.items()), columns=["Mission Level", "Average Duration"]
    )

    df_avg_score = pd.DataFrame(
        list(avg_score_by_level.items()), columns=["Mission Level", "Average Score"]
    )
    fig_avg_score = px.bar(
        df_avg_score,
        x="Mission Level",
        y="Average Score",
        title="Score moyen par niveau",
        text="Average Score",
    )
    fig_avg_score.update_traces(texttemplate="%{text}", textposition="outside")
    fig_avg_score.update_layout(
        xaxis_title="Niveaux",
        yaxis_title="Average Score",
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode="linear", dtick=1),
    )

    df_max_score = pd.DataFrame(
        list(max_score_by_level.items()), columns=["Mission Level", "Max Score"]
    )
    fig_max_score = px.bar(
        df_max_score,
        x="Mission Level",
        y="Max Score",
        title="Score max par niveau",
        text="Max Score",
    )
    fig_max_score.update_traces(texttemplate="%{text}", textposition="outside")
    fig_max_score.update_layout(
        xaxis_title="Niveaux",
        yaxis_title="Max Score",
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode="linear", dtick=1),
    )

    df_completed_counts = pd.DataFrame(
        list(completed_counts.items()), columns=["Mission Level", "Completed Count"]
    )
    fig_completed_counts = px.bar(
        df_completed_counts,
        x="Mission Level",
        y="Completed Count",
        title="Nombre de niveaux complétés",
        text="Completed Count",
    )
    fig_completed_counts.update_traces(texttemplate="%{text}", textposition="outside")
    fig_completed_counts.update_layout(
        xaxis_title="Niveaux",
        yaxis_title="Completed Count",
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode="linear", dtick=1),
    )

    if selected_time_spent == "Max Time Spent":
        fig_time_spent = px.bar(
            df_time_spent_max,
            x="Mission Level",
            y="Max Time Spent",
            title="Temps passé maximum par niveau",
            text="Max Time Spent",
        )
    elif selected_time_spent == "Min Time Spent":
        fig_time_spent = px.bar(
            df_time_spent_min,
            x="Mission Level",
            y="Min Time Spent",
            title="Temps passé minimum par niveau",
            text="Min Time Spent",
        )
    elif selected_time_spent == "Average Duration":
        fig_time_spent = px.bar(
            df_time_spent_avg,
            x="Mission Level",
            y="Average Duration",
            title="Temps moyen passé par niveau",
            text="Average Duration",
        )

    fig_time_spent.update_traces(texttemplate="%{text}", textposition="outside")
    fig_time_spent.update_layout(
        xaxis_title="Niveaux",
        yaxis_title=selected_time_spent,
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode="linear", dtick=1),
    )

    # Extraire les scores des étoiles
    base_dir = os.path.join("tableau_de_bord", "Levels", "Levels")
    star_scores = extract_scores(base_dir)
    # print("blabababa", star_scores)
    star_data = []
    player_star_data = []
    # max_score_by_level = df['Max Score'].to_dict()
    # print("bbbbb",max_score_by_level)# Convert Series to dictionary for faster lookup
    for Scénario, levels in star_scores.items():
        for level, stars in levels.items():
            transformed_level = level.replace("Niveau", "mission")
            star_data.append(
                {
                    "Scénario": Scénario,
                    "Level": transformed_level,
                    "Score to get 2 Stars": stars[0],
                    "Score to get 3 Stars": stars[1],
                }
            )
            # Determine the number of stars the player has achieved using max_score_by_level
            # transformed_level = level.replace("Niveau", "mission")
            max_score = max_score_by_level.get(transformed_level, 0)
            # print("level", transformed_level)
            # print("max_score", max_score_by_level)
            # print("max_score_by_level", max_score)
            player_stars = 0
            if max_score >= stars[1]:
                player_stars = 3
            if max_score >= stars[0] and max_score < stars[1]:
                player_stars = 2
            player_star_data.append(
                {
                    "Scénario": Scénario,
                    "Level": transformed_level,
                    "Nombre d'étoiles du joueur par scénario": player_stars,
                }
            )

    df_stars = pd.DataFrame(star_data)
    # print("bbbbbbb",player_star_data)
    player_star_data = [
        entry
        for entry in player_star_data
        if not (
            entry["Scénario"] == "Infiltration"
            and entry["Level"] in [f"mission0{i}" for i in range(1, 9)]
        )
    ]
    print("player_star_data", player_star_data)
    df_player_stars = pd.DataFrame(
        player_star_data
    )  # New DataFrame for Nombre d\'étoiles du joueur par scénario
    # print("blueblue",star_data)
    df_stars = pd.DataFrame(star_data)

    # print("greengreen", df_stars)

    fig_player_stars = px.bar(
        df_player_stars,
        x="Level",
        y="Nombre d'étoiles du joueur par scénario",
        color="Scénario",
        title="Nombre d'étoiles obtenues par niveau",
        text="Nombre d'étoiles du joueur par scénario",
    )
    fig_player_stars.update_traces(texttemplate="%{text}", textposition="inside")
    fig_player_stars.update_layout(
        xaxis_title="Niveaux",
        yaxis_title="Nombre d'étoiles obtenues",
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode="linear", dtick=1),
    )

    total_stars_data = []
    for scenario, levels in star_scores.items():
        total_stars = len(levels) * 3  # 3 stars per level
        player_stars = sum(
            [
                player_star_data[i]["Nombre d'étoiles du joueur par scénario"]
                for i in range(len(player_star_data))
                if player_star_data[i]["Scénario"] == scenario
            ]
        )
        total_stars_data.append(
            {
                "Scénario": scenario,
                "Nombre d'étoiles total par scénario": total_stars,
                "Nombre d'étoiles du joueur par scénario": player_stars,
            }
        )

    df_total_stars = pd.DataFrame(total_stars_data)

    # Create a graph comparing Nombre d\'étoiles du joueur par scénario to Nombre d\'étoiles total par scénario required
    fig_total_stars = px.bar(
        df_total_stars,
        x="Scénario",
        y=[
            "Nombre d'étoiles du joueur par scénario",
            "Nombre d'étoiles total par scénario",
        ],
        barmode="group",
        title="Progression du joueur en termes d'étoiles",
        text_auto=True,
    )

    # Update the layout to differentiate the bars
    fig_total_stars.update_traces(
        marker=dict(line=dict(width=1.5, color="DarkSlateGrey"))
    )
    fig_total_stars.update_layout(
        xaxis_title="Scénarios",
        yaxis_title="Nombre d'étoiles",
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode="linear", dtick=1),
        legend_title_text="Type d'étoiles",
        legend=dict(x=0.5, y=1.1, orientation="h", xanchor="center"),
    )
    # fig_combined1 = px.bar(df_stars, x='Level', y=['Max Score', 'Score to get 2 Stars'], barmode='group', color='Scénario', title='Comparaison du score maximum et du score nécessaire pour obtenir 2 étoiles')
    # fig_combined1.update_traces(texttemplate='%{text}', textposition='outside')
    # fig_combined1.update_layout(
    # xaxis_title='Niveaux',
    # yaxis_title='Scores',
    # margin=dict(l=40, r=40, t=40, b=40),
    # yaxis=dict(tickmode='linear', dtick=1)
    # )

    return (
        fig_avg_score,
        fig_max_score,
        fig_completed_counts,
        fig_time_spent,
        fig_player_stars,
        fig_total_stars,
    )


if __name__ == "__main__":
    app.run_server(debug=True)
