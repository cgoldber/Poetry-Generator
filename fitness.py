from sentiment_analysis import SentimentAnalysis
from language_tool_python import LanguageTool
import spacy
from scrape_reddit import ScrapeReddit
import string
import pronouncing


class Fitness():
    """ Represents the fitness of a poem by considering factors related to the
        poem's alignment with the inspiring article, coherence, and sound.
        
    Attributes
    ----------
    ref_article : Article
        The article that the poem is based on.
    fitness : int
        The value corresponding to the fitness.
    text : list
        Contains the text of the poem where each element corresponds to a line.
    rhyme_scheme : list
        Contains a list corresponding to the current rhyme scheme.
    grammar_tool : LanguageTool
        Tool for evaluating English grammar of a sentence.
    nlp : spacy
        Spacy library for tokenizing text.

    Methods
    -------
    get_sentiment():
        Performs sentiment analysis on the poem.
    compute_sentiment_difference():
        Calculates the difference in sentiment between the poem and article.
    compute_grammar_score():
        Comptutes score based on number of grammatical errors.
    simile_detection():
        Comptutes score based on number of lines that could have similes.
    get_coherence():
        Comptutes coherence of poem based on Reddit bigram model.
    count_alliterations():
        Comptutes score based on number of alliterations in poem.
    count_assonance():
        Comptutes scores based on amount of assonance.
    article_keyword_count():
        Comptutes scores based on number of keywords used from article.
    get_last_word():
        Retrieves last word of a sentence.
    rhyme_score():
        Evaluates how much the poem's rhyme scheme aligns with the desired
        rhyme scheme.
    compute_fitness():
        Combines the above factors to generate one fitness score.
    set_test():
        Replaces the text of the object's associated poem.
    """

    def __init__(self, text, ref_article, rhyme_scheme):
        """ Sets the relevant poetry text and reference article, and loads
            the relevant language tools.
        """
        self.ref_article = ref_article
        self.text = text
        self.rhyme_scheme = rhyme_scheme
        self.grammar_tool = LanguageTool('en-US')
        self.nlp = spacy.load("en_core_web_sm")
        self.fitness = 0
    
    def get_sentiment(self):
        """ Computes sentiment of the poem by multiplying the polarity with
            the subjectivity.
            Returns:
                The sentiment score.
        """
        sentiment_analyzer = SentimentAnalysis("\n".join(self.text))
        sentiment_analyzer.perform_sentiment_analysis()
        sentiments = sentiment_analyzer.get_sentiment_results()
        return sentiments['polarity'] * sentiments['subjectivity']
    
    def compute_sentiment_difference(self):
        """ Calculates the difference between the poem and reference article's
            polarities.
            Returns:
                The difference between poem and article's sentiment.
        """
        sent_val = self.get_sentiment()
        return abs(sent_val - self.ref_article.get_sentiment_score())
    
    def compute_grammar_score(self):
        """ Uses grammar tool to count number of grammatical errors in a
            sentence and divides it by the total number of words. Since the 
            system wants to maximize the fitness, the reciprocal is returned
            to prioritize poems with less grammar errors.
            Returns:
                The score corresponding to the poem's grammar.
        """
        text_as_string = " ".join(self.text)
        n_errors = len(self.grammar_tool.check(text_as_string))
        n_words = len(text_as_string.split())
        return n_words / (n_errors + 1e-12)

    def simile_detection(self):
        """ Counts the number of lines in the poem that have "like" and "as" 
            in them and divides this by the number of total words. The purpose
            of this function is to encourge the inclusion of similes.
            Returns:
                The score corresponding to the number of likely similes.
        """
        like_as_count = 0
        for sentence in self.text:
            if "as" in sentence or "like" in sentence:
                like_as_count += 1
        return like_as_count / len(self.text)
    
    def get_coherence(self):
        """ Returns the coherence score using the Reddit bigram as a reference.
        """
        reddit_scraper = ScrapeReddit()
        return reddit_scraper.text_coherence(" ".join(self.text))
    
    def count_alliterations(self):
        """ Counts the number of common first letters in subsequent words and
            divides the sum by the total number of words.
            Returns:
                Score corresponding to the amount of alliteration.
        """
        alliteration_count, n_words = 0, 0
        for line in self.text:
            words = line.split()
            lowercase_words = [word.lower() for word in words]

            # Counts alliterations
            for i in range(len(lowercase_words) - 1):
                if lowercase_words[i][0] == lowercase_words[i + 1][0]:
                    alliteration_count += 1
                n_words += 1

        return alliteration_count / n_words
    
    def count_assonance(self):
        """ Counts the number of subsequent words that share common vowels
            (assonance) and scales the score by the total number of words.
            Returns:
                Score corresponding to the amount of assonance in the poem.
        """
        vowels = set("aeiouAEIOU")
        assonance_count, n_words = 0, 0
        for line in self.text:
            words = line.split()
            for i in range(len(words) - 1):
                word1 = words[i]
                word2 = words[i + 1]

                # Extract vowels from each word
                vowels_word1 = [char for char in word1 if char in vowels]
                vowels_word2 = [char for char in word2 if char in vowels]

                # Check if the last vowel of the first word is the same as the 
                # first vowel of the second word
                if vowels_word1 and vowels_word2 and \
                        vowels_word1[-1].lower() == vowels_word2[0].lower():
                    assonance_count += 1
                n_words += 1
        return assonance_count / n_words

    def article_keyword_count(self):
        """ Returns what ratio of the total words in the poem are in the (or 
            are synonyms of words in the) reference article.
            Returns:
                Score corresponding to how much poem retained keywords from
                reference article.
        """
        pos_dics = self.ref_article.get_pos_dics()
        keyword_count, tot_count = 0, 0
        for line in self.text:
            for word in line.split():
                for dic in pos_dics.values():
                    if word in list(dic.keys()):
                        keyword_count += dic[word]
                tot_count += 1
        
        return keyword_count / tot_count
    
    def get_last_word(self, sentence):
        """ Helper function that skips through the punctuation and returns the
            last word in a sentence.
            Args:
                sentence (string) : the sentence to get the last word of
            Returns:
                The last word in the sentence.
        """
        sentence = sentence.split()
        sentence = [w for w in sentence if w not in string.punctuation]
        return sentence[-1]
    
    def rhyme_score(self):
        """ Computes a rhyme score for the poem by considering all of the
            desired line pairings. A pairing gets a score of 1 if the words
            rhyme and are different, half points if they are the same word,
            and no points if they do not rhyme. The score is divided by the
            number of possible rhymes.
            Returns:
                Score corresponding to the quality of rhymes
        """
        rhyme_score = 0
        for line1, line2 in self.rhyme_scheme:
            last1 = self.get_last_word(self.text[line1]).lower()
            last2 = self.get_last_word(self.text[line2]).lower()
            if last1 == last2:
                rhyme_score += 0.5
            elif last1 in " ".join(pronouncing.rhymes(last2)) \
                or last2 in " ".join(pronouncing.rhymes(last1)):
                rhyme_score += 1
        return rhyme_score / len(self.rhyme_scheme)
        
    def compute_fitness(self):
        """ Computes the fitness of the poem considering the sentiment
            alignment, grammar, simile presence, coherence, allitartion,
            assonance, article keyword alignment, and rhyme proficiency of the
            poem. Various coefficients are hardcoded to emphasize certain 
            qualities of the poem (can be changed based on the desired 
            qualities).
        """
        coefs = [1, .03, 1, 0.2, 1, 1, 0.2, 1]
        scores = [self.compute_sentiment_difference(), 
                  self.compute_grammar_score(), 
                  self.simile_detection(),
                  self.get_coherence(),
                  self.count_alliterations(),
                  self.count_assonance(),
                  self.article_keyword_count(),
                  self.rhyme_score()]

        self.fitness = sum([coefs[i] * scores[i] for i in range(len(coefs))])
    
    def set_text(self, text):
        """ Replaces the poem text with new text.
            Args:
                text (lis) : the new poem text
        """
        self.text = text
    
    def get_fitness(self):
        """ Calls to compute the fitness and returns the fitness value
        """
        self.compute_fitness()
        return self.fitness

    def __str__(self):
        """ Returns a string representation of the poem's fitness.
        """
        out_str = f"total fitness: {self.fitness}\n\n" +\
            f"sentiment difference: {self.compute_sentiment_difference()} " +\
                f"(score = {self.get_sentiment()})\n" +\
            f"grammar score: {self.compute_grammar_score() / 4}\n" +\
            f"simile score: {self.simile_detection()}\n" +\
            f"coherence score: {self.get_coherence()}\n" +\
            f"alliteration score: {self.count_alliterations()}\n" +\
            f"assonance score: {self.count_assonance()}\n" +\
            f"article keyword score: {self.article_keyword_count()}\n" +\
            f"rhyme score: {self.rhyme_score()}"
        return out_str