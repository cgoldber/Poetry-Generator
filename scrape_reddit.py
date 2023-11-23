import praw
from collections import defaultdict, Counter
import re
import pickle
import numpy as np

""" Relevant subreddits to scrape for the word corpus.
"""
SUBREDDITS = [
    "Poetry",
    "ocpoetry",
    "PoetrySlam",
    "poetry_critics",
    "sonnets",
    "spokenword",
    "ShittyPoetry",
    "libraryofshadows",
    "EpicPoetry",
    "Songwriting",
    "PoeticReddit",
    "poetryreading",
    "PoetryOutLoud",
    "lyricalwriting",
    "poetasters",
    "wordsmith",
    "Poemaday",
    "poetic",
    "PoetryDaily",
    "poetrywriting",
    "WritingPrompts",
    "fifthworldpoetry",
    "Foodforthought",
    "poetryvideos",
    "youtubehaiku", 
    "OCPoetry",
    "Original_Poetry",
    "Dark_Poetry",
    "DDLC", 
    "writing",
    "AmateurPoetry",
    "UnsentPoetry",
    "poetryreading",
    "zen",
    "WritingPoetry",
    "PoetrySlam",
    "books",
    "Best_Poetry",
    "PsychoactivePoetry",
    "literature",
    "KeepWriting",
    "SadPoetry",
    "OccultPoetry",
    "SoulPoetry",
    "justpoetry",
    "teenagers",
    "lefthandpoetry",
    "Poem",
    "AskReddit",
    "news",
    "UpliftingNews",
    "politics",
    "worldnews",
    "Positive_News",
    "NewsofTheStupid",
    "NewsOfTheWeird",
    "Conservative",
    "Crypto_Currency_News",
    "AnythingGoesNews",
    "NewsAroundYou",
    "science",
    "WorldNews_Serious",
    "IntelligenceNews",
    "entertainment",
    "Showerthoughts",
    "WriteWithMe",
    "ArtBuddy",
    "INAT",
    "Collaboration",
    "ComicBookCollabs",
    "YouTubeCollab",
    "CreatorServices",
    "letsplaycollab",
    "NeedVocals",
    "RoleplayPartnerSearch",
    "screenwritingpartners",
    "ArtistLounge",
    "Writing",
    "worldbuilding",
    "DnDBehindTheScreen",
    "RPGdesign",
    "Solo_Roleplaying",
    "makecomics",
    "MangaMakers",
    "Songwriting",
    "WeAreTheMusicMakers",
    "gamedev",
    "gamedesign",
    "DestructiveReaders",
    "WriteResearch",
    "IamAFiction",
    "Lightbulb",
    "Brainstorming",
    "scificoncepts",
    "StoryIdeas",
    "story_ideas",
    "Fanfic_Ideas",
    "NYC",
    "Seattle",
    "LosAngeles",
    "Chicago",
    "Austin",
    "Portland",
    "SanFrancisco",
    "Boston",
    "Houston",
    "Atlanta",
    "Philadelphia",
    "Denver",
    "SeattleWa",
    "Dallas",
    "WashingtonDC",
    "SanDiego",
    "Pittsburgh",
    "Phoenix",
    "Minneapolis",
    "Orlando",
    "Nashville",
    "StLouis",
    "SaltLakeCity",
    "Columbus",
    "Raleigh",
    "NewOrleans",
    "Tampa",
    "KansasCity",
    "rva",
    "Charlotte",
    "Baltimore",
    "Detroit",
    "Vegas",
    "Indianapolis",
    "Cincinnati",
    "Miami",
    "Boulder",
    "Sacramento",
    "MadisonWi",
    "SanAntonio",
    "Cleveland",
    "Milwaukee",
    "Louisville",
    "Chattanooga",
    "LasVegas",
    "Buffalo",
    "Tucson",
    "Rochester",
    "FortWorth",
    "Albuquerque",
    "Charleston",
    "Tulsa",
    "Memphis",
    "Jacksonville",
    "bullcity",
    "DesMoines",
    "London",
    "Toronto",
    "Melbourne",
    "Vancouver",
    "Sydney",
    "Calgary",
    "Montreal",
    "Berlin"
]

