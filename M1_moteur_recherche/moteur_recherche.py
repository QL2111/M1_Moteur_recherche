"""
@file moteur_recherche.py
@brief Fichier principal de l'application

Ce programme a pour but de créer un moteur de recherche à partir de données provenant de Reddit et Arxiv. 
"""

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
# TODO: Lorsqu'on définit vocab, la fréquence de l'apparition du mot est différente entre definir_vocab()-> Counter() et calculer_stats_vocab() -> traitement sparse_matrix


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
    """
    @fn traitement_Reddit
    @brief Effectue le traitement des documents provenant de Reddit.

    On va utiliser utiliser praw pour faire des requêtes sur Reddit, on récupère un objet qui nous permet de prendre les n(10 dans notre cas) meilleurs posts de la thématique choisie.
    On va ensuite récupérer les informations qui nous intéressent et les stocker dans des listes globales.
    On en profite pour créer nos intance RedditDocument et les stocker dans notre dictionnaire id2doc.
    On peuple aussi notre collection de document.

    @param client_id (str): Identifiant client Reddit.
    @param client_secret (str): Clé secrète client Reddit.
    @param user_agent (str): Chaîne d'agent utilisateur Reddit.
    @return dict: Dictionnaire des documents Reddit.
    """
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
    """
    @fn traitement_Arxiv
    @brief Effectue le traitement des documents provenant d'Arxiv.

    On va utiliser utiliser urlib.request pour faire une requête à base d'une url qu'on configure.
    On récupère un objet qui nous permet de prendre les n(10 dans notre cas) meilleurs posts de la thématique choisie.
    On va ensuite récupérer les informations qui nous intéressent et les stocker dans des listes globales.
    On fait un traitement spécial pour les co-auteurs car il peut y en avoir plusieurs.
    On en profite pour créer nos intance ArvixDocument et les stocker dans notre dictionnaire id2doc.
    On peuple aussi notre collection de document.

    @return dict: Dictionnaire des documents Arxiv.
    """
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
    """
    @fn sauvegarde_to_df
    @brief Sauvegarde les données dans un DataFrame pandas.

    Ici on va sauvegarder les données dans un fichier csv avec les listes globales qu'on a peuple avec traitement_Reddit et traitement_Arvix pour pouvoir les réutiliser plus tard.
    On en profite aussi pour faire un léger traitement(suppresion des textes trop petits)

    @return pd.DataFrame: DataFrame contenant les données.
    """
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
    """
    @fn sauvegarde_to_df_ID_texte_source
    @brief Sauvegarde une version minimale des données dans un DataFrame pandas.

    Question du TP, dans notre cas, on préfèrera utiliser sauvegarde_to_df() pour avoir plus d'informations.

    @return pd.DataFrame: DataFrame minimal contenant les données.
    """
    # Création du dataframe
    df = pd.DataFrame({'ID': range(len(Titles)), 'Texte': Textes, 'Source': src})
    df.to_csv('df_ID_texte_source.csv', sep="\t")
    print("Sauvegarde de la df minimale réussie")
    # On retourne la df pour effecutuer des test
    return df

    
def traitement_document_csv():
    """
    @fn traitement_document_csv
    @brief Traite les documents à partir d'un fichier CSV.

    On utilise cette fonction dans le cas où on a déjà sauvegardé nos données dans un fichier csv.
    On va donc simplement lire le fichier csv et peupler nos listes globales avec les données en transformer les df correspondantes en listes.
    On en profite aussi pour créer nos intance Document et les stocker dans notre dictionnaire id2doc.
    Le peuplement se fait en utilisant DocumentFactory.
    On peuple aussi notre collection de document.

    @return dict: Dictionnaire des documents.
    """
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
    """
    @fn peuplement_auteur
    @brief Peuple le dictionnaire des auteurs.

    On va utiliser les données de la liste globale Authors pour peupler notre dictionnaire id2aut avec comme clef le nom de l'auteur et comme valeur un objet de la classe Author.
    On effectue le traitement lorsqu'il y a plusieurs auteurs pour un document. (coAuteurs)
    On vérifie le type str ou list et on effectue le traitement approprié.
    On vérifie si l'auteur n'est pas déjà présent dans id2aut, sinon on peuple notre dictionnaire d'auteur.
    On peuple aussi notre collection d'auteurs.
    Avec tout ceci, on a tout les auteurs uniques, on en profite pour remplir les attributs de la classe Author avec les documents qui lui sont associés.

    @return dict: Dictionnaire des auteurs.
    """
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
    
    # Maintenant qu'on a tout les auteurs uniques, on peut peupler les attributs de la classe Author
    for doc in id2doc.values():
        id2aut[doc.getAuteur()].add(doc) 
    
    return id2aut

