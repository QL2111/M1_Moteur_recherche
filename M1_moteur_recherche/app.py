import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import json
from ast import literal_eval #stack overflow, convertir une liste stocker en string en liste

# Charger les données depuis le fichier JSON
with open('corpus.json', 'r') as json_file:
    data = json.load(json_file)

# Convertir les données en DataFrame pour les documents et les auteurs
df_documents = pd.DataFrame(data["id2doc"]).T
df_documents['nbCommentaire'] = pd.to_numeric(df_documents['nbCommentaire'])  # Convertir en type numérique

df_auteurs = pd.DataFrame(data["id2aut"]).T

# Filtrer les documents par type (Reddit et Arvix)
df_reddit = df_documents[df_documents['_Document__type'] == 'Reddit']
df_arvix = df_documents[df_documents['_Document__type'] == 'Arxiv']
df_arvix.coAuteurs = df_arvix.coAuteurs.apply(literal_eval) #stack overflow, convertir une liste stocker en string en liste

# print(df_arvix)

# Initialiser l'application Dash
app = dash.Dash(__name__)

# Créer une figure pour la visualisation des documents Reddit
fig_reddit = px.scatter(df_reddit, x='date', y='nbCommentaire', color='auteur', title='Visualisation des documents Reddit', hover_data=['titre'])

# Créer une figure pour la visualisation des documents Arvix
fig_arvix = px.scatter(df_arvix, x='date', y=df_arvix['coAuteurs'].apply(len), color='auteur', title='Visualisation des documents Arvix', hover_data=['titre'])
# Créer une figure pour la visualisation du corpus
fig_corpus = px.histogram(df_documents, x='date', title='Visualisation du corpus')

# Créer une figure pour la répartition des types de documents
fig_types = px.histogram(df_documents, x='_Document__type', title='Répartition des types de documents')

# Créer une figure pour la production de chaque auteur
fig_auteurs_production = px.bar(df_auteurs['ndoc'], x=df_auteurs.index, y=df_auteurs['ndoc'],
                                 title='Production de chaque auteur', labels={'y': 'Nombre de documents produits'})

# Disposition de l'interface Dash
# Thèmes CSS
app.layout = html.Div(style={'fontFamily': 'Arial, sans-serif'}, children=[
    html.H1("Exploration du Corpus", style={'textAlign': 'center', 'color': '#333'}),
    
    html.Div(children=[
        dcc.Graph(figure=fig_reddit, id='graph-reddit-documents'),
    ], style={'marginBottom': '30px'}),

    html.Div(children=[
        dcc.Graph(figure=fig_arvix, id='graph-arvix-documents'),
    ], style={'marginBottom': '30px'}),
    

    html.Div(children=[
        dcc.Graph(figure=fig_corpus, id='graph-corpus'),
    ], style={'marginBottom': '30px'}),

    html.Div(children=[
        dcc.Graph(figure=fig_types, id='graph-types'),
    ], style={'marginBottom': '30px'}),
    
    html.Div(children=[
        html.Label("Titre du document :", style={'fontSize': '18px'}),
        dcc.Input(id='titre-input', type='text', value='', placeholder='Entrez le titre', style={'width': '100%', 'fontSize': '16px'}),
        html.Button('Afficher le texte correspondant', id='text-button', n_clicks=0, style={'marginTop': '10px', 'fontSize': '16px'}),
        html.Div(id='text-output', style={'marginTop': '10px', 'fontSize': '16px'}),
    ], style={'marginBottom': '30px'}),
    
    html.Div(children=[
        html.Label("Voir les titres des textes du corpus :", style={'fontSize': '18px'}),
        dcc.Dropdown(
            id='corpus-titres-dropdown',
            options=[{'label': titre, 'value': titre} for titre in df_documents['titre']],
            multi=True,
            value=df_documents['titre'].values,
            style={'width': '100%', 'fontSize': '16px'}
        ),
        dcc.Graph(id='corpus-titres-graph'),
    ]),
    
    html.Div(children=[
        html.H2("Exploration des Auteurs", style={'textAlign': 'center', 'color': '#333', 'marginTop': '50px'}),
        html.Div(children=[
            dcc.Graph(figure=fig_auteurs_production, id='graph-auteurs-production'),
        ], style={'marginBottom': '30px'}),
        
        html.Div(children=[
            html.Label("Nom de l'auteur pour afficher le titre, le texte de sa production et potentiellement ses co-auteurs ", style={'fontSize': '18px'}),
            dcc.Dropdown(
                id='auteur-dropdown',
                options=[{'label': auteur, 'value': auteur} for auteur in df_documents['auteur'].unique()],
                value=df_documents['auteur'].iloc[0],
                style={'width': '100%', 'fontSize': '16px'}
            ),
            html.Div(children=[
                html.Label("Titre du document produit par l'auteur :", style={'fontSize': '18px'}),
                html.Div(id='titre-auteur-output', style={'fontSize': '16px'}),
            ], style={'marginTop': '20px'}
            ),
            html.Div(children=[
                html.Label("Texte du document produit par l'auteur :", style={'fontSize': '18px'}),
                html.Div(id='texte-auteur-output', style={'fontSize': '16px'}),
            ], style={'marginTop': '20px', 'marginBottom': '2rem'}
            ),
            html.Div(children=[
                html.Label("Les co-auteurs de l'auteur :", style={'fontSize': '18px'}),
                html.Div(id='coauteurs-auteur-output', style={'fontSize': '16px'}),
            ], style={'marginTop': '20px', 'marginBottom': '2rem'}
            ),
            
        ]),
    ]),
])

