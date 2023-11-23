from get_inspiring_poems import PoetryDB
from fitness import Fitness
from mutations import Mutator
import string

class Sonnet():
    """ A class representing a Sonnet.
        
    Attributes
    ----------
    rhyme_scheme : list
        Indicates the desired lines of the poem that should rhyme.
    ref_article : Article
        The news article the poem is based on.
    sonnet : list
        A list of lines in the poem.
    fitness : Fitness
        A class representing the Fitness of the poem.
    mutator : Mutator
        A class that contains tool for mutating the poem.

    Methods
    -------
    fill_w_rand_inspiring_set_lines():
        Generates first generation poem with random lines from PoetryDB.
    generate_sonnet():
        Makes first generation poem, swaps keywords, and imposes rhyme scheme.
    mutate():
        Calls Mutator object to mutate poem.
    get_fitness():
        Returns fitness of poem.
    get_line():
        Returns a line of the poem at a given index.
    most_important_word():
        Retrieves most important word from article using previously generated
        part of speech dictionaries.
    generate_title():
        Returns the title of the poem using the most important word.
    correct_capitalizations():
        Ensures the begininng of lines and "I"s are capitalized.
    format_line():
        Ensures the desireable spacing conventions for punctuation.
    """

    def __init__(self, rhyme_scheme, ref_article, text=[]):
        """ Initializes a poem, along with it's evaluation and mutation tools.
        """
        self.rhyme_scheme = rhyme_scheme
        self.ref_article = ref_article
        self.sonnet = text
        self.fitness = Fitness(text, ref_article, rhyme_scheme)
        self.mutator = Mutator(text, ref_article, rhyme_scheme)
    
    def fill_w_rand_inspiring_set_lines(self):
        """ Generates a poem where each of the 14 lines contain random lines
            from the poetry dataset. 
        """
        inspiring_set = PoetryDB()
        for i in range(14):
            line = inspiring_set.get_poetry_line(i)
            self.sonnet.append(line)

    def generate_sonnet(self):
        """ Generates a first generation Sonnet by populating random lines
            from the poetry database, swapping key words in the poem with
            semantically similar words from the reference article, and 
            imposing the proper rhyme scheme.
        """
        self.fill_w_rand_inspiring_set_lines()
        self.mutator.replace_keywords()
        self.sonnet = self.mutator.get_sonnet()

    def mutate(self):
        """ Calls to mutate the poem. Then, saves the new poetry text.
        """
        self.mutator.mutate()
        self.sonnet = self.mutator.get_sonnet()

    def get_fitness(self):
        """ Ensures that the fitness class is considering the proper version
            of the poem and returns the fitness value.
            Returns:
                The poem's fitness value
        """
        self.fitness.set_text(self.sonnet)
        return self.fitness.get_fitness()

    def get_line(self, ix):
        """ Returns a line of the poem corresponding to the given index.
            Args:
                ix (int) : the index of the desired line
            Returns:
                The line at the index
        """
        return self.sonnet[ix]
    
    def most_important_word(self):
        """ Returns the word in the reference article that was computed to 
            have the highest importance score across all parts of speech.
            Returns:
                The most important word.
        """
        curr_max_val, curr_max_word = 0, None
        pos_dics = self.ref_article.get_pos_dics()
        for dic in pos_dics.values():
            for word, val in dic.items():
                if val > curr_max_val:
                    curr_max_val = val
                    curr_max_word = word
        return curr_max_word
    
    def generate_title(self):
        """ Generates a poem title using the article's most important word.
            Returns:
                The poem's title
        """
        freq_word = self.most_important_word()
        return f"An Ode to {freq_word.capitalize()}"
    
    def correct_capitalizations(self, line):
        """ Ensures the first word in a line and all "I" characters are 
            capitalized.
            Args:
                line (string) : the line to be edited
            Returns:
                The line with proper capitalization
        """
        line = line.split()
        new_line = []
        for i in range(len(line)):
            if i == 0 or line[i] == "i":
                new_line.append(line[i].capitalize())
            else:
                new_line.append(line[i])
        return " ".join(new_line)

    def remove_duplicate_punc(self, line):
        """ Removes duplicate punctuation that might appear in a line.
            Args:
                line (string) : the line to be filtered
            Returns:
                The line without duplicate punctuation
        """
        line = line.split()
        new_line = [line[0]]
        for i in range(1, len(line)):
            if line[i] not in string.punctuation or line[i] != line[i - 1]:
                new_line.append(line[i])
        return " ".join(new_line)

    def format_line(self, words):
        """ Formats the poem to be written neatly to a file. This includes 
            stripping any beginning spaces, ensuring there's not extra spaces
            between punctuation, making sure that "I" and the first letter
            of every line are capitalized, and removing any duplicate
            punctuation.
            Args:
                words (string) : the words to format
            Returns:
                the formatted words
        """
        # Remove beginning spaces
        words = words.lstrip()
        # Make sure no spaces before punctuation
        end_punc_chars = set(['.', '!', '?', ',', ';', ':', "'", ')', ']', '}'])
        beg_punc_chars = set(['(', '{', '['])
        formatted_chars = []

        for pter in range(len(words)):
            if words[pter] == " " and pter < len(words) - 1 and words[pter + 1] in end_punc_chars:
                continue
            elif words[pter] in beg_punc_chars and pter < len(words) - 1 and words[pter + 1] == " ":
                formatted_chars.append(words[pter])
            else:
                formatted_chars.append(words[pter])
        # Ensure correct capitalization and remove duplicate punctuation
        formatted = self.correct_capitalizations("".join(formatted_chars))
        formatted = self.remove_duplicate_punc(formatted)
        return formatted

    
    def __str__(self):
        """ Returns a string representation of the poem.
        """
        ret_str = ""
        for line in self.sonnet:
            ret_str += self.format_line(line) + "\n"
        return ret_str
