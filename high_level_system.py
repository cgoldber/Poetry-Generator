from poem import Sonnet
from news_article import Article
import numpy as np
import random
import os
from datetime import datetime
from word2vec import MyWord2Vec
from scrape_reddit import ScrapeReddit


""" Contains the traditional Sonnet rhyme scheme, where each element of the
    list contains the indices of line numbers of the poem that should rhyme.
"""
SONNET_RHYME_SCHEME = [[0, 2], [1, 3], [4, 6], [5, 7], [8, 10], [9, 11], 
                       [12, 13]]


class GeneratorSystem():
    """ High-level class that calls to generate the intiial set of poems, 
        runs a genetic algorithm, and writes the best result.

    Attributes
    ----------
    n_poems : int
        The number of poems stores at each generation.
    ref_article : Article
        The article the poems will be based on.
    poems : list
        List of the current poems in the algorithm.

    Methods
    -------
    populate_models():
        Trains large bigram and Word2Vec Model
    write_poems_to_files():
        Writes the final poem, metrics, and reference article information to
        time-stamped files.
    fetch_reference_article():
        Calls to retrieve a reference article from NewsAPI.
    generate_poem():
        Calls to generate a new poem.
    generate_original_poems():
        Calls to generate a chosen number of poems.
    fittest_half():
        Returns fittest 50% of a population.
    crossover():
        Crosses over two poems into one.
    genetic_algo():
        Runs a round of the genetic algorithm.
    run_genetetic_algo_iterations():
        Runs a chosen amount of iterations of the genetic algorithm    
    """

    def __init__(self, n_poems):
        self.n_poems = n_poems
        self.ref_article = None
        self.poems = []
        #self.populate_models() #UNCOMMENT TO TRAIN LARGER MODELS
    
    def populate_models(self):
        """ Creates a new word2vec and bigram model (takes a very long time
            to run so only do it once, the models will save to nlp_models
            folder).
        """
        my_word2vec = MyWord2Vec() 
        my_word2vec.make_poetry_base()

        scrape_reddit = ScrapeReddit()
        scrape_reddit.reset_model()

    def write_poems_to_files(self):
        """ Creates a folder for all of the files related to this running of
            the poetry system named by the timestamp. In the folder, writes
            the generated poem, the metrics for the poem, the reference article
            tile, the reference article description, and the reference article
            content.
        """
        curr_path = "generated_poems/" + \
                                datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        os.makedirs(curr_path)
        print("Writing top poem to file")
        with open(curr_path + "/reference_article.txt", "w") as f:
                f.write("\nReference Article: \n")
                f.write(self.ref_article.get_title() + "\n")
                f.write(self.ref_article.get_text() + "\n")
                f.write(f"\nSentiment: {round(
                            self.ref_article.get_sentiment_score(), 2)}\n\n")
        with open(curr_path + "/reference_article_title.txt", "w") as f:
                f.write(self.ref_article.get_title())
        with open(curr_path + "/reference_article_description.txt", "w") as f:
                f.write(self.ref_article.get_description())
        
        self.poems = sorted(self.poems, key = lambda x : x.get_fitness(), 
                                                                reverse=True)
        poem = self.poems[0]
        with open(curr_path + f"/rank_1.txt", "w") as f:
            f.write(poem.generate_title() + "\n")
            f.write("\n")
            f.write(str(poem))
        with open(curr_path + f"/rank_1_metrics.txt", "w") as f:
            f.write(str(poem.fitness))
    
    def fetch_reference_article(self):
        """ Calls to NewsAPI to get a reference article to write a poem based
            on.
        """
        self.ref_article = Article()
        print("Writing poems based on the following article:")
        print(self.ref_article.get_title())
                
    def generate_poem(self):
        """ Generated a Sonnet object and adds it to the system's list of 
            poems.
        """
        sonnet = Sonnet(SONNET_RHYME_SCHEME, self.ref_article, [])
        sonnet.generate_sonnet()
        self.poems.append(sonnet)
    
    def generate_original_poems(self):
        """ Calls to generate n amount of first generation poems.
        """
        print("Generating First Set of Poems")
        for i in range(self.n_poems): 
            print(f"Generating poem {i+1} out of {self.n_poems}")
            self.generate_poem()
    
    def fittest_half(self, poems):
        """ Returns the fittest 50% of a given population.
            Args:
                poems (list) : list of poems
            Returns:
                a list of the fittest poems
        """
        sorted_poems = sorted(poems, key = lambda x : x.get_fitness())
        return sorted_poems[int(len(poems)/2):]
    
    def crossover(self, poem_opts):
        """ Crosses over two poems while maintaining the rhyming scheme. For
            each line pair in the rhyming scheme, takes both lines from a
            randomly selected poem to maintain scheme. 
            Args:
                poem_opts (list) : contains the two poems to be crossed
            Returns:
                The newly crossed poem.
        """
        new_poem = [""] * 14
        for line1, line2 in SONNET_RHYME_SCHEME:
            rand_poem = np.random.choice(poem_opts)
            new_poem[line1] = rand_poem.get_line(line1)  
            new_poem[line2] = rand_poem.get_line(line2)
        return Sonnet(SONNET_RHYME_SCHEME, self.ref_article, new_poem)
    
    def genetic_algo(self):
        """ Iterates for the number of poems in the set. For each iteration,
            the algorithm randomly selects two poems based on their fitnesses
            to crossover. Then, there is a 70% chance the poem will get
            mutated. After that, the top fittest 50% of the old generation
            and new generation move on to the next round of the algorithm.
        """
        new_poems = []
        for _ in range(self.n_poems):
            fitnesses = [poem.get_fitness() for poem in self.poems]
            sum_fit = sum(fitnesses)
            p = [fit / sum_fit for fit in fitnesses]
            poem_opts = np.random.choice(self.poems, p = p, size = 2, 
                                                            replace = False)
            new_poem = self.crossover(poem_opts)
            if random.random() > 0.3:
                new_poem.mutate()
            new_poems.append(new_poem)

        self.poems = self.fittest_half(self.poems) + \
                     self.fittest_half(new_poems)
    
    def run_genetic_algo_iterations(self, n_iterations):
        """ Runs the generatic algorithm for n_iterations amount of times.
            Args:
                n_iterations (int) : the number of times to run the algorithm
        """
        print("Running Genetic Algorithm")
        for i in range(n_iterations): #Can change num iterations
            print(f"Running iteration {i+1} of {n_iterations}")
            self.genetic_algo()


def main():
    generator = GeneratorSystem(n_poems=5)
    generator.fetch_reference_article()
    generator.generate_original_poems()
    generator.run_genetic_algo_iterations(n_iterations=5)
    generator.write_poems_to_files()
    print("All done :)")


if __name__ == "__main__":
    main()
