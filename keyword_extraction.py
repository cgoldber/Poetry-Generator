import spacy 
from collections import Counter
from gensim.models import Word2Vec
from scrape_reddit import ScrapeReddit


class KeywordExtractor():
    """ Extracts important keywords from a reference text where the 
    'importance' is computed based on their frequency and uniqueness compared 
    to a large corpus of text. Then, expands the keyword data to include 
    synonyms.
        
    Attributes
    ----------
    text : string
        The text that the content analysis will be performed on.
    entities : Counter
        Strings corresponding to entities mapped to their frequency.
    nouns : Counter
        Strings corresponding to nouns mapped to their frequency.
    adjectives : Counter
        Strings corresponding to adjectives mapped to their frequency.
    verbs : Counter
        Strings corresponding to verbs mapped to their frequency.

    Methods
    -------
    is_wanted_tok():
        Filters text for unwanted tokens.
    preprocess_text():
        Filters out punctuation and unwanted chars before analyzing content.
    calculate_frequencies():
        Stores how many times each word occurs in article scaled by their
        overall frequency in a greater corpus.
    get_context_aware_synonyms():
        Uses Word2Vec to compute context-aware synonyms.
    add_context_aware_synonyms():
        Expands keyword counters mined from ref article to include synonyms.
    process_text():
        High level that calls preprocessing, keyword mining, and synonym
        expanding.
    get_entities():
        Returns entity Counter
    get_nouns():
        Returns noun Counter
    get_adjectives():
        Returns adjective Counter
    get_verbs():
        Returns verb Counter
    """
    def __init__(self, text):
        self.text = text

        self.entities = Counter()
        self.nouns = Counter()
        self.adjectives = Counter()
        self.verbs = Counter()

        self.nlp = spacy.load("en_core_web_sm") # Load the spaCy language model
    
    def is_wanted_tok(self, token):
        """ Returns whether a token should be filtered out to avoid non-word
            tokens.
            Arguments:
                token (nlp token) : the token to be analyzed
            Returns:
                Boolean indicating whether token will be included in analysis
        """
        unwanted_chars = ['-', '|', '\', ''', '0', '1', '2', '3', '4', '5', \
                           '9', '0', '?', '@', '\n', ' ']
        for char in unwanted_chars:
            if char in token.text:
                return False
        
        if len(token.text) == 1 and token.text != 'a' and token.text != 'i':
            return False

        return True

    def preprocess_text(self):
        """ Uses spacy to preprocess text and filter out unwanted characters
            and symbols.
        """
        doc = self.nlp(self.text)
        tokens = []
        for token in doc:
            if not token.is_punct and not token.is_stop and \
                                                    self.is_wanted_tok(token):
                if not token.ent_type_:
                    token = token.text.lower() #Convert to lowercase
                else:
                    token = token.text
                tokens.append(token)
        self.text = ' '.join(tokens)

    def calculate_frequencies(self):
        """ Iterates through all of words in the text. For each word, it 
            calculates how frequently it occurs in the aritcle, and divides
            it by how frequently it occurs in the Reddit corpus to emphasize
            more unique words relevant to the article. Then, it stores the word
            and its associated value sorted by part of speech.
        """
        reddit_scraper = ScrapeReddit()
        #Get frequency of words in ref article
        total_counts = Counter()
        for word in self.text:
            total_counts[word] = reddit_scraper.get_amount(word) 

        #scale by overall frequency and sort by POS
        processed_text = self.nlp(self.text)
        for token in processed_text:
            val = int(1 / (total_counts[token.text] + 1)) 
            if token.ent_type_:
                self.entities[token.text] += val
            if token.pos_ == "NOUN":
                self.nouns[token.text] += val
            elif token.pos_ == "ADJ":
                self.adjectives[token.text] += val
            elif token.pos_ == "VERB":
                self.verbs[token.text] += val
    
    def get_context_aware_synonyms(self, word):
        """ Uses Word2Vec library to compute context-aware synonyms of a given
            word.
            Arguments:
                word (str) : word to get synonyms of
            Returns:
                List of context-aware synoynms
        """
        sentences = [s.split() for s in self.text.split('.') if s.strip()]
        word2vec_model = Word2Vec(sentences=sentences, vector_size=100, 
                                  window=5, min_count=1, workers=4)
        if word in word2vec_model.wv.key_to_index:
            sim_words = word2vec_model.wv.most_similar(word, topn=5)
            context_aware_synonyms = [sim_word for sim_word, _ in sim_words]
            return context_aware_synonyms
        return []

    def add_context_aware_synonyms(self):
        """ Generates context-aware synonyms of every keyword used in the
            article to expand the possible vocabulary set that relates to 
            the article. Records the frequency of the synonyms as one count
            less than the original word.
        """
        for noun, count in self.nouns.copy().items():
            synonyms = self.get_context_aware_synonyms(noun)
            for synonym in synonyms:
                self.nouns[synonym] += count - 1 
        
        for adj, count in self.adjectives.copy().items():
            synonyms = self.get_context_aware_synonyms(adj)
            for synonym in synonyms:
                self.adjectives[synonym] += count - 1
        
        for verb, count in self.verbs.copy().items():
            synonyms = self.get_context_aware_synonyms(verb)
            for synonym in synonyms:
                self.verbs[synonym] += count - 1
    
    def process_text(self):
        """ High-level function that collects and preprocesses the reference
            article text, calculates the frequent words used, and expands the 
            vocabulary with synonyms.
        """
        self.preprocess_text()
        self.calculate_frequencies()
        self.add_context_aware_synonyms()
        
    def get_entities(self):
        """ Returns the Counter of entities.
        """
        return self.entities
    
    def get_nouns(self):
        """ Returns the Counter of nouns.
        """
        return self.nouns
    
    def get_adjectives(self):
        """ Returns the Counter of adjectives.
        """
        return self.adjectives
    
    def get_verbs(self):
        """ Returns the Counter of verbs.
        """
        return self.verbs
    