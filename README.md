# Title: The Odient

## Description 
In a world where we often become desensitized to the constant onslaught of news, the Odient challenges
users to reflect deeper on the news they read through the lense of poetry. Users can choose a news category, and the system randomly selects a recent article and generates a Sonnet that is inspired by it. 

The system begins constructing poems by extracting random lines from various poems in a dataset. Nouns, adjectives, and verbs are then replaced with words from the chosen news article, weighted by their frequency and lack of prevalence in other texts. A rhyming scheme is also imposed to ensure the poem adheres to the structure of a Sonnet.

Then, the poems are processed by a genetic algorithm, where they are crossed over and potentially mutated. This includes swapping semantically similar words, utilizing bigrams extracted from Reddit posts to replace parts of lines, and employing a language correction tool on selected lines. The fittest poems from both the old and new generations are retained for the next iteration.

Evaluation criteria include article alignment (sentiment analysis, preservation of keywords), quality of content (grammar checks, coherence with bigrams, simile inclusion), and sound (alliteration, assonance, and rhyme).

Users can access a local website where a few news headlines are displayed. The users can press on a headline of
interest and the poem will be displayed and read aloud, along with the description of the inspiring news article.

## Running the Code
### Installations
Users must install requests, bs4 for Beuatiful Soup, TextBlob, spacy (specificlly must install the en_core_web_sm data), pronouncing, gensim, and language-tool-python

### Instructions
To generate their own poem, users must be in the Poetry Generator Folder and run high_level_system.py. They will
be instructed to select a category of news. After that, they only have to sit and wait for their poetry to be 
generated! They can find their poems in the generated_poems folder in the folder corresponding to the timestamp
of when the code stopped running. In that subfolder, they will find the generated poem, the corresponding poem
metrics, and the reference article.

To access the poetry display, users can run a local Python server by typing python -m http.server in the terminal.
Then, they can head to http://localhost:8000/speech.html on their browser of choice to access the display. To hear
a poem, they only have to click on the news article headline. To stop the poem reading, they can click the red stop
button. To change the poems avalable on the website, users can manually go into the speech.js code and input the 
timestamps corresponding to the poem they want to display.

## Personal Challenges
The most challenging aspect of this project was learning how to work with all of the libraries, APIs, and databases that I had never worked with before. A good amount of my time was spent sifting through documentation, trying to figure out exacyly what libraries and functions would be the most useful for my purposes. I think it was a very useful experience though, as I could definitely see myself using a lot of these tools and packages in the future!

Another big challenge for me was designing the local website. Though it is not the most complex website, I have never worked with JavaScript and HTML before, so it was really challenging for me to even figure out how to debug it when things went wrong. Though I definitely still have a lot to learn, it was very valuable to learn a bit about how front-end coding works.

## Academic Inspirations
1. "Evolutionary Elaboration of Daily News as a Poetic Stanza" by Pablo Gervás

This article explores the realm of poetry generation with an emphasis on sustained innovation by integrating current news events. In the same way that humans learn from our past experiences and stories we have heard, they wanted to simulate that computationally. Inspired by this approach, my system also incorporates news articles to ensure its topicality. The NewsAPI extracts articles that usually came out within a week, emphasizing the ever-changing nature of current events and the art that reflect it. Although my system does not gain extensive generally-applicable knowledge from extracting new articles, the incorporation of relevant keywords allows it to embody the essence of an ever-growing and updating creative system. 

3. "Less Rhyme, More Reason: Knowledge-based Poetry Generation with Feeling, Insight and Wit" by Tony Veale

This article emphasizes how important it is for systems to have an underlying understanding of the content of text corpuses, or at least generate in ways that make humans think they do. In designing my system, I also wanted to convey an overall message that audiences could resonate with. For one thing, I incorporated words from the article to try to capture the same meaning as the original article. I then went further and employed sentiment analysis to align the poems more authentically with the nuanced emotional tones and messages encapsulated in the chosen news articles. This is important, as as discussed in the article, it is important to go beyond the sterotype. Instead of simply repeating words that might incite a reaction, it is more meaningful to capture more nuanced emotion messages. The article also discusses using n-grams to gain deeper understandings of a text corpus. I did something similar, integrating bigrams into my approach to mitigate potential coherence challenges arising from the incorporation of news article words. By scraping Reddit pages, I aimed to elevate the emotional resonance of my system's poetry by accessing language that most people engage with on a daily basis.

4. "Emotion Detection and Sentiment Analysis in Text Corpus: A Differential Study with Informal and Formal Writing Styles" by Jasleen Kaur and Jatinderkumar R. Saini 

The article investigates formal and informal writing styles in the context of sentiment analysis and emotion detection. They discuss in detail the rich emotional nuances that could be found in both of these types of texts. I took inspiration from this article by also trying to incorporate formal and informal writing for my text corpus. Originally, my poems were generated by extracting lines and words from poems and news articles, which
(depending on the news article nowawadays) are generally formal writing styles. These sort of sources provided an excellent framework for generating linguistically complex and interesting systems. Beyond that, I also scraped Reddit posts for a lot of my text data. Posts on the internet are much more casual, and perhaps better depict the way typical humans interact with each other. By including bigrams to capture more common phrases that are used in daily life, I was hoping that it would help make my poems more accessible and understandale. I also think that formal writing and informal writing illicit emotions in different ways -- formal writing can be beautiful but informal writing feels rawer at times.



