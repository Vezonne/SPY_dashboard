# Tableau de Bord des Métriques Essentielles du Joueur

Ce projet implémente un tableau de bord interactif pour visualiser les métriques essentielles des joueurs par niveau. Il utilise Dash et Plotly pour créer des graphiques dynamiques basés sur les données extraites des fichiers XML stockés dans le dossier `Levels/Levels` et du LRS.

## Structure du Projet

- `tableau_final.py`: Fichier principal qui configure et lance le tableau de bord Dash.
- `lrs_request.py`: Fichier contenant les fonctions pour récupérer et traiter les données depuis un Learning Record Store (LRS).
- `score.py`: Fichier contenant les fonctions pour extraire les scores et les seuils des fichiers XML.
- `Levels/Levels`: Dossier contenant les fichiers XML des niveaux pour chaque scénario.

## Prérequis

- Python 3.x
- Bibliothèques Python : `requests`, `pandas`, `dash`, `plotly`, `xml.etree.ElementTree`

Vous pouvez installer les bibliothèques nécessaires en utilisant pip :

```bash
pip install requests pandas dash plotly
```

Ou faire un environnemt conda avec :

```bash
conda env create -f dashboard.yml
```

## Utilisation

### 1. Extraction des Scores

Le fichier `score.py` contient la fonction `extract_scores` qui extrait les scores et les seuils des fichiers XML dans le dossier `Levels/Levels`.

```python
from score import extract_scores

base_directory = "tableau_de_bord/Levels"
scores = extract_scores(base_directory)
print(scores)
```

### 2. Récupération des Données depuis le LRS

Le fichier `lrs_request.py` contient les fonctions pour récupérer et traiter les données depuis un LRS.

- `fetch_lrs_data(agent_name)`: Récupère les données pour un utilisateur donné.
- `process_data(data)`: Traite les données récupérées pour extraire les métriques essentielles.
- `calculate_time_per_level(df)`: Calcule le temps passé par niveau.

### 3. Lancement du Tableau de Bord

Le fichier `tableau_final.py` configure et lance le tableau de bord Dash. Il utilise les fonctions définies dans `lrs_request.py` et `score.py` pour extraire et traiter les données, puis crée des graphiques interactifs pour visualiser les métriques.

Pour lancer le tableau de bord, exécutez le fichier `tableau_final.py` :

```bash
python tableau_final.py
```

### 4. Utilisation du Tableau de Bord

- Entrez un nom d'utilisateur dans le champ prévu à cet effet et cliquez sur "Entrer".
- Sélectionnez un scénario dans le menu déroulant pour afficher les métriques correspondantes.
- Utilisez le menu déroulant pour sélectionner le type de temps passé à afficher (maximum, minimum, moyen).

### 5. Structure des Fichiers XML

Les fichiers XML dans le dossier `Levels/Levels` doivent contenir des éléments `<score>` avec les attributs `twoStars` et `threeStars` pour que les scores soient correctement extraits.

Exemple de fichier XML :

```xml
<level>
    <score twoStars="5000" threeStars="8000" />
</level>
```

## Exemple de Code

Voici un exemple de code pour extraire les scores et lancer le tableau de bord :

```python
from score import extract_scores
from lrs_request import fetch_lrs_data, process_data, calculate_time_per_level
import pandas as pd
import plotly.express as px
from dash import dcc, html, Dash
from dash.dependencies import Input, Output, State

# Extraire les scores
base_directory = "tableau_de_bord/Levels"
scores = extract_scores(base_directory)
print(scores)

# Lancer le tableau de bord
app = Dash(__name__, external_stylesheets=['/assets/style.css'])

# Configuration et lancement du tableau de bord
if __name__ == '__main__':
    app.run_server(debug=True)
```

## Conclusion

Ce projet fournit un tableau de bord interactif pour visualiser les métriques essentielles des joueurs par niveau. En suivant les instructions ci-dessus, vous pouvez extraire les scores des fichiers XML, récupérer les données depuis un LRS, et lancer le tableau de bord pour visualiser les données.
