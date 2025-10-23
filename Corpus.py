class Corpus :

    def __init__(self, nom, authors, id2doc):
        self.nom = nom 
        self.authors = authors
        self.id2doc = id2doc
        self.ndoc = len(id2doc)
        self.naut = len(authors)

    def sort_by_date(self):
        
        
        sorted = dict(sorted(self.id2doc))