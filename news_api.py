import requests
import bs4
from bs4 import BeautifulSoup
import re
import numpy as np

""" Minimum article length to be permitted."""
MIN_ARTICLE_LENGTH = 500

""" Potential news categories user can choose from."""
CATEGORIES = ['business', 'entertainment', 'general', 'health', 'science', 
              'sports', 'technology']


class NewsGetter():
    """ Extracts news article from newsapi based on a user-selected category.
        
    Attributes
    ----------
    article : dictionary
        Contains title, description, and content of a news article.
    category : String
        The user-selected news category.

    Methods
    -------
    get_user_input_category():
        Prompts user to select a news category.
    filter_unwanted_elements():
        Filters unwanted HTML elements, text patterns, and characters from soup
    call_api():
        Calls NewsAPI to get news articles.
    scrape_article_website():
        Selects a random article and scrapes it using BeautifulSoup and
        filtering tools
    fetch_article():
        Gets all articles of a given category from the NewsAPI and gets a 
        singular article that meets length requirements.
    get_category():
        Returns the user-selected news category.
    get_article():
        Returns the retrieved article information.
    """
    def __init__(self):
        """ Prompts user to select an article category and fetches the 
            corresponding article.
        """
        self.article = {}
        self.category = ""
        self.get_user_input_category()
        self.fetch_article()

    def get_user_input_category(self):
        """ Prompts user to select a category of news.
        """
        print("Which category of news article would you like to " + 
              "generate a poem based on?")
        print("Options are:")
        for i, category in enumerate(CATEGORIES):
            print(f"({i}) {category}")
        choice = input("Choice: ")
        self.category = CATEGORIES[int(choice)]

    def filter_unwanted_elements(self, soup):
        """ Filters unwanted HTML elements, text patterns, and characters from
            the text scraped from a website.
            Args:
                soup (BeautifulSoup) : result of website scraping
        """
        #Excludes certain HTML elements
        elements_to_exclude = [
            ('div', {'class': ['subscription', 'ads', 'related-articles', 
                               'sidebar']}),
            ('a', {'class': 'navigation-link'}),
            ('ul', {'class': 'social-media-links'}),
            ('div', {'id': re.compile(r'comment', re.IGNORECASE)}),
        ]
        for tag_name, attrs in elements_to_exclude:
            for tag in soup.find_all(tag_name, attrs=attrs):
                tag.decompose()

        # Excludes unwanted text patterns related to the website itself
        unwanted_patterns = [
            re.compile(r'copyright', re.IGNORECASE),
            re.compile(r'\bAll rights reserved\b', re.IGNORECASE),
            re.compile(r'cookie', re.IGNORECASE),
            re.compile(r'consent', re.IGNORECASE),
            re.compile(r'privacy policy', re.IGNORECASE),
            re.compile(r'All Rights Reserved', re.IGNORECASE),
            re.compile(r'Follow Us', re.IGNORECASE),
            re.compile(r'nt', re.IGNORECASE)
        ]
        for pattern in unwanted_patterns:
            for element in soup.find_all(text=pattern):
                if isinstance(element, bs4.element.Tag):
                    element.parent.decompose() 

        # Excludes special characters + non-ASCII characters
        special_character_pattern = r'[^\x00-\x7F]+'
        for text_element in soup.find_all(text=True):
            cleaned_text = re.sub(special_character_pattern, '', text_element)
            text_element.replace_with(cleaned_text)
        
        return soup

    def call_api(self):
        """ Makes a call to extract news articles from newsapi using predefined
            details.
            Returns:
                The response of the api request.
        """
        api_key = 'ac734d722e664da4844ebb710f33709c'
        base_url = 'https://newsapi.org/v2/top-headlines'
        parameters = {
            'country': 'us',
            'category': self.category,
            'apiKey': api_key,
        }
        response = requests.get(base_url, params=parameters)
        return response

    def scrape_article_website(self, articles):
        """ Chooses a random article from a list of articles and calls for
            BeautifulSoup to scrape it. Then, it performs filtering to remove
            unwanted element of texts, and saves information about the article
            if it is of sufficient length. Repeats until an article is
            successfully scraped (sometimes issues with request).
            Args:
                articles (list) : list of articles to chose from.
        """
        while True:
            article = np.random.choice(articles)

            article_response = requests.get(article['url'])
            if article_response.status_code == 200:
                soup = BeautifulSoup(article_response.text, 'html.parser')
                
                # Filter out unwanted elements of website scrape
                article_text = ""
                modified_text = self.filter_unwanted_elements(soup)
                for element in modified_text.find_all(['p', 'h1', 'h2', 'h3']):
                    article_text += element.get_text() + "\n"

                # Save article if it is of sufficient length
                if len(article_text) >= MIN_ARTICLE_LENGTH:
                    self.article = {"title" : article['title'], 
                                    "text" : article_text,
                                    "description" : article['title']}
                    return

    def fetch_article(self):
        """ Make a request to newsapi to retrieve news articles corresponding
            to a user-chosen category. Then, calls for the article to be
            scraped for relevant text. Repeats until an article is successfully
            extracted (sometimes issues with request).
        """
        while True:
            response = self.call_api()
            if response.status_code == 200:
                news_data = response.json()
                if 'articles' in news_data and len(news_data['articles']) > 0:
                    articles = news_data['articles']
                    self.scrape_article_website(articles)
                    return
    
    def get_category(self):
        """ Returns user-chosen news category.
        """
        return self.category
    
    def get_article(self):
        """ Returns article that was chosen.
        """
        return self.article
    