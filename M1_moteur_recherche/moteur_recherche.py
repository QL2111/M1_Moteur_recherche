import praw
import urllib, urllib.request
import xmltodict
import pandas as pd
import datetime
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json

#import de la classe Document du 
from Document import Document
#Document(Titre, Auteur, Date, Url, Texte)

#import de la classe Author
from Author import Author
#(Name, Ndoc, Production)

from Document import RedditDocument
#Hérite de Document et contient nbCommentaire
from Document import ArxivDocument
#Hérite de Document et contient les co-auteurs
from Document import DocumentFactory
#Factory pour créer les objets Document

from Corpus import Corpus


# TODO: Faire un fichier de configuration pour les identifiants reddit et praw
# TODO: Dans la requete arvix/reddit, créer une variable pour choisir la thématique au lieu d'écire en dur
# TODO: Faire un try pour voir si on peut lire le fichier out sinon on fait une requête
# TODO: Faire une bonne fonction de nettoyage de texte et l'incorporer dans le traitement reddit et arvix
# TODO: Faire une interface pour que l'utilisateur choisisse le nb de fichier Reddit et Arvix
# TODO: Faire une interface pour que l'utilisateur choisisse le nom de l'auteur pour les statistiques(aussi afficher les auteurs existants)
# TODO: Utilité de certaines variables globales ? (collection, collection_author)
# TODO: Faire cohabiter Pickle et Singleton sinon on va transformer en df
# TODO: Lorsqu'on passe le call API, on n'a pas encore fait la suppresion des textes trop petits, on va donc avoir des différences (notamment pour id2doc)

Textes = []   # docs pour stocker les textes(corps de texte)
src = [] # Reddit ou Arxiv (stock les sources)
Titles = [] # Liste des titres
Authors = [] # LIste des auteurs
Dates = [] # Liste des dates
Urls = [] # Liste des urls
collection = [] # Liste d'instance Document
collection_author = [] # Liste d'instance Author

nbCommentaires = [] # Liste des nombres de commentaires pour Reddit
global_coAuteurs = [] # Liste des co-auteurs pour Arvix

nbDocumentReddit = 10 # Faire une interface pour que l'utilisateur choisisse 

id2aut ={} # dictionnaire avec les noms d'auteurs comme clefs et les instances Author en valeurs
id2doc = {} # dictionnarie avec les indices comme clefs et les document en valeurs
indiceClef = 0 # indice pour notre dictionnarie id2doc (on fait une variable globale et non un enumerate car on fait une boucle pour chaque source)

nbDocumentAutheur = 0

def traitement_Reddit(client_id='90mRLOBN2nYhS45pOWpeGg', client_secret='Gu0rQUBgA2Dup2kBWw1xBOcR7xOQww', user_agent='M1_TD3_WebScrapping'):
    reddit = praw.Reddit(client_id = client_id, client_secret = client_secret, user_agent = user_agent)

    #client id 90mRLOBN2nYhS45pOWpeGg secret Gu0rQUBgA2Dup2kBWw1xBOcR7xOQww user_agent M1_TD3_WebScrapping
    try:
        # 10 meilleurs posts de la thématique choisie
        hot_posts = reddit.subreddit('physiology').hot(limit=nbDocumentReddit)
        print("Connexion Reddit réussie")
    except Exception as e:
        print("Connexion Reddit échouer", str(e))

    for indiceClef, post in enumerate(hot_posts):
        # Mini traitement du texte
        text = post.selftext
        text = text.replace('\n', ' ')
        text = text.replace('*', ' ')

        # Ajout des données
        Textes.append(text)
        titre, auteur, url, date, nbCommentaire = post.title, str(post.author), post.url, datetime.datetime.fromtimestamp(post.created).strftime("%Y/%m/%d"), post.num_comments     
        Titles.append(titre)
        Authors.append(str(auteur))
        Urls.append(url)
        Dates.append(date)
        src.append("Reddit")    # On ajoute la source pour la colonne source de notre df
        nbCommentaires.append(post.num_comments) # On ajoute le nombre de commentaire pour la colonne nbCommentaire de notre df
        global_coAuteurs.append("NaN") # Pour avoir la même lenght pour la conversion en df

        # Création de nos classes RedditDocument qui héritent de Document
        doc_classe = RedditDocument(titre, auteur, date, url, text, nbCommentaire) 
        # peuplement de notre dictionnaire avec indiceClef comme clef
        id2doc[indiceClef] = doc_classe   
        collection.append(doc_classe)
    
    # On retourne le dictionnaire pour effectuer des tests
    return id2doc 