class ScrapeReddit():
    """ Extracts text from reddit posts to create a bigram model that can be
        used to evaluate coherence based on how likely the words in a text are
        to come after one another.
        
    Attributes
    ----------
    model_path : string
        The path the bigram model will be saved to.
    model : dictionary
        Maps words to words that have proceeded them in a text and the 
        frequencies that they have done so.

    Methods
    -------
    preprocess_text():
        Removes unwanted tokens from text and converts to lowercase.
    create_bigrams():
        Creates a list of bigrams in a text.
    build_bigram_model():
        Creates bigram lists and converts them into a dictionary format.
    reset_model():
        Creates a new bigram model that extracts text from reddit pages.
    text_coherence():
        Uses bigram model to compute how likely the words in a text are likely
        to be next to each other.
    get_probable_next_word():
        Chooses random next word based on the frequency of co-occurence with
        the previous word in Reddit posts.
    get_amount():
        Returns how prevalent a word is in the Reddit submissions gathered.
    get_bigram_size():
        Returns the number of words in the bigram.
    """

    def __init__(self):
        """ Defines file path and opens previously made bigram model (do not
            necessarily need to remake model every time).
        """
        self.model_path = 'nlp_models/bigram_model.pkl'
        with open(self.model_path, 'rb') as file:
            self.model = pickle.load(file)

    def preprocess_text(self, text):
        """ Removes punctuation of text and converts it to lowercase.
            Args:
                text (string) : the text to preprocess
            Returns:
                the preprocessed text
        """
        # Remove punctuation and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        return text

    def create_bigrams(self, text):
        """ Iterates through a text to create a list where each element
            contains a word and the following word (corresponding bigrams).
            Args:
                text (string) : to be converted into a bigram
            Returns:
                the list of bigrams
        """
        words = text.split()
        bigrams = zip(words, words[1:])
        return list(bigrams)

    def build_bigram_model(self, reddit_texts):
        """ Iterates through texts extracted from subreddits, constructs bigram
            lists, and then constructs a bigram model. The model is a 
            dictionary where the keys are words and the values are Counters 
            that map the following words to the frequency they followed the
            original key. Then it saves the model.
            Args:
                reddit_texts (list) : strings to form base of bigram model
        """
        bigram_model = defaultdict(Counter)
        for text in reddit_texts:
            preprocessed_text = self.preprocess_text(text)
            bigrams = self.create_bigrams(preprocessed_text)
            for bigram in bigrams:
                bigram_model[bigram[0]][bigram[1]] += 1
        
        print(f"Created bigram model with {len(bigram_model.keys())} words")
        with open(self.model_path, 'wb') as file:
            pickle.dump(bigram_model, file)

        self.model = bigram_model
    
    def reset_model(self):
        """ Uses the Reddit API to access various subreddit pages, accesses 
            1000 of the top submissions for each subreddit, and send the 
            text from the submissions to be processed by a bigram model.
        """
        # Access Reddit api
        reddit_client_id = 'DL6ZjiFxKjYXdVRvsKrB3g'
        reddit_client_secret =  '_RPu8G8yB3GAmMmCfq73h7860ViCTg'
        reddit_user_agent = 'kkkkccccc'
        reddit = praw.Reddit(client_id=reddit_client_id,
                            client_secret=reddit_client_secret,
                            user_agent=reddit_user_agent)

        # Collect text from Reddit posts
        corpus = []
        for subreddit_name in SUBREDDITS:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.top(limit=1000):
                corpus.append(submission.selftext)

        # Build bigram model
        self.build_bigram_model(corpus)
    
    def text_coherence(self, text):
        """ Evalutes how coherent the text is using the bigram model. To 
            compute this value, the algorithm sums the frequency of every 
            consequetive word coming after the previous word, and divides the
            total by the number of words.

        """
        sentence = self.preprocess_text(text) 
        coherence_weighted_count, total_weight = 0, 0
        for i in range(len(sentence) - 1):
            prev, next = sentence[i], sentence[i+1]
            if prev in self.model and next in self.model[prev].keys():
                coherence_weighted_count += self.model[prev][next]
            total_weight += 1

        return coherence_weighted_count / total_weight
    
    def get_probable_next_word(self, word):
        """ Given a word, returns a random word that is likely to come next.
            The probabilities are weighted by how frequent each word in the
            bigram came after the previous word in the existing Reddit corpus.
            Args:
                word (string) : the most recent word
            Returns:
                The next word to be added to the poem
        """
        word = self.preprocess_text(word)
        if word not in self.model: #word not in bigram model
            return None

        # Probability based on freq of word combination in bigram
        probs = [self.model[word][next] for next in self.model[word].keys()]
        probs = np.array(probs) / sum(probs)
        return np.random.choice(list(self.model[word].keys()), p=probs)

    def get_amount(self, word):
        """ Returns the number of times a given word appears in the reddit
            corpus.
            Args:
                word (string) : the word whose frequency is desired
            Returns:
                The frequency of the word in the Reddit corpus
        """
        if word in self.model.keys():
            return sum(self.model[word].values())
        else:
            return 0
    
    def get_bigram_size(self):
        """ Returns the size of the bigram
        """
        return len(self.model)
