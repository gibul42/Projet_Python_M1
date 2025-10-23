class Document:

    def __init__(self, titre, auteur, date, url, texte):
        self.titre = titre
        self.auteur = auteur
        self.date = date
        self.url = url
        self.texte = texte
        self.nb_mots = len(self.texte.split(' '))

    def get_attributes(self):
        return (self.titre, self.auteur, self.date, self.url, self.texte)
    
    def __str__(self):
        return self.titre
    
class Author:

    def __init__(self, nom, ndoc):
        self.nom = nom
        self.ndoc = ndoc
        self.production = {}
        

    def add(self, key, value):
        self.production[key] = value

    def __str__(self):
        return self.nom
    
    def get_stat(self):
        return len(self.production)