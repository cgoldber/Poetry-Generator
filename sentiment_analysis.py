from textblob import TextBlob


class SentimentAnalysis():
    """ Performs sentiment analysis on a piece of text.

    Attributes
    ----------
    text : string
        The text that sentiment analysis will be performed on.
    sentiment_results : dict
        The label, polarity, and subjectivity results of the analysis.

    Methods
    -------
    perform_sentiment_analysis():
        Performs sentiment analysis on the text.
    get_sentiment_results():
        Returns the sentiment analysis results
    """
    
    def __init__(self, text):
        """ Calls to perform sentiment analyis on the text immediately.
        """
        self.text = text
        self.sentiment_results = None
        self.perform_sentiment_analysis()

    def perform_sentiment_analysis(self):
        """ Uses TextBlob library to perform sentiment analysis on the test.
        """
        blob = TextBlob(self.text)
        sentiment_polarity = blob.sentiment.polarity
        sentiment_subjectivity = blob.sentiment.subjectivity

        self.sentiment_results = {
            "polarity": sentiment_polarity,
            "subjectivity": sentiment_subjectivity,
        }
        
    def get_sentiment_results(self):
        """ Returns the sentiment analysis results.
        """
        return self.sentiment_results
    