"""
@file Corpus.py
@brief Fichier contenant la classe Corpus ayant le décorateur singleton

"""

from Author import Author
from Document import Document
import re
import pandas as pd
from collections import Counter
import scipy
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer


# =============== SINGLETON ===============
def singleton(cls):
    """
    @fn singleton
    @brief Décorateur pour implémenter le modèle de conception Singleton.

    Assure qu'une seule et unique instance de la classe corpus soit créée.

    @param cls: Classe à décorer.
    @return: Instance unique de la classe.
    """
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]
    return wrapper

# =============== 2.7 : CLASSE CORPUS ===============
@singleton
class Corpus():
    """
    @class Author
    @brief Représente un Corpus ayant un nom, une liste d'auteurs une liste de documents, son nombre de documents et son nombre d'auteurs.


    """
    def __init__(self, nom, id2doc, id2aut):
        """
        @fn __init__
        @brief Initialise une instance de la classe Corpus.

        @param nom (str): Nom du corpus.
        @param id2doc (dict): Dictionnaire des documents associés au corpus. Clé : ID, Valeur : Document.
        @param id2aut (dict): Dictionnaire des auteurs associés au corpus. Clé : ID, Valeur : Auteur.
        """
        self.nom = nom 
        self.authors = id2aut # clef : id, valeurs : auteur
        self.id2doc = id2doc # clef : id, valeurs : document
        self.ndoc = len(id2doc)   # nombre de documents
        self.naut = len(id2aut)   # nombre d'auteurs
        self.__vocabulaire = set()    # set au départ pour éviter les doublons, puis mot netttoyé
        self.frequence_mot = {}  # dictionnaire de fréquence des mots
        self.vocab = {} # clef : mots, valeurs : dictionnaire id, nb_frequence, nbOccurrencesTotales, nbDocumentsContenantMot
        self.mat_TF = None # matrice de co-occurence Document(j) x Mot(i), conversion plus tard
        self.mat_TFxIDF = None # Alternative à la matrice TF
    

    def add(self, Document):
        """
        @fn add
        @brief Ajoute un document au corpus.

        Incrémente également le nombre total de documents associés au corpus et met à jour la liste d'auteurs.

        @param Document (Document): Document à ajouter au corpus.
        """
        self.id2doc.update({self.ndoc: Document})
        self.ndoc += 1

        self.authors = Document.auteur
        if isinstance(self.authors, list):
            self.naut += len(self.authors)
        else:
            self.naut += 1

    def getAuthors(self):
        """
        @fn getAuthors
        @brief Retourne la liste d'auteurs associés au corpus.

        @return: Liste d'auteurs.
        """
        return self.authors

    def getId2doc(self):
        """
        @fn getId2doc
        @brief Retourne le dictionnaire des documents associés au corpus.

        @return: Dictionnaire des documents. Clé : ID, Valeur : Document.
        """
        return self.id2doc

# =============== 2.8 : REPRESENTATION =============== # 
    # !!!!!!!!Correction de G. Poux-Médard, 2021-2022!!!!!!!!
    def show(self, n_docs=-1, tri="abc"):
        docs = list(self.id2doc.values())
        if tri == "abc":  # Tri alphabétique
            docs = list(sorted(docs, key=lambda x: x.titre.lower()))[:n_docs]
        elif tri == "123":  # Tri temporel
            docs = list(sorted(docs, key=lambda x: x.date))[:n_docs]
        print("\n".join(list(map(str, docs))))

    """
    @fn __repr__
    @brief Affiche les documents du corpus

    Une représentation plus digeste que celle de la méthode show()
    
    @return str : la représentation du corpus
    """
    def __repr__(self):
        docs = list(self.id2doc.values())
        docs = list(sorted(docs, key=lambda x: x.titre.lower()))
        return "\n".join(list(map(str, docs)))

    