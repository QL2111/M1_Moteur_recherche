#Création du document

""" • titre : le titre du document
• auteur : le nom de l'auteur
• date : la date de publication
• url : l'url source
• texte : le contenu textuel du document """

class Document:
    #Initule de déclarer les attributs, le faire dans le constructeur
    def __init__(self, titre="", auteur="", date="", url="", texte="", type=""):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.__type = type #Attribut privé
    
    def affiche(self):
        return("Titre :", self.titre, "Auteur :", self.auteur, "Date :", self.date, "Url :", self.url, "Texte :",self.texte)
    
    #On doit faire un __str__ sinon ça retourne un pointeur vers l'object quand on print
    def __str__(self) ->str:
        return(f"Titre : {str(self.titre)}")
    
    #Redifinition dans les classes filles
    def getType(self):
        pass    
    
    def getAuteur(self):
        return self.auteur
    
    def getTexte(self) -> str:
        return self.texte
    
    def getTitre(self) -> str:
        return self.titre

#Test
#d1 = Document("TitreTest", "AuteurTest", "DateTest", "UrlTest", "TexteTest")
#print(d1.affiche())
#print("\nAffichage direct __str__")
#print(d1)

class RedditDocument(Document):
    #nbCommentaire
    def __init__(self, titre="", auteur="", date="", url="", texte="", nbCommentaire = 0):
        #Document.__init__(self, titre = titre, auteur = auteur, date = date, url = url, texte = texte) #Manière alternative sans super
        super().__init__(titre = titre, auteur = auteur, date = date, url = url, texte = texte, type="Reddit")     #pas de self avec super
        self.nbCommentaire = nbCommentaire
    
    def getNbCommentaire(self):
        return self.nbCommentaire
    
    def setNbCommentaire(self, nbCommentaire):
        self.nbCommentaire = nbCommentaire
        
    def __str__(self):
        return super().__str__() + "\n(Reddit)Nb Commentaire :" +str(self.nbCommentaire)
    
    def getType(self):
        return "Reddit"
    
class ArxivDocument(Document):
    #coAuteurs
    def __init__(self, titre="", auteur="", date="", url="", texte="", coAuteurs = []):
        super().__init__(titre = titre, auteur = auteur, date = date, url = url, texte = texte, type="Arxiv")
        self.coAuteurs = coAuteurs
    
    def getCoAuteurs(self):
        return self.coAuteurs

    def __str__(self) -> str:
        return super().__str__() + "\n(Arxiv)Liste co-auteurs :" + str(self.coAuteurs)

    def getType(self):
        return "Arxiv"
    
class DocumentFactory:
    #staticmethod pour créer une factory
    @staticmethod
    def factory(document_type, Document):
        #Reddit ou Arxiv
        if document_type == "Reddit":
            return RedditDocument(Document.titre, Document.auteur, Document.date, Document.url, Document.texte, Document.nbCommentaire )
        if document_type == "Arxiv":
            return ArxivDocument(Document.titre, Document.auteur, Document.date, Document.url, Document.texte, Document.coAuteurs)
        
        assert 0, "Erreur : " + document_type