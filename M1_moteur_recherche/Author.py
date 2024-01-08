""" • name : son nom
• ndoc : nombre de documents publies
• production : un dictionnaire des documents ecrits par l'auteur """
from Document import Document
from Document import ArxivDocument

class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = []

    def add(self, doc):
        self.ndoc += 1
        self.production.append(doc)

    def __str__(self) -> str:
        return(f"Nom : {str(self.name)}" )
    
    def get_statistiques(self):
        taille_moyenne = 0
        for doc in self.production:
            taille_moyenne += len(doc.texte)
        taille_moyenne = taille_moyenne / self.ndoc
        return(f"L'auteur {self.name} a {str(self.ndoc)} documents, ses documents ont en moyenne une taille de : {taille_moyenne}" )
    
        

#Test
#a1 = Author("AuthorTest", 10)
#print(a1)