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
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]
    return wrapper

# =============== 2.7 : CLASSE CORPUS ===============
@singleton
class Corpus():
    def __init__(self, nom, id2doc, id2aut):
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
        self.id2doc.update({self.ndoc: Document})
        self.ndoc += 1

        self.authors = Document.auteur
        if isinstance(self.authors, list):
            self.naut += len(self.authors)
        else:
            self.naut += 1

    def getAuthors(self):
        return self.authors

    def getId2doc(self):
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

    def __repr__(self):
        docs = list(self.id2doc.values())
        docs = list(sorted(docs, key=lambda x: x.titre.lower()))
        return "\n".join(list(map(str, docs)))

    # regular expression
    def search(self, mot_clef, chaine_unique):
        p = re.compile(fr'\b{mot_clef}[a-zA-Z]*\b', re.IGNORECASE)
        res = p.finditer(chaine_unique)
        list_res = []
        for r in res:
            (start, end) = r.span()     # start and end correspondent à la position de la chaîne unique
            list_res.append(chaine_unique[start - 5: end + 5]) # on ajoute 5 caractères avant et après la chaîne unique
        return list_res

    def concorder(self, mot_clef, chaine_unique, taille_contexte):
        p = re.compile(fr'\b{mot_clef}[a-zA-Z]*\b', re.IGNORECASE)
        res = p.finditer(chaine_unique)
        liste_contexte_gauche = []
        liste_motif_trouve = []
        liste_contexte_droite = []
        for r in res:
            (start, end) = r.span()     # start and end correspondent à la position de la chaîne unique
            liste_contexte_gauche.append(chaine_unique[start - taille_contexte: start])
            liste_motif_trouve.append(chaine_unique[start: end ])
            liste_contexte_droite.append(chaine_unique[end: end + taille_contexte])
        df = pd.DataFrame(list(zip(liste_contexte_gauche, liste_motif_trouve, liste_contexte_droite)), columns=['contexte_gauche', 'motif','contexte_droite'])
        return df
# Stats
    def nettoyer_texte(self, chaine_unique):
        chaine_unique = chaine_unique.lower()
        # retour à la ligne
        chaine_unique = chaine_unique.replace('\n', ' ')
        chaine_unique = chaine_unique.replace('*', ' ')
        # ponctuations 
        chaine_unique = re.sub(r'[^\w\s]', ' ', chaine_unique)
        # chiffre
        chaine_unique = re.sub(r'\d', ' ', chaine_unique)
        # Suppression des espaces multiples
        chaine_unique = re.sub(r'\s+', ' ', chaine_unique)

        return chaine_unique
    
    def definir_vocab(self):
        freq_counter = Counter()  # compteur de fréquence
        doc_counter = Counter()  # compteur de document fréquence

        for doc in self.id2doc.values():
            vocab = self.nettoyer_texte(doc.texte)
            mots = vocab.split(" ")
            freq_counter.update(mots)
            doc_counter.update(set(mots))  # Utilisation d'un set pour compter chaque mot une seule fois par document
            self.__vocabulaire.update(vocab.split(" "))  # on coupe la chaine en liste à chaque espace, update est une insertion dans un set

        self.frequence_mot = pd.DataFrame(list(freq_counter.items()), columns=['Mot', 'Fréquence'])
        self.frequence_mot = self.frequence_mot.sort_values(by='Fréquence', ascending=False)

        # Ajout de la colonne Document Frequency (DF)
        self.frequence_mot['DocumentFrequency'] = self.frequence_mot['Mot'].apply(lambda mot: doc_counter[mot]) # ajout de la colonne DF, utilisation de chat GPT pour avancer au TD 7

        # peuplement de self.vocab
        self.frequence_mot.insert(0, 'ID', range(0, 0 + len(self.frequence_mot)))
        vocab = self.frequence_mot.set_index('Mot').to_dict(orient='index')
        self.vocab = {mot: {'ID': info['ID'], 'Fréquence': info['Fréquence'], 'DocumentFrequency': info['DocumentFrequency']} for mot, info in vocab.items()}

        return self.vocab


    def get_frequence_mot(self):
        if not self.frequence_mot:
            self.definir_vocab()
        return self.frequence_mot
    
    # return sparse matrix
    def definir_matrice(self):
        # matrice de co-occurence Document(j) x Mot(i)
        # on parcourt chaque document
        # peuplement du vocabulaire
        if not self.vocab:
            self.definir_vocab()
        indice = 0
        # print(self.__vocabulaire)
        # print(self.ndoc, len(self.__vocabulaire)) #20x918
        # print(self.id2doc.values())
        self.mat_TF = np.zeros((self.ndoc, len(self.__vocabulaire)))
        for doc in self.id2doc.values():
            # on parcourt chaque mot du document
            for mot in doc.texte.split(" "):
                # on parcourt chaque mot du vocabulaire
                for mot_vocab in self.__vocabulaire:
                    if mot == mot_vocab:
                        # on incrémente la valeur de la matrice
                        self.mat_TF[indice, self.vocab[mot]['ID']] += 1
            indice += 1
        # Conversion en matrice creuse
        self.mat_TF = scipy.sparse.csr_matrix(self.mat_TF)
        print(f"Dimension de la matrice",self.mat_TF.shape)
        return self.mat_TF
    

    # on ajoute les clefs valeurs nbTotalOccurenceCorpus et nbTotalOccurenceDoc dans le dictionnaire vocab
    def calculer_stats_vocab(self):
        if not self.mat_TF:
            self.definir_matrice()

        # Nb d'occurence total dans le corpus
        occurrences_totales = np.sum(self.mat_TF, axis=0)
        # print(occurrences_totales)
        # Nb de documents contenant le mot (on regarde si la valeur est supérieur à 0)
        documents_contenant_mot = np.sum(self.mat_TF > 0, axis=0)

        # Mettre à jour les informations dans self.vocab
        for mot in self.vocab.values():
            mot_id = mot['ID']
            mot['OccurrencesTotales'] = occurrences_totales[0, mot_id]
            mot['DocumentsContenantMot'] = documents_contenant_mot[0, mot_id]

        return self.vocab
    
    # TF-IDF
    # résultat proche de 0 -> pas important
    # résultat proche de 1 -> important
    def definir_mat_TFxIDF(self):
        if not self.mat_TFxIDF:
            self.definir_matrice()

        # Utilisation de la classe TfidfTransformer de scikit-learn
        transformer = TfidfTransformer()
        self.mat_TFxIDF = transformer.fit_transform(self.mat_TFxIDF)

        return self.mat_TFxIDF