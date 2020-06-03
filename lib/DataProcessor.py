from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from lib.Translator import Translator
import nltk


class DataProcessor:

    def __init__(self):
        self.polarities = []  # tableu des polarités
        self.sentences = {}  # dict des phrases et le tri des mots
        self.words_count = {'pos': {}, 'neg': {}, 'neu': {}}  # Reduce

    def process(self, inputs):

        analyzer = SentimentIntensityAnalyzer()

        if isinstance(inputs, list):
            for sentence in inputs:
                self.polarities.append(analyzer.polarity_scores(Translator.translate(sentence)))
                self.getSentimentWords(sentence)

    def getSentimentWords(self, sentence):

        tokenized_sentence = nltk.word_tokenize(sentence)
        sid = SentimentIntensityAnalyzer()

        pos_words = []
        neu_words = []
        neg_words = []

        for word in tokenized_sentence:
            if (sid.polarity_scores(word)['compound']) >= 0.1:
                pos_words.append(word)
            elif (sid.polarity_scores(word)['compound']) <= -0.1:
                neg_words.append(word)
            else:
                neu_words.append(word)

        self.sentences[sentence] = {'pos': pos_words, 'neu': neu_words, 'neg': neg_words}

        self.reduce(pos_words, neu_words, neg_words)

    def reduce(self, pos, neu, neg):
        self.iterate(pos, 'pos')
        self.iterate(neu, 'neu')
        self.iterate(neg, 'neg')

    def iterate(self, words, pol):
        for word in words:
            if word in self.words_count[pol][words]:
                self.words_count[pol][words] += 1
            else:
                self.words_count[pol][words] = 1
