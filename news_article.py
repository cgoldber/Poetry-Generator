from sentiment_analysis import SentimentAnalysis
from keyword_extraction import KeywordExtractor
from news_api import NewsGetter
from word2vec import MyWord2Vec

class Article():
    """ Contains functions to interact with the news article that is retrieved
        from the NewsAPI.
        
    Attributes
    ----------
    article : dictionary
        Contains title, description, and content of a news article.
    sentiments : dictionary
        Contains the polarity and subjectivity retrieved from the sentiment
        analysis.
    keyword_extractor : KeyWordExtractor
        Class that is used to determine most important words in the article.

    Methods
    -------
    preprocess_test():
        Calls other classes to perform analyses on the article's text.
    get_pos_dicts():
        Maps part of speech to their corresponding counter of word freq.
    get_sentiment_score():
        Returns score corresponding to sentiment of article.
    get_title():
        Returns the article's title
    get_description():
        Returns the article's description
    get_text():
        Returns a formatted version of the article's text
    """
    def __init__(self):
        """ Gets a news article from NewsAPI and calls for the text to be 
            preprocessed.
        """
        news_getter = NewsGetter()
        self.article = news_getter.get_article()
        self.preprocess_text()
    
    def preprocess_text(self):
        """ Performs sentiment analysis on the text, extracts keywords from
            the text, and then adds the keywords it extracts to the text corpus
            stored in Word2Vec.
        """
        sentiment_analyzer = SentimentAnalysis(self.article['text'])
        self.sentiments = sentiment_analyzer.get_sentiment_results()

        self.keyword_extractor = KeywordExtractor(self.article['text'])
        self.keyword_extractor.process_text()

        word2vec = MyWord2Vec()
        word2vec.add_vocab(self.article['text'])

    
    def get_pos_dics(self):
        """ Returns a dictionary mapping entities/parts of speech to the
            keyword counters extracted from the reference article
            Returns:
                The part of speech dictionaries
        """
        return {"entities" : self.keyword_extractor.get_entities(),
                "nouns" : self.keyword_extractor.get_nouns(),
                "adjectives" : self.keyword_extractor.get_adjectives(),
                "verbs" : self.keyword_extractor.get_verbs()}
    
    def get_sentiment_score(self):
        """ Returns the polartiy of the sentiment analysis times the
            subjectivity.
        """
        return self.sentiments['polarity'] * self.sentiments['subjectivity']

    def get_title(self):
        """ Returns the title of the article.
        """
        return self.article['title']
    
    def get_description(self):
        """ Returns the description of the article
        """
        return self.article['description']
    
    def get_text(self):
        """ Formats the text of the article.
            Returns:
                The formatted text of the article.
        """
        filtered_text = []
        text = self.article['text'].split("\n")
        for line in text:
            if line:
                filtered_text.append(line)
        return "\n".join(filtered_text)
    