# Callback pour afficher le texte correspondant au titre entré
@app.callback(
    Output('text-output', 'children'),
    [Input('text-button', 'n_clicks')],
    [dash.dependencies.State('titre-input', 'value')]
)
def display_text(n_clicks, titre):
    if n_clicks > 0:
        selected_doc = df_documents[df_documents['titre'] == titre]
        if not selected_doc.empty:
            return selected_doc.iloc[0]['texte']
        else:
            return "Aucun document trouvé avec ce titre."

# Callback pour mettre à jour le graphique des titres du corpus
@app.callback(
    Output('corpus-titres-graph', 'figure'),
    [Input('corpus-titres-dropdown', 'value')]
)
def update_corpus_titres_graph(selected_titres):
    filtered_df = df_documents[df_documents['titre'].isin(selected_titres)]
    fig = px.bar(filtered_df['nbCommentaire'], x=filtered_df['titre'], y=filtered_df['nbCommentaire'],
                 title='Visualisation des titres du corpus', labels={'y': 'Nombre de commentaires'})
    return fig

# Callback pour afficher le titre du document produit par l'auteur sélectionné
@app.callback(
    Output('titre-auteur-output', 'children'),
    [Input('auteur-dropdown', 'value')]
)
def display_titre_auteur(auteur):
    selected_doc = df_documents[df_documents['auteur'] == auteur].iloc[0]
    return selected_doc['titre']

# Callback pour afficher le texte du document produit par l'auteur sélectionné
@app.callback(
    Output('texte-auteur-output', 'children'),
    [Input('auteur-dropdown', 'value')]
)
def display_texte_auteur(auteur):
    selected_doc = df_documents[df_documents['auteur'] == auteur].iloc[0]
    return selected_doc['texte']

# Callback pour afficher les coauteurs de l'auteur sélectionné
@app.callback(
    Output('coauteurs-auteur-output', 'children'),
    [Input('auteur-dropdown', 'value')]
)
def display_coauteurs(selected_auteur):
    coauteurs_list = df_arvix[df_arvix['auteur'] == selected_auteur]['coAuteurs']
    chaine_coauteurs = " "
    for coauteur in coauteurs_list:
        chaine_coauteurs = chaine_coauteurs.join(coauteur) # On utilise join et non += car celà génère une erreur : TypeError: can only concatenate list (not "str") to list
    return chaine_coauteurs




# Exécuter l'application Dash
if __name__ == '__main__':
    app.run_server(debug=True)
