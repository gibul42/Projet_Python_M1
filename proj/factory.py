from Document import RedditDocument, ArxivDocument

class DocumentFactory:
    def create(self, source, *args):
        if source == "reddit":
            return RedditDocument(*args)
        elif source == "arxiv":
            return ArxivDocument(*args)
        else:
            raise ValueError("Source inconnue")