def traitement_Arxiv():
    url = 'http://export.arxiv.org/api/query?search_query=all:physiology&start=0&max_results=10'
    indiceClef = nbDocumentReddit # On commence à l'indice nbDocumentReddit car on a déjà nbDocumentReddit dans notre dictionnaire
    docTestArxiv = {}
    try:
        data = urllib.request.urlopen(url)
        data = data.read().decode('utf-8')
        data = xmltodict.parse(data)
        data['feed']['entry']
        print("Connexion Arxiv réussie")
    except Exception as e:
        print("Connexion Arxiv échouée:", str(e))

    for element in data['feed']['entry']:
        text = element['summary']
        text = text.replace('\n', ' ')
        text = text.replace('*', ' ')

        titre, url, date = element['title'], element['link'], datetime.datetime.strptime(element["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d") 
        coAuteurs = []
        # formatage Authors il y a soit une liste d'auteurs ou un unique auteur
        try:
            auteur = element["author"][0]["name"]
            coAuteurs = [a["name"] for a in element["author"]]
            Authors.append(auteur)  # On fait une liste d'auteurs, séparés par une virgule
        except:
            auteur = element["author"]["name"]
            Authors.append(element["author"]["name"])  # Si l'auteur est seul, pas besoin de liste

        Textes.append(text)
        Titles.append(titre)
        Urls.append(url)
        Dates.append(date)  # formatage de la date en année/mois/jour avec librairie datetime)
        src.append("Arxiv") # On ajoute la source pour la colonne source de notre df

        nbCommentaires.append("Nan") # Pour avoir la même lenght pour la conversion en df
        # On souhaite ajouter les co-auteurs pour nos articles Arvix
        # On enlève le premier élément car c'est l'auteur principal
        coAuteurs = coAuteurs[1:]
        global_coAuteurs.append(coAuteurs) # On ajoute les co-auteurs à notre liste globale


        # Création de nos classes ArvixDocument qui héritent de Document
        doc_classe = ArxivDocument(titre, auteur, date, url, text, coAuteurs = coAuteurs) 
        # peuplement de notre dictionnaire avec indiceClef comme clef
        id2doc[indiceClef] = doc_classe   #peuplement
        docTestArxiv[indiceClef] = doc_classe
        indiceClef += 1
        collection.append(doc_classe)

    # On retourne le dictionnaire pour effectuer des tests
    return docTestArxiv

def sauvegarde_to_df():
    # Création de la df
    df = pd.DataFrame({'ID': range(len(Titles)), 'Titre': Titles, 'Auteur': Authors, 'Date': Dates, 'Url': Urls, 'Texte': Textes, 'Source': src, 'nbCommentaires': nbCommentaires, 'coAuteurs': global_coAuteurs})
    # Suppression des textes trop petit
    df = df.drop(df[df["Texte"].str.len() < 20].index)
    df = df.dropna() # Suppression des lignes avec des valeurs manquantes
    df.to_csv('df_main.csv', sep="\t")
    print("Sauvegarde en fichier csv réussie")
    # On retourne la df pour effecutuer des test
    return df

def sauvegarde_to_df_ID_texte_source():
    # Création du dataframe
    df = pd.DataFrame({'ID': range(len(Titles)), 'Texte': Textes, 'Source': src})
    df.to_csv('df_ID_texte_source.csv', sep="\t")
    print("Sauvegarde de la df minimale réussie")
    # On retourne la df pour effecutuer des test
    return df

    
def traitement_document_csv():
    # On récupère les données de la df
    global Titles, Authors, Dates, Urls, Textes, src, collection, df, nbCommentaires, global_coAuteurs

    df = pd.read_csv('df_main.csv', sep="\t", index_col=0)  # index_col=0 pour ne pas avoir une colonne index en plus car on utilise ID
    Textes = df['Texte'].tolist()
    src = df['Source'].tolist()
    Titles = df['Titre'].tolist()
    Authors = df['Auteur'].tolist()
    Dates = df['Date'].tolist()
    Urls = df['Url'].tolist()
    nbCommentaires = df['nbCommentaires'].tolist()
    global_coAuteurs = df['coAuteurs'].tolist()
    # print(nbCommentaires)

    # On peuple notre dictionnaire id2doc avec les données de la df
    for indiceClef, texte in enumerate(Textes):
        if src[indiceClef] == "Reddit":
            doc_classe = DocumentFactory.factory("Reddit", RedditDocument(Titles[indiceClef], Authors[indiceClef], Dates[indiceClef], Urls[indiceClef], texte, nbCommentaires[indiceClef]))
        if src[indiceClef] == "Arxiv":
            doc_classe = DocumentFactory.factory("Arxiv", ArxivDocument(Titles[indiceClef], Authors[indiceClef], Dates[indiceClef], Urls[indiceClef], texte, global_coAuteurs[indiceClef]))
        # peuplement de notre dictionnaire avec indiceClef comme clef
        id2doc[indiceClef] = doc_classe   #peuplement
        collection.append(doc_classe)

    # On retourne le dictionnaire pour effectuer des tests
    return id2doc

def peuplement_auteur():
    # On a déjà une liste contenant tout les auteurs ou une liste d'auteur, on va simplement convertir en dictionnaire
    # clef : nom de l'auteur , valeur : instance de la classe Author
    # print(Authors)
    for i, authors in enumerate(Authors):
        # print(type(authors)) # On s'aperçoit qu'il n'y a que des str, les listes ont été converties en str lors de la sauvegarde en csv
        # print(authors)
        if authors.count("[") > 0:
            # Celà signifie que c'était une liste, on va donc trim
            authors = authors[1:-1]
            # On va ensuite split pour avoir une liste d'auteurs
            authors = authors.split(",")
            # print(type(authors)))
        # print(authors)
        if isinstance(authors, list):
            #Si la liste contient plusieurs auteurs, ajoutez chaque auteur individuellement
            for author in authors:  # On vérifie qu'il n'existe pas déjà
                if author not in id2aut:
                    id2aut[author] = Author(author) # Objet de la classe Author
                    collection_author.append(Author(author)) # Liste d'instance Author
        else:
            if authors not in id2aut: # On vérifie qu'il n'existe pas déjà
                id2aut[authors] = Author(authors) # Objet de la classe Author
                collection_author.append(Author(authors)) # Liste d'instance Author
    # print(id2aut)
    # print(collection_author) # Liste d'instance Author
    return id2aut

def statistiques_auteur(auteur):
    for doc in collection:
        id2aut[doc.getAuteur()].add(doc)
    if auteur in id2aut:
        print(id2aut[auteur].get_statistiques())
    else:
        print("L'auteur n'a pas été trouvé")

def save_pickle(corpus):
    with open("corpus.pkl", "wb") as f:
        pickle.dump(corpus, f)

def load_pickle():
    with open("corpus.pkl", "rb") as f:
        corpus = pickle.load(f)
    return corpus

def convert_to_json_serializable(obj):
    if isinstance(obj, Document):
        return obj.__dict__

def save_json(corpus):
    # On convertit nos dictionnaires id2aut et id2doc qui nous posent problème en JSON
    json_aut = {}
    for key, value in id2aut.items():
        json_aut[key] = value.__dict__

    json_doc = {}
    for key, value in id2doc.items():
        json_doc[key] = value.__dict__

    corpus_data = {
        "Nom": corpus.nom,
        "id2aut": json_aut,
        "id2doc": json_doc
    }
    # On sauvegarde en JSON
    # On a l'erreur TypeError: Object of type Document is not JSON serializable
    # On va créer une fonction pour convertir nos Document en dictionnaire pour que ça soit serializable
    with open("corpus.json", "w") as json_file:
        json.dump(corpus_data, json_file, default=convert_to_json_serializable, indent=4)


def load_json():
    with open('corpus.json') as json_file:
        corpus = json.load(json_file)
        # print(corpus.keys())
        # print(corpus["Nom"])
        # print(corpus["id2aut"])
        return Corpus(corpus["Nom"], corpus["id2doc"], corpus["id2aut"])   # On crée notre corpus avec les données du json

def main():
    global Titles, Authors, Dates, Urls, Textes, src, collection, df, nbCommentaires, global_coAuteurs

    print("Moteur de recherche python")

    #########Chargement des données#########
    try:
        df = pd.read_csv('df_main.csv', sep="\t", index_col=0) # index_col=0 pour ne pas avoir une colonne index en plus car on utilise ID
        print("Lecture du csv réussie")
        #########Création de nos document #########
        id2doc = traitement_document_csv()
        # print(id2doc)
        
    except Exception as e:
        #########Cas où on n'a pas le csv contenant les données#########
        print("On a pas les fichiers sauvegardées en local, on va faire les requêtes API", str(e))
        # -----------------Traitement Reddit------------------
        traitement_Reddit()
        # -----------------Traitement Arxiv-----------------
        traitement_Arxiv()
        # print(id2doc) # On vérifie notre dictionnaire
        #########Sauvegarde des données#########
        df = sauvegarde_to_df()
        sauvegarde_to_df_ID_texte_source()

    #########Premières Manipulations#########
        
    # On affiche le nombre de documents après le traitement
    print(f"Nombre de documents après traitement : {len(collection)} ")
    for texte in df["Texte"]:
        # print(type(texte))
        nbMots = str(texte).split(" ")
        nbPhrases = str(texte).split(".")
        # print(f"Il y a {len(nbMots)} mots pour ce texte")
        # print(f"Il y a  {len(nbPhrases)} phrases pour ce texte")
    
    #print(f"Nb document :{df.shape[0]}" )
    chaine_unique = " ".join(df["Texte"])
    # print(chaine_unique)

    # Test nom document
    # print(collection[0])

    #########Gestion des Auteurs#########
    id2aut = peuplement_auteur()
    # print(id2aut)
    statistiques_auteur("Dongrui Wu") # Plus tard remplacer par un input de l'utilisateur

    ##########Création du Corpus + Patrons de conception##########
    # Ici on peuple directement notre corpus avec nos dictionnaires en les passant dans le constructeur
    # mais pour la démonstration du Pattern Factory, on va donner un dictionnaire vide pour ne pas faire de doublons
    corpus = Corpus("Mon corpus", id2doc = {}, id2aut = id2aut)

    # Test Singleton
    # corpus2 = Corpus("Mon corpus 2", id2doc, id2aut)
    # print(corpus2.nom) # Retourne Mon corpus, car on ne créer qu'un seul unique corpus(singleton, on revoit instance[0] -l'original)

    ##########Démonstration patron de conception Factory##########
    # ajout des documents dans le corpus un à un
    for i, doc in enumerate(collection):
        corpus.add(DocumentFactory.factory(src[i], doc))
    

    # corpus.show(n_docs=5, tri="123") # 123 -> Tri temporel, abc -> Tri alphabétique
    #print(corpus.__repr__)
    
    ##########Sauvegarde de notre Corpus##########
        
    # !!!!!!!!Correction de G. Poux-Médard, 2021-2022!!!!!!!!
    # Conflit avec singleton, on ne peut pas sauvegarder le corpus avec pickle
    # save_pickle(corpus)
    # corpus = load_pickle()
    # corpus.show(n_docs=5, tri="123")
    

    # On a des problèmes lorsqu'on souhaite convertir en df nos dictionnaires, on va donc les sauvegarder en JSON
    save_json(corpus)
    corpus = load_json()
    print(type(corpus))
    # On vérifie que ça fonctionne correctement
    corpus.show(n_docs=5, tri="123")
    
        

    
    




if __name__ == '__main__':
    main()


# Sources:
    # https://www.reddit.com/r/redditdev/comments/3qbll9/praw_getting_started/
    # https://praw.readthedocs.io/en/latest/getting_started/quick_start.html
    # https://realpython.com/python-use-global-variable-in-function/#:~:text=Inside%20a%20function%2C%20you%20can,creating%20a%20new%20local%20one.
    # https://www.geeksforgeeks.org/different-ways-to-iterate-over-rows-in-pandas-dataframe/
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # https://medium.com/@amirm.lavasani/design-patterns-in-python-factory-method-1882d9a06cb4
    # Corpus, function show, Correction de G. Poux-Médard, 2021-2022
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    # https://docs.python.org/3/library/json.html
