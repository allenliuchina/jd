from haystack import indexes

from .models import Good


class GoodIndex(indexes.Indexable, indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Good

    def index_queryset(self, using=None):
        return self.get_model().objects.all()
