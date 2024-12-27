import torch
import numpy as np
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.snowball import EnglishStemmer
from typing import Iterable


class TFIDVectAndStem:
    def __init__(self, min_df, max_df):
        self.stemmer = EnglishStemmer()
        self.tfidf = TfidfVectorizer(
            analyzer="word",
            ngram_range=(1, 2),
            min_df=min_df,
            max_df=max_df,
            stop_words="english",
        )
        self.__tf_matrix = None
        self.vocab = None
        self.features = None

    @property
    def tf_matrix(self):
        if self.__tf_matrix is not None:
            return TFIDVectAndStem.__sparse_to_torch(self.__tf_matrix)

    def __sparse_to_torch(sparse, dtype=torch.float32):
        torch_sparse = torch.sparse_coo_tensor(
            np.array(sparse.nonzero()), sparse.data, sparse.shape, dtype=dtype
        )
        return torch_sparse.to_dense()

    def __snowball(self, text) -> str:
        text = str(text)
        stemmed_text = []
        for word in text.split(" "):
            stemmed_text.append(self.stemmer.stem(word))
        return " ".join(stemmed_text)

    def fit(self, texts: Iterable[str]):
        texts = [re.sub("[^A-Za-z ]+", "", text) for text in texts]
        stemmed = [self.__snowball(text) for text in texts]
        self.__tf_matrix = self.tfidf.fit_transform(list(stemmed))
        self.vocab = self.tfidf.vocabulary_
        self.features = self.tfidf.get_feature_names_out()

    def __call__(self, texts: Iterable[str]):
        texts = [re.sub("[^A-Za-z ]+", "", text) for text in texts]
        stemmed = [self.__snowball(text) for text in texts]
        sparse = self.tfidf.transform(stemmed)
        return TFIDVectAndStem.__sparse_to_torch(sparse)
