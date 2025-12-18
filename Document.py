class Document:

    def __init__(self, titre, auteur, date, url, texte, source = None):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.nb_mots = len(self.texte.split(' '))
        self.source = source  # nouveau champ pour la provenance

    def get_attributes(self):
        return (self.titre, self.auteur, self.date, self.url, self.texte)

    def getType(self):
        # méthode générique : sera redéfinie dans les classes filles
        return self.source

    def __str__(self):
        return self.titre


# Classe fille : RedditDocument
class RedditDocument(Document):
    def __init__(self, titre, auteur, date, url, texte, nb_commentaires):
        super().__init__(titre, auteur, date, url, texte)
        self.nb_commentaires = nb_commentaires
        self.source = "Reddit"  # on définit le type directement ici

    def get_nb_commentaires(self):
        return self.nb_commentaires

    def set_nb_commentaires(self, nb_commentaires):
        self.nb_commentaires = nb_commentaires

    def getType(self):
        return self.source

    def __str__(self):
        return f"[Reddit] {self.titre} ({self.nb_commentaires} commentaires)"


# Classe fille : ArxivDocument
class ArxivDocument(Document):
    def __init__(self, titre, auteurs, date, url, texte):
        super().__init__(titre, ", ".join(auteurs), date, url, texte)
        self.auteurs = auteurs
        self.source = "Arxiv"  # on définit le type ici

    def get_auteurs(self):
        return self.auteurs

    def set_auteurs(self, auteurs):
        self.auteurs = auteurs
        self.auteur = ", ".join(auteurs)

    def getType(self):
        return self.source

    def __str__(self):
        return f"[Arxiv] {self.titre} – Auteurs : {', '.join(self.auteurs)}"




