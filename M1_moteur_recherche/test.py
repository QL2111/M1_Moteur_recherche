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
import scipy

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


# On créer ses variables globales pour les tests(pour le Corpus)
# Initialisation globale pour les tests
id2doc_test = {}
id2aut_test = {}
corpus_test = None

# Fonction de configuration pour Pytest, on initialise les variables globales
# La fonction setup est appelée avant chaque test, celà nous permettra de ne pas avoir à répéter les initialisations pour chaque teste unitaire

def setup():
    global id2doc_test, id2aut_test, corpus_test
    id2doc_test = traitement_document_csv()
    id2aut_test = peuplement_auteur()
    corpus_test = Corpus("Mon corpus", id2doc_test, id2aut_test)

def test_document_traitement_Reddit():
    dict_Reddit = traitement_Reddit()
    # print(dict_Reddit)
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
    global id2doc_test
    id2doc_test = traitement_document_csv()
    for doc in id2doc_test.values():
        assert isinstance(doc, Document), "On ne se retrouve pas avec un objet Document"
    assert len(id2doc_test) > 19, "Le dictionnaire a retourné moins de 20 documents"

def test_peuplement_auteur():
    id2aut_test = peuplement_auteur()
    for aut in id2aut_test.values():
        assert isinstance(aut, Author), "On ne se retrouve pas avec un objet Author"
    assert len(id2aut_test) > 1, "La taille est inférieur à 1, il y a erreur dans la sauvegarde"

def test_load_json():
    corpus_test_json = load_json()
    assert corpus_test_json.nom == "Mon corpus", "Le nom du corpus n'est pas correct"

# Test des fonctions de corpus_test
def test_corpus_test_search():
    corpus_test = Corpus("Mon corpus", id2doc_test, id2aut_test)
    chaine_unique_test = "blablabla test carotte, fraise test banane"
    corpus_test_search = corpus_test.search("test", chaine_unique_test)
    assert len(corpus_test_search) == 2, "Il devrait n'y avoir que 2 passages de test dans la chaine"
    for passage in corpus_test_search:
        assert "test" in passage, "Le mot test n'est pas dans le passage"



def test_corpus_test_concorder():
    # Il serait plus pertinent d'avoir un contexte plus grand, mais pour les tests, on va se contenter de 5 caractères
    df_concorder = corpus_test.concorder("test", "blablabla test carotte, fraise test banane", 5)
    colonnes_attendus = ['contexte_gauche', 'motif', 'contexte_droite']

    assert isinstance(df_concorder, pd.DataFrame), "On ne se retrouve pas avec un objet DataFrame"
    assert all(col in df_concorder.columns for col in colonnes_attendus), "Les colonnes ne sont pas correctes"

    # Test fonctionnement de la fonction

    # On vérifie que le nombre de lignes est correct
    # Résultat attendu : 2 lignes car 2 fois le mot test dans la chaine
    assert len(df_concorder) == 2, "Il devrait y avoir 2 lignes dans le DataFrame"
    list_test_0 = list(corpus_test.concorder("test", "blablabla test carotte, fraise test banane", 5).loc[0])
    print(list_test_0)
    # Résultat attendu pour list_test[0](abla ) : 5 caractères à gauche de test
    # Résultat attendu pour list_test[1](test) : motif
    # Résultat attendu pour list_test[2]( caro ) : 5 caractères à droite de test
    assert list_test_0[0] == "abla ", "La fonction ne retourne pas la bonne chaine pour le contexte gauche"
    assert list_test_0[1] == "test", "La fonction ne retourne pas la bonne chaine pour le motif"
    assert list_test_0[2] == " caro", "La fonction ne retourne pas la bonne chaine pour le contexte droit"

    list_test_1 = list(corpus_test.concorder("test", "blablabla test carotte, fraise test banane", 5).loc[1])
    # Résultat attendu pour list_test[0]( frai) : 5 caractères à gauche de test
    # Résultat attendu pour list_test[1](test) : motif
    # Résultat attendu pour list_test[2]( bana) : 5 caractères à droite de test
    assert list_test_1[0] == "aise ", "La fonction ne retourne pas la bonne chaine pour le contexte gauche"
    assert list_test_1[1] == "test", "La fonction ne retourne pas la bonne chaine pour le motif"
    assert list_test_1[2] == " bana", "La fonction ne retourne pas la bonne chaine pour le contexte droit"

def test_nettoyer_texte(chaine_unique="AAA\n  1un?*@.BBB"):
    # toLowerCase, enlever les retours à la ligne, astériques, ponctuation, caractères spéciaux, nombres et espaces multiples
    print(corpus_test.nettoyer_texte(chaine_unique))
    assert corpus_test.nettoyer_texte(chaine_unique) == "aaa un bbb", "Le résultat attendu est mauvais"

def test_definir_vocab():
    # Résultat attendu : dictionnaires avec les mots en clef et en valeur un dictionnaires avec ID, TermFrequency et DocumentFrequency
    dict_vocab_test = corpus_test.definir_vocab()
    assert isinstance(dict_vocab_test, dict), "On ne se retrouve pas avec un objet dict"
    # print(dict_vocab_test["and"].keys())
    # On vérifie que les clefs sont bonnes
    assert str(dict_vocab_test["and"].keys()) == "dict_keys(['ID', 'TermFrequency', 'DocumentFrequency'])"
    assert len(dict_vocab_test) > 1, "La taille est inférieur à 1, il y a erreur dans la sauvegarde"

def test_definir_matrice():
    sparse_matrix_test = corpus_test.definir_matrice()
    print(type(sparse_matrix_test))
    assert isinstance(sparse_matrix_test, scipy.sparse._csr.csr_matrix), "On ne se retrouve pas avec une sparse matrix"



"""



# def test_calculer_stats_vocab():

# def test_definir_mat_TFxIDF():
    
# def test_moteur_recherche(mot_clefs, corpus_test):
"""