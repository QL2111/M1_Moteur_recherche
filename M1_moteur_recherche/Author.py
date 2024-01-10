"""
@file Author.py
@brief Fichier contenant la classe Author


"""


from Document import Document
from Document import ArxivDocument

class Author:
    """
    @class Author
    @brief Représente un auteur avec son nom, le nombre de documents associés et ses productions.

    Cette classe contient le nombre de documents associés à un auteur ainsi que des statistiques sur ses productions.
    """
    def __init__(self, name):
        """
        @fn __init__
        @brief Initialise une instance de la classe Author.

        @param name (str): Nom de l'auteur.
        """
        self.name = name
        self.ndoc = 0
        self.production = []

    def add(self, doc):
        """
        @fn add
        @brief Ajoute un document à la production de l'auteur.

        Incrémente également le nombre total de documents associés à l'auteur.

        @param doc (Document): Document à ajouter à la production.
        """
        # la ligne de code -> if doc in self.production ne marche pas, on va donc contourner en utilisant les titres
        listes_titres_production = [doc.getTitre() for doc in self.production]
        # print(listes_titres_production)
        # print(doc.getTitre())
        if doc.getTitre() not in listes_titres_production:
            # print("j'ai été ajouté")
            self.ndoc += 1
            self.production.append(doc)

    def __str__(self) -> str:
        """
        @fn __str__
        @brief Retourne une représentation sous forme de chaîne de l'objet Author.

        @return str: Chaîne représentant l'auteur.
        """
        return(f"Nom : {str(self.name)}" )
    

    def get_statistiques(self):
        """
        @fn get_statistiques
        @brief Retourne les statistiques de l'auteur.

        Les statistiques montrent le nombre de document que l'auteur entré en paramètre à produit et sa taille moyenne de document.

        @return str: Chaîne représentant les statistiques de l'auteur.
        """
        taille_moyenne = 0
        for doc in self.production:
            taille_moyenne += len(doc.texte)
        taille_moyenne = taille_moyenne / self.ndoc
        return(f"L'auteur {self.name} a {str(self.ndoc)} documents, ses documents ont en moyenne une taille de : {taille_moyenne} mots" )
    
        

#Test
#a1 = Author("AuthorTest", 10)
#print(a1)