def statistiques_auteur(auteur):
    """
    @fn statistiques_auteur
    @brief Affiche les statistiques d'un auteur.

    On prend un paramètre le nom d'un auteur et on affiche ses statistiques.

    @param auteur (str): Nom de l'auteur.
    """
    
    if auteur in id2aut:
        print(id2aut[auteur].get_statistiques())
    else:
        print("L'auteur n'a pas été trouvé")

def save_pickle(corpus):
    """
    @fn save_pickle
    @brief Sauvegarde le corpus en format pickle.

    On a pu sauvegarder une version primitive du corpus, néanmoins on ne l'utilise plus et on préfère une sauvegarde par fichier JSON car le décorateur singleton pose probèlme avec pickle.

    @param corpus (Corpus): Objet Corpus à sauvegarder.
    """
    with open("corpus.pkl", "wb") as f:
        pickle.dump(corpus, f)

def load_pickle():
    """
    @fn load_pickle
    @brief Charge le corpus depuis le fichier pickle.

    On n'utilise plus cette fonction et on préfère une sauvegarde par fichier JSON car le décorateur singleton pose probèlme avec pickle.

    @return Corpus: Objet Corpus chargé.
    """
    with open("corpus.pkl", "rb") as f:
        corpus = pickle.load(f)
    return corpus

def convert_to_json_serializable(obj):
    """
    @fn convert_to_json_serializable
    @brief Convertit un objet en format JSON serializable.

    La type Document n'est pas serializable, et posait problème, on va donc les transformer en dictionnaire pour que la conversion en JSON marche.

    @param obj: Objet à convertir.
    @return dict: Dictionnaire représentant l'objet.
    """
    if isinstance(obj, Document):
        return obj.__dict__

def save_json(corpus):
    """
    @fn save_json
    @brief Sauvegarde le corpus en format JSON.

    On a des problèmes lorsqu'on souhaite convertir en df nos dictionnaires, on va donc les sauvegarder en JSON.
    On convertit nos dictionnaires id2aut et id2doc qui nous posent problème en dictionnaires afin qu'ils sont serializable. 
    On utilise .__dict__ pour les convertir en dictionnaire.
    On créer notre dictionnaire corpus_data avec les données du corpus.
    On sauvegarde en JSON en utilisant json.dump avec default=convert_to_json_serializable pour convertir nos Document en dictionnaire pour que ça soit serializable.

    @param corpus (Corpus): Objet Corpus à sauvegarder.
    """
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
    """
    @fn load_json
    @brief Charge le corpus depuis le fichier JSON.

    @return Corpus: Objet Corpus chargé.
    """
    with open('corpus.json') as json_file:
        corpus_json = json.load(json_file)
        # print(corpus_json.keys())
        # print(corpus_json["Nom"])
        # print(corpus_json["id2aut"])

        # On crée notre corpus avec les données du json
        corpus = Corpus(corpus_json["Nom"], corpus_json["id2doc"], corpus_json["id2aut"])

    return corpus   

def moteur_recherche(mot_clefs, corpus):
    query_vector = np.zeros(len(corpus.vocab)) # vecteur de la taille du vocabulaire

    for mot_clef in mot_clefs.split(" "):
        # Si le mot que l'utilisateur à rentrer est dans le vocabulaire, on incrémente le vecteur
        if mot_clef in corpus.vocab:
            print(f"Mot-clé : {mot_clef}, ID : {corpus.vocab[mot_clef]['ID']}")
            query_vector[corpus.vocab[mot_clef]['ID']] += 1

    print("Vecteur de requête:", query_vector)

    # similarité entre votre vecteur requ^ete et tous les documents, -> similarité cosinus(voir TD 7 fin de page)
    similarites = cosine_similarity(query_vector.reshape(1, -1), corpus.mat_TF)

    # indices des documents triés par ordre décroissant
    sorted_indices = similarites.argsort()[0][::-1]

    # trier les scores résultats et associé les meilleurs résultats.
    # On affiche les meilleurs résultats
    for index in sorted_indices[:3]:
        print(f"Document {index}: Similarité Cosinus = {similarites[0, index]}")
        print(corpus.id2doc[index])  
        print("\n")

