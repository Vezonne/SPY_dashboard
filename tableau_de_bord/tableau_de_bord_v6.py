import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from lrs_request import fetch_lrs_data, process_data, calculate_time_per_level

app = dash.Dash(__name__, external_stylesheets=['/assets/style.css'])

app.layout = html.Div(children=[
    html.H1(children='Tableau de Bord des métriques essentielles du joueur par niveau'),
    html.Div(children=[
        dcc.Input(id='username-input', type='text', placeholder='Entrer un nom d\'utilisateur', style={'margin-right': '10px'}),
        html.Button('Entrer', id='submit-button', n_clicks=0),
        dcc.Dropdown(
            id='menu-deroulant-scenario',
            options=[],  # Les options seront mises à jour dynamiquement
            placeholder='Sélectionner un scénario',
            style={'width': '50%', 'margin-top': '20px'}
        )
    ], style={'text-align': 'center', 'margin-bottom': '20px'}),
    html.Div(id='output-container', children=[
        html.Div(className='graph-container', children=[
            dcc.Graph(id='graph-avg-score'),
            dcc.Graph(id='graph-completed-counts'),
            html.Div(className='dropdown-container', children=[
                dcc.Dropdown(
                    id='menu-deroulant-time-spent',
                    options=[
                        {'label': 'Temps passé maximum par niveau', 'value': 'Max Time Spent'},
                        {'label': 'Temps passé minimum par niveau', 'value': 'Min Time Spent'},
                        {'label': 'Temps moyen passé par niveau', 'value': 'Average Duration'}
                    ],
                    value='Max Time Spent',  # Par défaut, afficher le temps passé maximum par niveau
                    style={'width': '50%'}
                )
            ]),
            dcc.Graph(id='graph-time-spent')
        ], style={'display': 'flex', 'flex-direction': 'column'})
    ]),
    html.Script(src='/assets/script.js')
])

@app.callback(
    Output('menu-deroulant-scenario', 'options'),
    [Input('submit-button', 'n_clicks')],
    [State('username-input', 'value')]
)
def update_scenario_options(n_clicks, username):
    if not username:
        return []

    data = fetch_lrs_data(username)
    df, _, _, _ = process_data(data)

    # Générer les options pour le menu déroulant des scénarios
    scenarios = df['Scenario'].dropna().unique()
    # Exclude scenarios starting with 'erty' or 'plok'
    scenarios = [scenario for scenario in scenarios if not scenario.startswith(('erty', 'plok'))]
    scenario_options = [{'label': scenario, 'value': scenario} for scenario in scenarios]

    return scenario_options

@app.callback(
    [Output('graph-avg-score', 'figure'),
     Output('graph-completed-counts', 'figure'),
     Output('graph-time-spent', 'figure')],
    [Input('menu-deroulant-scenario', 'value'),
     Input('menu-deroulant-time-spent', 'value')],
    [State('username-input', 'value')]
)
def update_graphs(selected_scenario, selected_time_spent, username):
    if not username or not selected_scenario:
        return {}, {}, {}

    data = fetch_lrs_data(username)
    df, all_mission_levels, completed_counts, avg_score_by_level = process_data(data)

    df = df[df['Scenario'] == selected_scenario]

    time_spent_max, time_spent_min, time_spent_avg = calculate_time_per_level(df)

    # Arrondir les valeurs des dictionnaires à 3 décimales
    time_spent_max = {k: round(v, 3) for k, v in time_spent_max.items()}
    time_spent_min = {k: round(v, 3) for k, v in time_spent_min.items()}
    time_spent_avg = {k: round(v, 3) for k, v in time_spent_avg.items()}

    df_time_spent_max = pd.DataFrame(list(time_spent_max.items()), columns=['Mission Level', 'Max Time Spent'])
    df_time_spent_min = pd.DataFrame(list(time_spent_min.items()), columns=['Mission Level', 'Min Time Spent'])
    df_time_spent_avg = pd.DataFrame(list(time_spent_avg.items()), columns=['Mission Level', 'Average Duration'])

    df_avg_score = pd.DataFrame(list(avg_score_by_level.items()), columns=['Mission Level', 'Average Score'])
    fig_avg_score = px.bar(df_avg_score, x='Mission Level', y='Average Score', title='Score moyen par niveau', text='Average Score')
    fig_avg_score.update_traces(texttemplate='%{text}', textposition='outside')
    fig_avg_score.update_layout(
        xaxis_title='Niveaux',
        yaxis_title='Average Score',
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode='linear', dtick=1)
    )

    df_completed_counts = pd.DataFrame(list(completed_counts.items()), columns=['Mission Level', 'Completed Count'])
    fig_completed_counts = px.bar(df_completed_counts, x='Mission Level', y='Completed Count', title='Nombre de niveaux complétés', text='Completed Count')
    fig_completed_counts.update_traces(texttemplate='%{text}', textposition='outside')
    fig_completed_counts.update_layout(
        xaxis_title='Niveaux',
        yaxis_title='Completed Count',
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode='linear', dtick=1)
    )

    if selected_time_spent == 'Max Time Spent':
        fig_time_spent = px.bar(df_time_spent_max, x='Mission Level', y='Max Time Spent', title='Temps passé maximum par niveau', text='Max Time Spent')
    elif selected_time_spent == 'Min Time Spent':
        fig_time_spent = px.bar(df_time_spent_min, x='Mission Level', y='Min Time Spent', title='Temps passé minimum par niveau', text='Min Time Spent')
    elif selected_time_spent == 'Average Duration':
        fig_time_spent = px.bar(df_time_spent_avg, x='Mission Level', y='Average Duration', title='Temps moyen passé par niveau', text='Average Duration')

    fig_time_spent.update_traces(texttemplate='%{text}', textposition='outside')
    fig_time_spent.update_layout(
        xaxis_title='Niveaux',
        yaxis_title=selected_time_spent,
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode='linear', dtick=1)
    )

    return fig_avg_score, fig_completed_counts, fig_time_spent

if __name__ == '__main__':
    app.run_server(debug=True)