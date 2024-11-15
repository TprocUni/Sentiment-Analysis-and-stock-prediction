#Sentiment analysis

#-----------------------------------------------------imports-------------------------------------------------------
import sqlite3
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer as SIA1
import ast
import json

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA2
nltk.download('vader_lexicon')
from textblob import TextBlob

#----------------------------------------------------Constants------------------------------------------------------

parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
configPath = os.path.join(parentDirectory, 'config.json')

# Get data from the config file
with open(configPath, 'r') as f:
    configData = json.load(f)

# Database path
DB_PATH = os.path.join(parentDirectory, configData["DB_PATH"])





#----------------------------------------------------Classes------------------------------------------------------
class Article ():

    def __init__ (self, id, company, words):
        self.id = id
        self.company = company
        self.words = words


class SentimentEngine ():
    def __init__ (self):
        self.processingArticles = []
        self.readyArticles = []


#------------------------------------------------Database operations------------------------------------------------

    def getWordList(self):
        '''
        gets all articles from database table processedArticles and stores them in a list

        Parameters:
            None

        Returns:
            None
        '''
        #connect to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        #get all articles from database
        c.execute("SELECT * FROM ProcessedArticles")
        #store all articles in a list
        self.processingArticles = c.fetchall()
        for i in self.processingArticles:
            # Check if the article with the same ID is already in the readyArticles list
            if not any(article.id == i[0] for article in self.readyArticles):
                #set up each article as an article object
                art = Article(i[0], i[1], ast.literal_eval(i[2]))
                #put the objects in the ready list
                self.readyArticles.append(art)
        #close connection
        conn.close()


    #gets all articles from database table NewsArticles and stores them in a list
    def getWordListUnprocessed(self):
        '''
        gets all articles from database table NewsArticles and stores them in a list

        Parameters:
            None

        Returns:
            None
        '''
        #connect to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        #get all articles from database
        c.execute("SELECT * FROM NewsArticles")
        #store all articles in a list
        self.processingArticles = c.fetchall()
        for i in self.processingArticles:
            # Check if the article with the same ID is already in the readyArticles list
            if not any(article.id == i[0] for article in self.readyArticles):
                #set up each article as an article object
                art = Article(i[0], i[1], i[2].split())
                #put the objects in the ready list
                self.readyArticles.append(art)
        #close connection
        conn.close()


#------------------------------------------------Sentiment Analysis------------------------------------------------

    #VADER
    #parameters for Vader:
    #                                  "good": 2.0, "bad": -2.0},
    #                                  punctuation=False,
    #                                  n_gram_range=(1, 2),
    #                                 stopwords=["and", "the"],
    #                                  normalize=False

    #                                       more exist



    #Uses vader sentiment analysis to get the sentiment of a word - individual word basis
    def sentimentAnalysisVader1 (self, words):
        '''
        Sentiment analysis method one - VADER - vader library VADER

        Parameters:
            words (list): list of words to be analysed
        
        Returns:
            avgDict (dict): dictionary of sentiment scores
        '''
        #make sentiment analyzer
        analyzer = SIA1()
        sentimentScores = []
        #analyse each word independantly and deduce sentiment
        for word in words:
            text = " ".join([word])
            scores = analyzer.polarity_scores(text)
            sentimentScores.append(scores)
        #-------------------------------------------------------------------------------------------is shit
        #make sentiment score averages for each column
        #find average of sentiment scores
        avgDict = {}
        n = len(sentimentScores)
        for d in sentimentScores:
            for k, v in d.items():
                if k not in avgDict:
                    avgDict[k] = 0.0
                avgDict[k] += v / n
        
        return avgDict
    

    #same as above with concatenated string
    #INPUT   - List of words
    #OUTPUT  - Dict of sentiment scores
    def sentimentAnalysisVader2 (self, words):
        '''
        Sentiment analysis method two - VADER - vader library VADER

        Parameters:
            words (list): list of words to be analysed
        
        Returns:
            avgDict (dict): dictionary of sentiment scores
        '''
        #make sentiment analyzer
        analyzer = SIA1()
        #create sentance
        sentance = ""
        #create ge full sentance
        for i in range(len(words)):
            sentance += words[i] + " " 
        #get sentiment score
        score = analyzer.polarity_scores(sentance)
        return score
    

    #sentiment analysis using NLTK vader library
    #INPUT  -   list of words
    #OUTPUT -   dictionary of sentiment scores
    def sentimentAnalysisNLTK (self, words):
        '''
        Sentiment analysis method two - VADER - NLTK library VADER

        Parameters:
            words (list): list of words to be analysed
        
        Returns:
            avgDict (dict): dictionary of sentiment scores
        '''
        # Initialize the sentiment analyzer
        sid = SIA2()
        # Join the list of words into a single string
        text = ' '.join(words)
        # Get the sentiment score for the text
        scores = sid.polarity_scores(text)
        # Return the compound sentiment score
        return scores
    

    #sentiment analysis using TextBlob library
    #INPUT  -   list of words
    #OUTPUT -   tuple of polarity & subjectivity
    def sentimentAnalysisTextBlob (self, words):
        '''
        Sentiment analysis method two - VADER - TextBlob VADER

        Parameters:
            words (list): list of words to be analysed
        
        Returns:
            avgDict (dict): dictionary of sentiment scores
        '''
        # Join the list of words into a single string
        text = ' '.join(words)
        # Get the sentiment score for the text
        sentiment = TextBlob(text).sentiment
        # Return the sentiment score
        return sentiment




