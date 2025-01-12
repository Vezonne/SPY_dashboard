import requests
import pandas as pd
import dash
import json
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import warnings

warnings.filterwarnings("ignore", message=".*NotOpenSSLWarning.*")

ENDPOINT = "https://lrsels.lip6.fr/data/xAPI/statements"
HEADERS = {"X-Experience-API-Version": "1.0.3"}
AUTH = (
    "9fe9fa9a494f2b34b3cf355dcf20219d7be35b14",
    "b547a66817be9c2dbad2a5f583e704397c9db809",
)
NAME = "59F2BF0"


def fetch_lrs_data(agent_name):
    agent = {"account": {"homePage": "https://www.lip6.fr/mocah/", "name": agent_name}}
    params = {
        "agent": json.dumps(agent),  # Convertir l'objet Python en JSON
        "limit": 500,
    }
    response = requests.get(ENDPOINT, headers=HEADERS, auth=AUTH, params=params)
    if response.status_code == 200:
        return response.json()["statements"]
    else:
        raise Exception(f"Error fetching data: {response.status_code}, {response.text}")


def process_data(data):
    records = []
    last_mission_level = None
    all_mission_levels = set()
    completed_counts = {}
    score_by_level = {}

    for statement in data:
        try:
            success = statement.get("result", {}).get("success", False)
            score = (
                statement.get("result", {})
                .get("extensions", {})
                .get("https://spy.lip6.fr/xapi/extensions/score", None)
            )

            if not success:
                score = None

            if score:
                if isinstance(score, list) and len(score) > 0:
                    score = score[0]

                if isinstance(score, str):
                    score = float(score)

                if isinstance(score, (int, float)):
                    score = float(score)
                else:
                    score = None
            else:
                score = None

            mission_level = None
            scenario = None
            if "object" in statement:
                object_data = statement["object"]
                if "definition" in object_data:
                    definition = object_data["definition"]
                    if "extensions" in definition:
                        extensions = definition["extensions"]
                        if (
                            "https://w3id.org/xapi/seriousgames/extensions/progress"
                            in extensions
                        ):
                            mission_level = extensions[
                                "https://w3id.org/xapi/seriousgames/extensions/progress"
                            ][0]
                        if "https://spy.lip6.fr/xapi/extensions/context" in extensions:
                            scenario = extensions[
                                "https://spy.lip6.fr/xapi/extensions/context"
                            ][0]

            if mission_level is None and last_mission_level is not None:
                mission_level = last_mission_level

            if mission_level is not None:
                last_mission_level = mission_level
                all_mission_levels.add(mission_level)

                verb = statement["verb"]["id"].split("/")[-1]
                if verb == "completed":
                    if mission_level not in completed_counts:
                        completed_counts[mission_level] = 0
                    completed_counts[mission_level] += 1

                if mission_level not in score_by_level:
                    score_by_level[mission_level] = []
                if score is not None:
                    score_by_level[mission_level].append(score)

            records.append(
                {
                    "Timestamp": statement.get("timestamp"),
                    "Verb": statement["verb"]["id"].split("/")[-1],
                    "Actor": statement["actor"].get("name", "Unknown"),
                    "Object": statement["object"].get("id", "Unknown"),
                    "Score": score,
                    "Mission Level": mission_level,
                    "Scenario": scenario,
                }
            )
        except Exception as e:
            continue

        avg_score_by_level = {
            level: round(sum(scores) / len(scores)) if len(scores) > 0 else None
            for level, scores in score_by_level.items()
        }
        max_score_by_level = {
            level: max(scores) if len(scores) > 0 else None
            for level, scores in score_by_level.items()
        }

    df = pd.DataFrame(records)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    print(df)
    return (
        df,
        list(all_mission_levels),
        completed_counts,
        avg_score_by_level,
        max_score_by_level,
    )


def calculate_time_per_level(df):
    if df["Mission Level"].isnull().all():
        # print("Aucun niveau détecté dans les données.")
        return pd.DataFrame(columns=["Mission Level", "Time Spent (min)"])

    # Fonction pour convertir les timestamps en minutes écoulées
    def timestamps_to_minutes(group):
        base_time = group.min()  # Prend le premier Timestamp (le plus petit)
        return (group - base_time).dt.total_seconds() / 60  # Convertit en minutes

    # Regrouper par "Mission Level" et calculer la liste de minutes écoulées
    minutes_per_level = (
        df.dropna(subset=["Mission Level"])  # Supprime les lignes sans niveau
        .groupby("Mission Level")["Timestamp"]
        .apply(
            lambda x: list(timestamps_to_minutes(x))
        )  # Applique la conversion pour chaque groupe
        .reset_index(name="Minutes Elapsed")
    )

    # Retirer les valeurs de minutes égales à 0
    minutes_per_level["Minutes Elapsed"] = minutes_per_level["Minutes Elapsed"].apply(
        lambda x: [
            t for t in x if t > 0.05
        ]  # Filtrer les valeurs supérieures à 3 seconds
    )

    # Calculer le temps total passé (durée maximale pour chaque Mission Level)
    minutes_per_level["Max Time Spent"] = minutes_per_level["Minutes Elapsed"].apply(
        lambda x: max(x) if len(x) > 0 else 0
    )

    # Fixer un seuil minimal en minutes
    min_threshold = 0.01

    # Récupérer la durée minimale au-dessus du seuil
    minutes_per_level["Min Time Spent"] = minutes_per_level["Minutes Elapsed"].apply(
        lambda x: min(
            [t for t in x if t > min_threshold], default=None
        )  # Filtrer les valeurs au-dessus du seuil
    )

    # Ajouter le temps moyen pour chaque "Mission Level"
    minutes_per_level["Average Duration"] = minutes_per_level["Minutes Elapsed"].apply(
        lambda x: sum(x) / len(x) if len(x) > 0 else 0  # Calcule la moyenne des durées
    )

    # Définir une limite arbitraire (e.g., 24 heures en minutes)
    threshold = 24 * 60

    # Identifier les anomalies où le temps passé dépasse le seuil
    anomalies = minutes_per_level[minutes_per_level["Max Time Spent"] > threshold]

    if not anomalies.empty:
        # print("Anomalies détectées :")
        # print(anomalies)

        # Filtrer les données pour ne garder que les lignes conformes
        minutes_per_level = minutes_per_level[
            minutes_per_level["Max Time Spent"] <= threshold
        ]

    # print("Contenu final de time_spent :")
    # print(minutes_per_level)

    time_spent_max = dict(
        zip(minutes_per_level["Mission Level"], minutes_per_level["Max Time Spent"])
    )
    time_spent_min = dict(
        zip(minutes_per_level["Mission Level"], minutes_per_level["Min Time Spent"])
    )
    time_spent_avg = dict(
        zip(minutes_per_level["Mission Level"], minutes_per_level["Average Duration"])
    )

    return time_spent_max, time_spent_min, time_spent_avg


def main():
    data = fetch_lrs_data(NAME)
    df, all_mission_levels, completed_counts, avg_score_by_level, max_score_by_level = (
        process_data(data)
    )
    time_spent = calculate_time_per_level(df)
    # print("Niveaux de mission :", all_mission_levels)
    # print("Comptage des niveaux de mission :", completed_counts)
    # print("Score moyen par niveau de mission :", avg_score_by_level)
    # print("Temps passé par niveau de mission :", time_spent)


if __name__ == "__main__":
    main()
