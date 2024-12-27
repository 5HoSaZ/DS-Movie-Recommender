from nltk.stem.snowball import EnglishStemmer
import json
import re


class KewwordsHighlighter:
    def __init__(self, kw_path):
        self.stemmer = EnglishStemmer()
        with open(kw_path, "r") as data:
            self.kw_dict: dict = json.load(data)

    def __call__(self, text: str):
        text = re.sub("[^A-Za-z ]+", "", text)
        stemmed_words = []
        inv_stem = dict()
        for word in text.split(" "):
            stemmed = self.stemmer.stem(word)
            inv_stem[stemmed] = word
            stemmed_words.append(stemmed)
        stemmed_text = " " + " ".join(stemmed_words) + " "
        for kw in self.kw_dict:
            stemmed_text = stemmed_text.replace(f" {kw} ", f" :blue[{kw}] ")
        for sword in inv_stem:
            stemmed_text = stemmed_text.replace(f" {sword} ", f" {inv_stem[sword]} ")
            stemmed_text = stemmed_text.replace(
                f":blue[{sword}]", f":blue[{inv_stem[sword]}]"
            )
        return stemmed_text.strip()
