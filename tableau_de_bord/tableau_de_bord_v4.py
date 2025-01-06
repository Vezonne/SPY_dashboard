import dash
from dash import dcc, html
import plotly.express as px
from dash.dependencies import Input, Output
import pandas as pd
from lrs_request import fetch_lrs_data, process_data, calculate_time_per_level

# Récupérer et traiter les données du joueur
data = fetch_lrs_data("BA47A4CF")
df, all_mission_levels, completed_counts, avg_score_by_level = process_data(data)
time_spent_max, time_spent_min, time_spent_avg = calculate_time_per_level(df)

# Arrondir les valeurs des dictionnaires à 3 décimales
time_spent_max = {k: round(v, 3) for k, v in time_spent_max.items()}
time_spent_min = {k: round(v, 3) for k, v in time_spent_min.items()}
time_spent_avg = {k: round(v, 3) for k, v in time_spent_avg.items()}

df_time_spent_max = pd.DataFrame(list(time_spent_max.items()), columns=['Mission Level', 'Max Time Spent'])
df_time_spent_min = pd.DataFrame(list(time_spent_min.items()), columns=['Mission Level', 'Min Time Spent'])
df_time_spent_avg = pd.DataFrame(list(time_spent_avg.items()), columns=['Mission Level', 'Average Duration'])

print("completed_counts", completed_counts)
print("time_spent_max", time_spent_max)
print("time_spent_min", time_spent_min)
print("time_spent_avg", time_spent_avg)

app = dash.Dash(__name__, external_stylesheets=['/assets/style.css'])

app.layout = html.Div(children=[
    html.H1(children='Tableau de Bord des métriques essentielles du joueur par niveau'),
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
])

@app.callback(
    Output('graph-avg-score', 'figure'),
    Input('menu-deroulant-time-spent', 'value')
)
def update_graph_avg_score(_):
    df_avg_score = pd.DataFrame(list(avg_score_by_level.items()), columns=['Mission Level', 'Average Score'])
    fig = px.bar(df_avg_score, x='Mission Level', y='Average Score', title='Score moyen par niveau', text='Average Score')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        xaxis_title='Niveaux',
        yaxis_title='Average Score',
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode='linear', dtick=1)
    )
    return fig

@app.callback(
    Output('graph-completed-counts', 'figure'),
    Input('menu-deroulant-time-spent', 'value')
)
def update_graph_completed_counts(_):
    df_completed_counts = pd.DataFrame(list(completed_counts.items()), columns=['Mission Level', 'Completed Count'])
    fig = px.bar(df_completed_counts, x='Mission Level', y='Completed Count', title='Nombre de niveaux complétés', text='Completed Count')
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        xaxis_title='Niveaux',
        yaxis_title='Completed Count',
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode='linear', dtick=1)
    )
    return fig

@app.callback(
    Output('graph-time-spent', 'figure'),
    Input('menu-deroulant-time-spent', 'value')
)
def update_graph_time_spent(selected_time_spent):
    if selected_time_spent == 'Max Time Spent':
        fig = px.bar(df_time_spent_max, x='Mission Level', y='Max Time Spent', title='Temps passé maximum par niveau', text='Max Time Spent')
    elif selected_time_spent == 'Min Time Spent':
        fig = px.bar(df_time_spent_min, x='Mission Level', y='Min Time Spent', title='Temps passé minimum par niveau', text='Min Time Spent')
    elif selected_time_spent == 'Average Duration':
        fig = px.bar(df_time_spent_avg, x='Mission Level', y='Average Duration', title='Temps moyen passé par niveau', text='Average Duration')
    #else:
    #    fig = px.bar(df, x='Mission Level', y='Score', title=f'{selected_time_spent}', text='Score')
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        xaxis_title='Niveaux',
        yaxis_title=selected_time_spent,
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis=dict(tickmode='linear', dtick=1)
    )
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)