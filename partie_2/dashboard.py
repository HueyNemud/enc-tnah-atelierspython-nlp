from functools import lru_cache
import dash
import dash_bootstrap_components as dbc
from dash import html
import folium
import spacy
import requests
from folium.plugins import HeatMap


# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Load the French model of spaCy
nlp = spacy.load("../partie_1/ner_presse_ancienne/model-best")


# Create a Folium map centered on France
m = folium.Map(location=[48.8566, 2.3522], zoom_start=6, width="100%", height="100%")
map_html = m._repr_html_()

# Layout of the app
app.layout = dbc.Container(
    [
        dbc.Row(
            # Add a form with a field to enter an URL
            [
                dbc.Col(
                    [
                        dbc.CardGroup(
                            [
                                dbc.Input(
                                    id="url-input",
                                    placeholder="Enter URL",
                                    type="text",
                                    value="https://gallica.bnf.fr/ark:/12148/bpt6k661732w/f1",
                                ),
                            ]
                        ),
                        dbc.Button("Submit", id="submit-button", color="primary"),
                    ],
                    width=12,
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Iframe(
                            id="folium-map",
                            srcDoc=map_html,
                            width="100%",
                            height="800px",  # Or '100%' depending on the full viewport height
                        )
                    ],
                    width=6,
                ),
                dbc.Col(
                    [
                        html.Iframe(
                            id="spacy-output",
                            srcDoc="",
                            width="100%",
                            height="800px",
                        )
                    ],
                    width=6,
                ),
            ]
        ),
    ],
    fluid=True,
)


# Add lru_cache to avoid fetching the same URL multiple times
@lru_cache
def fetch_gallica(url):
    # Si l'URL ne termine pas par .texteBrut, on ajoute cette extension
    if not url.endswith(".texteBrut"):
        url += ".texteBrut"

    # On envoie une requête GET à l'URL
    response = requests.get(url)

    # raise for status va lever une exception si le code de statut HTTP n'est pas 200
    response.raise_for_status()

    # Sinon, récupérer le contenu de la réponse
    content = response.text

    # Et conserve uniquement se qui se trouve après le premier <hr>. Avant, c'est l'en-tête ajouté par Gallica
    content = content.split("<hr>", 1)[1]

    return content


def spacy_ner(content):
    doc = nlp(content)

    return doc


# Complétez-moi ! 🏗️

from functools import cache
from typing import Any


@cache  # On active la mise en cache pour cette fonction, cf. l'astuce précédente
def dbpedia_top1(toponyme: str) -> str | None:
    r = dbpedia_lookup(toponyme)
    if not r:
        return None
    else:
        return r[0].get("resource")[0]


@cache
def dbpedia_lookup(toponyme: str) -> list[dict[str, Any]]:
    query = f"https://fr.dbpedia.org/lookup/api/search?query={toponyme}&format=JSON"
    response = requests.get(query)
    response.raise_for_status()
    return response.json().get("docs", [])


@cache  # Mise en cache, les requêtes SPARQL sont coûteuses en temps !
def geocode(uri: str) -> tuple[float, float]:

    # Le patron de requête SPARQL: l'URI sera substituée à la place de %s par l'argument de la fonction
    sparql_template = """PREFIX geo: <http://www.w3.org/2003/01/geo/wgs84_pos#> SELECT ?lat ?long WHERE {<%s> (geo:lat) ?lat ; (geo:long) ?long. }"""

    # On substitue l'URI dans le template de requête SPARQL en utilisant le formatage ancien de Python plutôt que les f-strings car la requête SPARQL contient déjà des accolades.
    sparql_query = sparql_template % uri

    http_headers = {
        "Content-Type": "application/sparql-query",
        "Accept": "application/json",
    }
    response = requests.post(
        "http://fr.dbpedia.org/sparql", headers=http_headers, data=sparql_query
    )
    response.raise_for_status()
    json_response = response.json()

    # Récupérer l'élément results -> bindings dans l'objet json_response
    # ⚠️ ATTENTION : l'élement "bindings" est une liste, donc l'argument par défaut pour get("bindings") doit être une liste vide => get("bindings", [])
    bindings = json_response.get("results", {}).get("bindings", [])

    # Si la liste "bindings" est vide, lat et long seront None
    if not bindings:
        return None, None

    # Sinon, le premier élément de la liste "bindings" est un dictionnaire contenant les valeurs de lat et long
    bindings = bindings[0]

    # Récupérer la valeur de latitude dans : lat -> value
    lat = bindings.get("lat", {}).get("value", None)

    # Récupérer la valeur de longitude dans : long -> value
    long = bindings.get("long", {}).get("value", None)

    # lat et long sont récupérés en tant que chaînes de caractères, on les convertit en float
    lat = float(lat) or None
    long = float(long) or None

    return lat, long


def resolution(toponyme: str) -> tuple[float, float]:

    uri = dbpedia_top1(toponyme)
    print(f"{toponyme=} => {uri=}", end="")

    if not uri:
        lat, long = None, None
    else:
        lat, long = geocode(uri)

    print(f" => {lat=}, {long=}")
    return lat, long


def geocode_texte(
    text: str, nlp: spacy.language.Language
) -> tuple[list[str], list[tuple[float, float]]]:
    doc = nlp(text)
    loc = [ent.text for ent in doc.ents if ent.label_ == "LOC"]
    coordonnees = [resolution(toponyme) for toponyme in loc]
    return loc, coordonnees


# ---
# Callback principal !


@app.callback(
    dash.dependencies.Output("folium-map", "srcDoc"),
    dash.dependencies.Output("spacy-output", "srcDoc"),
    [dash.dependencies.Input("submit-button", "n_clicks")],
    [dash.dependencies.State("url-input", "value")],
    prevent_initial_call=True,  # Key setting to prevent the callback on page load
)
def fetch_and_map(n_clicks, url):

    print("Fetching", url)
    content = fetch_gallica(url)

    doc = nlp(content)
    loc = [ent.text for ent in doc.ents if ent.label_ == "LOC"]
    coordonnees = [resolution(toponyme) for toponyme in loc]
    coordonnees_valides = [(lat, long) for lat, long in coordonnees if lat and long]

    print("Building the map")
    folium_map = folium.Map(
        location=[
            48.8566,
            2.3522,
        ],  # On précise les coordonnées du centre de la carte...
        zoom_start=3,  # ... et le niveau de zoom initial. 0 = vue du monde, 18 = vue très rapprochée
    )
    HeatMap(coordonnees_valides).add_to(folium_map)

    map_html = folium_map._repr_html_()
    spacy_html = spacy.displacy.render(doc, style="ent")

    print("Ready for display !")
    return map_html, spacy_html


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
