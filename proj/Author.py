class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = {}

    def add(self, doc_id, doc):
        self.production[doc_id] = doc
        self.ndoc += 1

    def __str__(self):
        return f"Auteur: {self.name}, Documents: {self.ndoc}"