def main():
    """
    @brief Fonction principale du programme.
    """
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
    print("")
    print("---------------Traitement Auteur-----------------")
    statistiques_auteur("Dongrui Wu") # Plus tard remplacer par un input de l'utilisateur
    print("")
    ##########Création du Corpus + Patrons de conception##########
    # D'habitude on aurait peupler directement notre corpus avec nos dictionnaires en les passant dans le constructeur
    # Pour la démonstration du Pattern Factory, on va donner un dictionnaire vide pour ne pas faire de doublons
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
    # print(type(corpus))


    print("\n-----------------Visualisation du corpus après sauvegarde en JSON-----------------\n")
    # On vérifie que ça fonctionne correctement
    corpus.show(n_docs=5, tri="123")
    print("\n-----------------Manipulation sur le corpus-----------------\n")
    # print(chaine_unique)
    print("Test de la fonction search")
    print(corpus.search("hypertrophy", chaine_unique)) # On recherche le mot hypertrophy dans notre corpus et on renvoie le passage(5 caractères à droite et à gauche)
    print("")
    print("Test de la fonction concorder")
    print(corpus.concorder("hypertrophy", chaine_unique, 5)) # On recherche le mot hypertrophy dans notre corpus et on renvoie le passage(5 caractères à droite et à gauche)
    print("")

    print("Test nettoyer texte")
    print(f"Version non nettoyée :{chaine_unique[:10]}")
    chaine_unique = corpus.nettoyer_texte(chaine_unique)
    print(f"Version nettoyée :{chaine_unique[:10]} \n") # On nettoie le texte

    print("Test tableau freq(Fréquence du mot dans le corpus et Nombre de document le comportant) Trié par ordre décroissant de Fréquence")
    corpus.definir_vocab()
    print(f"{corpus.freq.head()} \n")

    print("Test vocab, version 1")
    # getVocab_digeste -> affiche les 10 premiers mots du vocabulaire avec leur fréquence et le nombre de documents le comportant
    print(corpus.getVocab_digeste(10)) # clef : mots, valeurs : dictionnaire id, nb_frequence, nbOccurrencesTotales, nbDocumentsContenantMot
    print("")

    print("Test sparse matrix")
    # print(corpus.definir_matrice()) # retourne la matrice creuse, print les éntrées non nulles (DocumentxMot) et le nb d'occurence

    # on ajoute les clefs valeurs nbTotalOccurenceCorpus et nbTotalOccurenceDoc dans le dictionnaire vocab
    corpus.calculer_stats_vocab() # definir_matrice est appelé dans cette fonction car on calcul le nombre d'occurence total du mot dans le corpus et le nombre de document le comportant
    # On l'a déjà calculé dans la fonction definir_vocab mais cette fois-ci, on le fait à partir de la matrice creuse
    print(corpus.getMat_TF())
    print(f"\nTest vocab après calcul des statistiques via la matrice creuse : \n{corpus.getVocab_digeste(10)} \n")

    print("On voit qu'il y a un problème TermFrequency est différent de OccurencesTotales alors que les valeurs devraient être égales")
    
    print("Test de la matrice TF-IDF")
    print(corpus.definir_mat_TFxIDF()) # retourne la matrice creuse, print les éntrées non nulles (DocumentxMot) et l'importance relative au corpus du mot'
    # résultat proche de 0 -> pas important
    # résultat proche de 1 -> important

    print("\n-----------------Moteur de recherche-----------------\n")
    # Demander à l'utilisatuer mot clef -> input puis faire une interface et changer la valeur

    # transformer ces mots-clefs sous la forme d'un vecteur sur le vocabulaire précédement construit,

    # Pour tester, on n'a choisi que des mots présent dans un seul document, on va tester si il n'y a que lui qui a une similarité supérieur à 0
    mot_clefs = "interactive storytelling narratives"
    moteur_recherche(mot_clefs, corpus)



    




if __name__ == '__main__':
    main()


# Sources:
    # https://www.reddit.com/r/redditdev/comments/3qbll9/praw_getting_started/
    # https://praw.readthedocs.io/en/latest/getting_started/quick_start.html
    # https://realpython.com/python-use-global-variable-in-function/#:~:text=Inside%20a%20function%2C%20you%20can,creating%20a%20new%20local%20one.
    # https://www.geeksforgeeks.org/different-ways-to-iterate-over-rows-in-pandas-dataframe/
    # https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
    # https://medium.com/@amirm.lavasani/design-patterns-in-python-factory-method-1882d9a06cb4
    # https://www.adamsmith.haus/python/answers/how-to-get-the-first-n-items-from-a-dictionary-in-python
    # Corpus, function show, Correction de G. Poux-Médard, 2021-2022
    # https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.from_dict.html
    # https://docs.python.org/3/library/json.html
    # Doxygen
    # !!!!!Utilisation de chat GPT pour la documentation doxygen!!!!! (Les descriptions en dehors de @brief ont été écris à la main)
