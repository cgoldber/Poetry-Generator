import requests
import numpy as np

""" Poets in PoetryDB to be excluded because they write in Old English and 
    this poetry system aims to write modern poetry.
"""
POETS_B4_1700 = [
    "Anne Kingsmill Finch",
    "Ben Jonson",
    "Christopher Marlowe",
    "Coventry Patmore",
    "Edward Taylor",
    "Edgar Allan Poe",
    "George Gordon, Lord Byron",
    "Henry David Thoreau",
    "John Donne",
    "John Dryden",
    "John Milton",
    "Jonathan Swift",
    "Joyce Kilmer",
    "Katherine Philips",
    "Lady Mary Chudleigh",
    "Matthew Prior",
    "Michael Drayton",
    "Oliver Goldsmith",
    "Percy Bysshe Shelley",
    "Richard Crashaw",
    "Robert Herrick",
    "Robert Southey",
    "Sir John Suckling",
    "Sir Philip Sidney",
    "Sir Thomas Wyatt",
    "Sir Walter Raleigh",
    "Mary Darby Robinson",
    "Thomas Campion",
    "William Blake",
    "William Browne",
    "William Lisle Bowles",
    "William Shakespeare",
    "Thomas Warton",
    "William Wordsworth",
]

class PoetryDB():
    """ Class for retrieving poems from PoetryDB.
        
    Attributes
    ----------
    all_poems : list
        All wanted authors' poems in PoetryDB.
    sonnets : list
        All wanted author's poems in PoetryDB that have 14 lines.

    Methods
    -------
    retrieve_sonnets():
        Gets all poems that have 14 lines and meet author condition.
    retrieve_all_poem_types():
        Gets all poems that meet author condition.
    get_poetry_line():
        Returns line of a random poem given a specific index.
    get_all_poems():
        Returns all poems in PoetryDB that meet author condition.
    """

    def __init__(self):
        """ Calls to populate the Sonnet list with poems from PoetryDB that 
            have 14 lines.
        """
        self.all_poems = []
        self.sonnets = []
        self.retrieve_sonnets()
    
    def retrieve_sonnets(self):
        """ Retrieve poems from PoetryDB that have fourteen lines and are not
            in the list of excluded poets.
        """
        url = "https://poetrydb.org/linecount/14"
        response = requests.get(url)
        if response.status_code == 200:
            poems = response.json()
            for poem in poems:
                if len(poem['lines']) == 14 and \
                                        poem['author'] not in POETS_B4_1700:
                    self.sonnets.append(poem)
    
    def retrieve_all_poem_types(self):
        """ Retrieve all poems from the PoetryDB that are not in the list of
            excluded poets to be included in Word2Vec corpus.
        """
        url = "https://poetrydb.org/lines/all"
        response = requests.get(url)
        if response.status_code == 200:
            poems = response.json()
            for poem in poems:
                if poem['author'] not in POETS_B4_1700:
                    self.all_poems.append("\n".join(poem['lines']))
    
    def get_poetry_line(self, ix):
        """ Chooses a random poem that contains 14 lines and returns the line
            at the given index.
            Args:
                ix (int) : the index of the line to be returned
            Returns:
                The line of a random poem at the given index.
        """
        rand_poem = np.random.choice(self.sonnets)
        return rand_poem['lines'][ix]
    
    def get_all_poems(self):
        """ Returns all wanted authors' poems.
        """
        return self.all_poems
