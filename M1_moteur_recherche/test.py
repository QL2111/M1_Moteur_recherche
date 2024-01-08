"""
@file test.py
@brief Fichier de test pour le moteur de recherche

Dans ce fichier, nous allons tester les différentes fonctions du moteur de recherche nécessaire au bon fonctionnement.
On vérifiera si les objets retournés sont bien ceux du type attendus et si les sauvegardes sont bien effectuées.
"""

# pytest -v test.py --html=pytest_report.html --self-contained-html
# Installer pytest
# pytest -v test.py
# rapport html

import pandas as pd

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

from moteur_recherche import traitement_Reddit
from moteur_recherche import traitement_Arxiv
from moteur_recherche import sauvegarde_to_df
from moteur_recherche import sauvegarde_to_df_ID_texte_source
from moteur_recherche import traitement_document_csv
from moteur_recherche import peuplement_auteur
from moteur_recherche import load_json


def test_document_traitement_Reddit():
    dict_Reddit = traitement_Reddit()
    for doc in dict_Reddit.values():
        assert isinstance(doc, RedditDocument), "On ne se retrouve pas avec un objet RedditDocument"
    assert len(dict_Reddit) > 9, "Reddit a retourné moins de 10 documents"

def test_document_traitement_Arxiv():
    dict_Arvix = traitement_Arxiv()
    for doc in dict_Arvix.values():
        print(type(doc))
        assert isinstance(doc, ArxivDocument), "On ne se retrouve pas avec un objet ArxivDocument"
    assert len(dict_Arvix) > 9, "Arxiv a retourné moins de 10 documents"

def test_document_sauvegarde_to_df():
    df = sauvegarde_to_df()
    colonnes_attendus = ['ID', 'Titre', 'Auteur', 'Date', 'Url', 'Texte', 'Source']
    assert all(col in df.columns for col in colonnes_attendus), "Les colonnes ne sont pas correctes"
    assert len(df) > 1, "La taille est inférieur à 1, il y a erreur dans la sauvegarde"

def test_document_sauvegarde_to_df_ID_texte_source():
    df = sauvegarde_to_df_ID_texte_source()
    colonnes_attendus = ['ID', 'Texte', 'Source']
    assert all(col in df.columns for col in colonnes_attendus), "Les colonnes ne sont pas correctes"
    assert len(df) > 1, "La taille est inférieur à 1, il y a erreur dans la sauvegarde"

def test_document_traitement_csv():
    id2doc = traitement_document_csv()
    for doc in id2doc.values():
        assert isinstance(doc, Document), "On ne se retrouve pas avec un objet Document"
    assert len(id2doc) > 19, "Le dictionnaire a retourné moins de 20 documents"

def test_peuplement_auteur():
    id2aut = peuplement_auteur()
    for aut in id2aut.values():
        assert isinstance(aut, Author), "On ne se retrouve pas avec un objet Author"
    assert len(id2aut) > 1, "La taille est inférieur à 1, il y a erreur dans la sauvegarde"

def test_load_json():
    corpus_json = load_json()
    assert corpus_json.nom == "Mon corpus", "Le nom du corpus n'est pas correct"
