import random
import numpy as np
import pronouncing
import string
import spacy
from language_tool_python import LanguageTool
from gensim.models import Word2Vec as GensimWord2Vec
from scrape_reddit import ScrapeReddit

class Mutator():
    """ Contains tools for mutating and altering the associated poem.

    Attributes
    ----------
    sonnet : list
        The lines of the associated poem.
    ref_article : Article
        The reference article.
    rhyme_scheme : list
        List encoding the desired rhyme scheme.
    nlp : spacy 
        Spacy tool for tokenizing words.
    word2vec : Word2Vec
        Pretrained Word2Vec for semantic embedding of words.
    grammar_tool : LanguageTool
        Tool for checking grammar

    Methods
    -------
    get_random_word():
        Selects random word from article keywords weighted by their freq.
    get_semantically_similar_word():
        Uses Word2Vec to return a semantically similar word.
    replace_keyword():
        Calls to get semantically similar keyword based on pos.
    replace_keywords():
        Calls to replace all nouns, verbs, and adjectives in a text.
    filter_subwords():
        Ensures no potential rhymes are subwords of the rhyming word.
    generate_rhyme():
        Generates a rhyme of a given word and a desires part of speech.
    get_last_word_and_idx():
        Returns the last word and index of that word of a sentence.
    incorporate_rhyme_scheme():
        Imposes the rhyme scheme on the poem.
    punctuation_spacing():
        Helper function to counteract de-spacing between words and punctuation
        in corrector method to correspond to rest of system.
    correct_grammar():
        Uses LanguageTool to correct grammar of randomly selected line.
    swap_words_from_article():
        Randomly selects word from each line of Sonnet to be replaced with
        article keyword.
    swap_words_using_bigram():
        Uses bigram to replace part of line with most likely next words based
        on Reddit corpus.
    mutate():
        Calls to perform a mutation on the poem
    get_sonnet():
        Returns the text of the poem.
    """

    def __init__(self, sonnet, ref_article, rhyme_scheme):
        """ Stores the poem information and the relevant language tools.
        """
        self.sonnet = sonnet
        self.ref_article = ref_article
        self.rhyme_scheme = rhyme_scheme
        self.nlp = spacy.load("en_core_web_sm")
        self.word2vec = GensimWord2Vec.load("nlp_models/word2vec.model")
        self.grammar_tool = LanguageTool('en-US')   

    def get_random_word(self, dic):
        """ Given a dictionary of words mapped to values, selects a random 
            word based on the probability of their associated value.
            Returns:
                a randomly selected word
        """
        words, freqs = list(dic.keys()), list(dic.values())
        norm_freqs = [freq / sum(freqs) for freq in freqs]
        return np.random.choice(words, p = norm_freqs)

    def get_semantically_similar_word(self, original_word, pos):
        """ Uses the trained Word2Vec Model to compute the semantic similarity
            between the given word and all of the keywords of the same part 
            of speech extracted from the reference article. Then it chooses
            a random article keyword weighted by the similarity score
            multiplied by the square root of the prevelence scores computed
            earlier.
            Args:
                original_word (string) : word to be replaces
                pos (string) : part of speech of original word
        """
        pos_dics = self.ref_article.get_pos_dics()
        word_freqs = pos_dics[pos]

        # If the word is not in the model, return a random word
        if original_word not in self.word2vec.wv:
            return self.get_random_word(word_freqs)

        # Weight each potential word by the square root 
        weighted_sims = {}
        for new_word, freq in word_freqs.items():
            if new_word in self.word2vec.wv:
                sim = self.word2vec.wv.similarity(original_word, new_word)
                weighted_sims[new_word] = max(0, sim) * np.sqrt(freq)

        return self.get_random_word(weighted_sims)
    
    def replace_keyword(self, token):
        """ Given a token, finds a semantically similar keyword of the same
            part of speech and returns it.
            Args:
                token (spacy token) : the word to be replaced
            Returns:
                The semenatically similar word of the same part of speech.
        """
        if token.ent_type_:
            new_text = self.get_semantically_similar_word(token.text, 
                                                          'entities')
        elif token.pos_ == "NOUN":
            new_text = self.get_semantically_similar_word(token.text, 
                                                          'nouns')
        elif token.pos_ == "ADJ":
            new_text = self.get_semantically_similar_word(token.text, 
                                                          'adjectives')
        elif token.pos_ == "VERB":
            new_text = self.get_semantically_similar_word(token.text, 
                                                          'verbs')
        else:
            new_text = token.text
        return new_text

    def replace_keywords(self):
        """ Replaces all of the nouns, adjectives, and verbs in the first 
            generation poems with keywords (and their synonyms) from the 
            reference articles.
        """
        for i in range(len(self.sonnet)):
            tokens = []
            for token in self.nlp(self.sonnet[i]):
                tokens.append(self.replace_keyword(token))
            self.sonnet[i] = ' '.join(tokens)
        self.incorporate_rhyme_scheme()
            
    def filter_subwords(self, original_word, rhyming_words):
        """ Filters list of potential rhymes to exclude any words that contain
            the original word or vice versa. This function is motivated by 
            getting a more diverse set of rhymes.
            Args:
                original_word (string) : the word to be rhymed with
                rhyming_words (list) : the list of potential rhyming words
            Returns:
                A filtered version of rhyming words that does not contain
                subwords.
        """
        new_potential_rhymes = []
        for new_word in rhyming_words:
            if original_word not in new_word.text and \
                                            new_word.text not in original_word:
                new_potential_rhymes.append(new_word)
        return new_potential_rhymes
    
    def generate_rhyme(self, pos, to_rhyme):
        """ Given a tokenized version of a word to rhyme with, returns a rhyme
            that is of a specified part of speech. If there are no rhymes of
            that part of speech, returns a random rhyming word. If there are
            no rhyming words, returns the word to rhyme with.
            Args:
                pos (string) : the desired part of speech of the new rhyme
                to_rhyme (string) : the word to rhyme with
            Returns:
                The rhyming word
        """
        rhyming_words = self.nlp(" ".join(pronouncing.rhymes(to_rhyme.text)))
        rhyming_words = self.filter_subwords(to_rhyme.text, rhyming_words)
        if pos == "NOUN":
            rhyme_options = [r for r in rhyming_words if r.pos_ == "NOUN"]
        elif pos == "ADJ":
            rhyme_options = [r for r in rhyming_words if r.pos_ == "ADJ"]
        elif pos == "VERB":
            rhyme_options = [r for r in rhyming_words if r.pos_ == "VERB"]
        else:
            rhyme_options = [r for r in rhyming_words if r.pos_ != "ADJ" \
                             and r.pos_ != "NOUN" and r.pos_ != "VERB"]
        
        if not rhyming_words: # Return original word if no rhymes
            return to_rhyme.text
        if not rhyme_options: # Return random rhyme if none of the correct pos
            return np.random.choice(rhyming_words).text 
        
        # Optimally, return rhyme of the desired pos
        return np.random.choice(rhyme_options).text 
    
    def get_last_word_and_idx(self, words):
        """ Returns the last word (excluding punctuation) and its
            corresponding index for a given sentence.
            Args:
                words (string) : the sentence to get the last word of
            Returns:
                The last word and idx of a sentence.
        """
        for i in range(len(words) - 1, -1, -1):
            if words[i] not in string.punctuation:
                return words[i], i

    def incorporate_rhyme_scheme(self):
        """ This function imposes the rhyme scheme of the poem. For each 
            rhyming line pairs, it gets the last word from each line. If the
            words already rhyme, it moves on. If not, the second line of the 
            pair is replaced with a rhyme of the same part of speech to help
            preserve coherence. Then, the new line is added to the Sonnet.
        """
        for line1, line2 in self.rhyme_scheme:
            to_rhyme, _ = self.get_last_word_and_idx(self.sonnet[line1].split())
            prev_word, idx_to_replace = self.get_last_word_and_idx(self.sonnet[line2].split())
            
            if prev_word != to_rhyme and \
                          prev_word in " ".join(pronouncing.rhymes(to_rhyme)):
                continue  # lines already rhyme

            pos = self.nlp(prev_word)[0].pos_
            new_word = self.generate_rhyme(pos, self.nlp(to_rhyme)[0])
            
            prev_line = self.sonnet[line2].split()
            prev_line[idx_to_replace] = new_word
            self.sonnet[line2] = " ".join(prev_line)
    
    def punctuation_spacing(self, line):
        """ The system is designed to treat punctuation spaced from all words, 
            but the LanguageTool grammar corrector deletes those spaces. So,
            this function undos that by putting spaces between punctuation and
            words.
            Args:
                line (string) : the string to reformat
            Returns:
                The reformatted line.
        """
        result = []
        words = line.split()
        for word in words:
            if word[0] in string.punctuation and word[-1] in string.punctuation:
                result.append(word[0])
                result.append(word[1:-1])
                result.append(word[-1])
            elif word[0] in string.punctuation:
                result.append(word[0])
                result.append(word[1:])
            elif word[-1] in string.punctuation:
                result.append(word[:-1])
                result.append(word[-1])
            else:
                result.append(word)
        return ' '.join(result)

    def correct_grammar(self):
        """ Chooses a random line of the Sonnet and applied the LanguageTool
            grammar correct method on it.
        """
        idx = random.randint(0, 13)
        corrected_line = self.grammar_tool.correct(self.sonnet[idx])
        new_line = self.punctuation_spacing(corrected_line)
        self.sonnet[idx] = new_line
    
    def swap_words_from_article(self):
        """ For each line of the Sonnet, selects one keyword to be swapped
            with a semantically similar word of the same part of speech
            from the reference article.
        """
        new_sonnet = []
        for line in self.sonnet:
            keywords = [tok for tok in self.nlp(line) if not tok.is_punct]
            random_keyword = np.random.choice(keywords)
            new_text = self.replace_keyword(random_keyword)
            line = line.replace(random_keyword.text, new_text, 1)
            new_sonnet.append(line)
        self.sonnet = new_sonnet
    
    def swap_words_using_bigram(self):
        """ Chooses a random line from the Sonnet and a random starting index
            of the line to start the swap. From the start index on, uses the
            reddit bigram to predict the next most likely word given the
            previous word and continues until the end of the line.
        """
        # Chooses a random line and random start index of line that is not
        # punctuation
        line_idx = random.randint(0, len(self.sonnet) - 1)
        line = self.sonnet[line_idx].split()
        start_idx = random.randint(0, len(line) - 2)
        while line[start_idx] in string.punctuation:
            start_idx = random.randint(0, len(line) - 2)
        curr_word = line[start_idx]

        # Uses reddit bigram to generate next most likely word until the end
        # of the line
        reddit_scraper = ScrapeReddit()
        new_line = line[:start_idx + 1]
        for i in range(start_idx + 1, len(line)):
            if line[i] in string.punctuation:
                new_line.append(line[i]) # Preserve punctuation
            else:
                curr_word = reddit_scraper.get_probable_next_word(curr_word)
                if not curr_word: #word not in bigram -> leave alone
                    curr_word = line[i]
                new_line.append(curr_word)

        new_line = " ".join(new_line)
        self.sonnet[line_idx] = new_line

    def mutate(self):
        """ With equal probability, perform one of the following mutations:
            swap poems words with keywords from reference article, swap
            the end of a line with words generated using the bigram model, or
            use the LanguageTool correct to correct a random line. After 
            mutating, ensures the rhyme scheme is still intact.
        """
        rand_choice = random.random()
        if rand_choice < 0.33:
            self.swap_words_from_article()
        elif rand_choice < 0.66:
            self.swap_words_using_bigram()
        else:
            self.correct_grammar()
        self.incorporate_rhyme_scheme()
    
    def get_sonnet(self):
        """ Returns the lines of text that make up the sonnet.
        """
        return self.sonnet
    