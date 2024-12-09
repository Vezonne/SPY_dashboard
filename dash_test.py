import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Créer une application Dash
app = dash.Dash(__name__)

# Layout de l'application
app.layout = html.Div(
    [
        dcc.Input(id="input", value="Dash", type="text"),  # Champ de saisie
        html.Div(id="output"),  # Zone d'affichage
    ]
)


# Callback pour mettre à jour la sortie en fonction de l'entrée
@app.callback(Output("output", "children"), Input("input", "value"))
def update_output(value):
    return f"Vous avez entré : {value}"


# Lancer le serveur
if __name__ == "__main__":
    app.run_server(debug=True)
