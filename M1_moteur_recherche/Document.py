#Création du document
"""
@file Document.py
@brief Fichier contenant les classes Document, RedditDocument, ArxivDocument et DocumentFactory

RedditDocument et ArxivDocument héritent de Document
DocumentFactory permet de créer les objets Document

"""

""" • titre : le titre du document
• auteur : le nom de l'auteur
• date : la date de publication
• url : l'url source
• texte : le contenu textuel du document """

class Document:
    """
    @class Document
    @brief Représente un document.

    Cette classe sert de base pour les classes Reddit Document et ArvixDocument.
    Elle contient le titre, l'auteur, la date, l'url, le texte et le type du document.

    """
    #Initule de déclarer les attributs, le faire dans le constructeur
    def __init__(self, titre="", auteur="", date="", url="", texte="", type=""):
        """
        @brief Initialise une instance de la classe Document.

        @param titre (str): Titre du document.
        @param auteur (str): Auteur du document.
        @param date (Date): Date du document.
        @param url (str): URL du document.
        @param texte (str): Texte du document.
        @param type (str): Type du document (par exemple, "Reddit" ou "Arxiv").
        """
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.__type = type #Attribut privé
    
    def affiche(self):
        """
        @fn affiche
        @brief Retourne une représentation textuelle du document.

        @return: Chaîne de caractères représentant le document.
        """
        return("Titre :", self.titre, "Auteur :", self.auteur, "Date :", self.date, "Url :", self.url, "Texte :",self.texte)
    
    #On doit faire un __str__ sinon ça retourne un pointeur vers l'object quand on print
    def __str__(self) ->str:
        """
        @fn __str__
        @brief Retourne une représentation textuelle du document.

        @return: Chaîne de caractères représentant le document.
        """
        return(f"Titre : {str(self.titre)}")
    
    #Redifinition dans les classes filles
    def getType(self):
        pass    
    
    def getAuteur(self):
        """
        @fn getAuteur
        @brief Retourne l'auteur du document.

        @return: Auteur du document.
        """
        return self.auteur
    
    def getTexte(self) -> str:
        """
        @fn getTexte
        @brief Retourne le texte du document.

        @return: Texte du document.
        """
        return self.texte
    
    def getTitre(self) -> str:
        """
        @fn getTitre
        @brief Retourne le titre du document.

        @return: Titre du document.
        """
        return self.titre

#Test
#d1 = Document("TitreTest", "AuteurTest", "DateTest", "UrlTest", "TexteTest")
#print(d1.affiche())
#print("\nAffichage direct __str__")
#print(d1)

class RedditDocument(Document):
    """
    @class RedditDocument
    @brief Représente un document provenant de Reddit, héritant de la classe Document.

    On ajoute l'attribut nbCommentaire pour le nombre de commentaires, spécifique à Reddit.

    """
    #nbCommentaire
    def __init__(self, titre="", auteur="", date="", url="", texte="", nbCommentaire = 0):
        """
        @brief Initialise une instance de la classe RedditDocument.

        @param titre (str): Titre du document.
        @param auteur (str): Auteur du document.
        @param date (str): Date du document.
        @param url (str): URL du document.
        @param texte (str): Texte du document.
        @param nbCommentaire (int): Nombre de commentaires associés au document.
        """
        #Document.__init__(self, titre = titre, auteur = auteur, date = date, url = url, texte = texte) #Manière alternative sans super
        super().__init__(titre = titre, auteur = auteur, date = date, url = url, texte = texte, type="Reddit")     #pas de self avec super
        self.nbCommentaire = nbCommentaire
    
    def getNbCommentaire(self):
        """
        @fn getNbCommentaire
        @brief Retourne le nombre de commentaires associés au document Reddit.

        @return: Nombre de commentaires.
        """
        return self.nbCommentaire
    
    def setNbCommentaire(self, nbCommentaire):
        """
        @fn setNbCommentaire
        @brief Modifie le nombre de commentaires associés au document Reddit.

        @param nbCommentaire (int): Nouveau nombre de commentaires.
        """
        self.nbCommentaire = nbCommentaire
        
    def __str__(self):
        """
        @fn __str__
        @brief Retourne une représentation textuelle du document Reddit.

        @return: Chaîne de caractères représentant le document Reddit.
        """
        return super().__str__() + "\n(Reddit)Nb Commentaire :" +str(self.nbCommentaire)
    
    def getType(self):
        """
        @fn getType
        @brief Retourne le type du document (Reddit).

        @return: Type du document -> Reddit.
        """
        return "Reddit"
    
class ArxivDocument(Document):
    """
    @class ArxivDocument
    @brief Représente un document provenant d'Arxiv, héritant de la classe Document.

    Ajoute l'attribut coAuteurs pour la liste des co-auteurs, spécifique à Arxiv.

    """
    #coAuteurs
    def __init__(self, titre="", auteur="", date="", url="", texte="", coAuteurs = []):
        """
        @brief Initialise une instance de la classe ArxivDocument.

        @param titre (str): Titre du document.
        @param auteur (str): Auteur du document.
        @param date (str): Date du document.
        @param url (str): URL du document.
        @param texte (str): Texte du document.
        @param coAuteurs (list): Liste des co-auteurs du document.
        """

        super().__init__(titre = titre, auteur = auteur, date = date, url = url, texte = texte, type="Arxiv")
        self.coAuteurs = coAuteurs
    
    def getCoAuteurs(self):
        """
        @fn getCoAuteurs
        @brief Retourne la liste des co-auteurs du document Arxiv.

        @return: Liste des co-auteurs.
        """
        return self.coAuteurs

    def __str__(self) -> str:
        """
        @fn __str__
        @brief Retourne une représentation textuelle du document Arxiv.

        @return: Chaîne de caractères représentant le document Arxiv.
        """
        return super().__str__() + "\n(Arxiv)Liste co-auteurs :" + str(self.coAuteurs)

    def getType(self):
        """
        @fn getType
        @brief Retourne le type du document (Arxiv).

        @return: Type du document -> Arxiv.
        """
        return "Arxiv"
    
class DocumentFactory:
    """
    @class DocumentFactory
    @brief Fabrique de documents pour créer des instances spécifiques de documents en fonction du type.

    """
    #staticmethod pour créer une factory
    @staticmethod
    def factory(document_type, Document):
        """
        @fn factory
        @brief Crée une instance spécifique de document en fonction du type.

        @param document_type (str): Type du document à créer ("Reddit" ou "Arxiv").
        @param Document (Document): Document générique à partir duquel créer le document spécifique.
        @return: Instance de document spécifique.
        """
        #Reddit ou Arxiv
        if document_type == "Reddit":
            return RedditDocument(Document.titre, Document.auteur, Document.date, Document.url, Document.texte, Document.nbCommentaire )
        if document_type == "Arxiv":
            return ArxivDocument(Document.titre, Document.auteur, Document.date, Document.url, Document.texte, Document.coAuteurs)
        
        assert 0, "Erreur : " + document_type