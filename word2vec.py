from gensim.models import Word2Vec as GensimWord2Vec
import spacy
from get_inspiring_poems import PoetryDB

class MyWord2Vec:
    """ Class for creating, saving and adding to Word2Vec models, which are 
        models that converts words into vectors while considering their
        semantic meanings.

        Attributes
        ----------
        nlp : spacy
            Spacy library for tokenizing words.

        Methods
        -------
        make_poetry_base():
            Makes Word2Vec model with words from PoetryDB.
        add_vocab():
            Adds words to Word2Vec model and retrains it.
    """

    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def make_poetry_base(self):
        """ Populates Word2Vec model with all of the words in the PoetryDB to
            represent them as vectors. Then, it saves the Word2Vec model for 
            later use.
        """
        poetry_getter = PoetryDB()
        poetry_getter.retrieve_all_poem_types()
        poetry_text = poetry_getter.get_all_poems()

        common_texts = []
        for line in poetry_text:
            tokens = [token.text for token in self.nlp(line)]
            common_texts.append(tokens)

        word2vec = GensimWord2Vec(sentences=common_texts, vector_size=100, 
                                  window=5, min_count=1, workers=4)
        word2vec.save("nlp_models/base_word2vec.model")
    
    def add_vocab(self, text):
        """ Adds text to the already initialized Word2Vec model and trains the
            model to capture the semantic similarity between words and their
            corresponding vectors. Then, saves the updated model.
            Args:
                article_text (list) : strings to be added to Word2Vec model

        """
        new_words = [token.text for token in self.nlp(text)]

        word2vec_model = GensimWord2Vec.load("nlp_models/base_word2vec.model")
        word2vec_model.build_vocab([new_words], update=True)
        word2vec_model.train([new_words], total_examples=1, epochs=1)

        # Save the updated model
        word2vec_model.save("nlp_models/word2vec.model")
