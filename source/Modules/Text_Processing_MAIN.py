#Text processing & cleaning
#imports
import sqlite3
import os
import string
import nltk
import json

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer



#-----------------------------------------------------------CONSTANTS-----------------------------------------------------------

#Database path
parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
configPath = os.path.join(parentDirectory, 'config.json')

# Get data from the config file
with open(configPath, 'r') as f:
    configData = json.load(f)

# Database path
DB_PATH = os.path.join(parentDirectory, configData["DB_PATH"])






#-----------------------------------------------------------Text cleaner-----------------------------------------------------------
class TextCleaner ():
    """
    Class for cleaning text data
    
    Attributes:
        completedIDs (list): List of IDs of articles that have been processed
        ProcessingArticles (list): List of articles that are being processed

    Methods:

    """
    def __init__(self):
        self.completedIDs = []
        self.ProcessingArticles = []

    #------------------------------------------------------Database operations------------------------------------------------------

    #get data from the database
    def getDataFromDatabase (self, minValue):
        """
        gets data from the database and stores it in ProcessingArticles

        Parameters:
            maxValue (int): The min ID value to get data from

        Returns:
            None
        """
        #connect to database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        #get all articles from database
        c.execute("SELECT * FROM NewsArticles WHERE id > ?", (minValue, ))
        #store all articles in a list
        self.ProcessingArticles = c.fetchall()
        #close connection
        conn.close()


    #print data in ProcessingArticles
    def printData (self):
        """
        prints all articles in ProcessingArticles

        Parameters:
            None
        
        Returns:
            None
        """
        for i in self.ProcessingArticles:
            print(i)
    

    #saves the processed data to the database
    def saveData (self, id, company, words):
        """
        saves the processed data to the database

        Parameters:
            id (int): The ID of the article
            words (list): The list of words in the article

        Returns:   
            None
        """
        #connect to db
        if self.checkIDNotInDB(id):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            #check if table exists, if not create it
            self.checkTablePAExists()
            #insert new row with ID and words
            #convert words list to json string
            wordsJson = json.dumps(words)
            c.execute("INSERT INTO ProcessedArticles VALUES (?, ?, ?)", (int(id), company, wordsJson))
            #commit changes
            conn.commit()
            #close connection
            conn.close()


    #checks if the ID is already in the database
    def checkIDNotInDB (self, id):
        """
        checks if the ID is already in the database

        Parameters:
            id (int): The ID to be checked

        Returns:
            True if ID is not in database, False otherwise
        """
        #connect to db
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        #check if table exists, if not create it
        self.checkTablePAExists()
        #get all IDs from database
        c.execute("SELECT id FROM ProcessedArticles")
        #store all IDs in a list
        ids = c.fetchall()
        #close connection
        conn.close()
        #check if id is in list
        for i in ids:
            if i[0] == id:
                return False
        return True
    

    #gets highest ID value stored in the database
    def getMaxId(self):
        """
        gets highest ID value stored in the database
        
        Parameters:
            None
        
        Returns:
            maxId (int): The highest ID value stored in the database
        """
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Execute SQL query to get maximum ID value
        c.execute("SELECT MAX(id) FROM ProcessedArticles")
        maxId = c.fetchone()[0]
        # Close connection and return result
        conn.close()
        if maxId == None:
            maxId = 0
        return int(maxId)
    

    #check if table ProcessedArticles exists
    def checkTablePAExists(self):
        """
        checks if table ProcessedArticles exists, if not creates it
        
        Parameters:
            None
        
        Returns:
            None
        """
        #connect to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        #check if table exists, if not create it
        c.execute('''CREATE TABLE IF NOT EXISTS ProcessedArticles (id INTEGER PRIMARY KEY, company TEXT, words TEXT)''')


    #------------------------------------------------------Text processing------------------------------------------------------
    
    #clean the data
    def cleanData (self, article):
        """
        cleans the data by removing punctuation and capital letters
        
        Parameters:
            article (string): The article to be cleaned
        
        Returns:
            longString (string): The cleaned article
        """
        #remove punctuation from string
        longString = article.translate(str.maketrans('', '', string.punctuation))
        #remove caps
        longString = longString.lower()
        #Return the list of tokens
        return(longString)
    
    
    #Tokenise the article
    def tokenise (self, article):
        """
        tokenises the article

        Parameters:
            article (string): The article to be tokenised
        
        Returns:
            tokens (list): The list of tokens
        """
        #split based on whitespace
        tokens = word_tokenize(article)
        return tokens


    #clean - remove stop words, numbers, noise
    def reduceData(self, articleList):
        """
        removes stop words, numbers and noise from the article
        
        Parameters:
            articleList (list): The article to be cleaned
            
        Returns:
            cleanWords (list): The list of cleaned words
        """
        stopWords = set(stopwords.words('english'))
        cleanWords = []
        for word in articleList:
            # Remove noise
            if not word.isalpha():
                continue
            # Remove stopwords
            if word.lower() in stopWords:
                continue
            # Remove numbers
            if word.isdigit():
                continue
            cleanWords.append(word.lower())
        return cleanWords


    #stemming/lemmatization
    def lemmatizeList(self, words):
        """
        lemmatizes the words in the article
        
        Parameters:
            words (list): The list of words to be lemmatized
            
        Returns:
            lemmatized (list): The list of lemmatized words
        """
        #create lemmatizer
        lemmatizer = WordNetLemmatizer()
        #new list of lemmatized words
        lemmatized = []
        #iterate through all the words and lemmatize them
        for word in words:
            lemmatizedWord = lemmatizer.lemmatize(word)
            lemmatized.append(lemmatizedWord)
        return lemmatized


    #does all steps of processing to an article
    def processWholeArticle(self, sentance):
        """
        processes the whole article by cleaning, tokenising, reducing and lemmatizing it

        Parameters:
            sentance (string): The article to be processed
        
        Returns:
            words (list): The list of words in the article
        """
        #clean data
        sentance = self.cleanData(sentance)
        #tokenise data
        sentance = self.tokenise(sentance)
        #reduce data
        sentance = self.reduceData(sentance)
        #lemmatize data
        words = self.lemmatizeList(sentance)
        return words
    

#------------------------------------------------------ProcessArticle--------------------------------------------

#text process body of article
def processArticle (TC):
    """
    processes the article by cleaning, tokenising, reducing and lemmatizing it

    Parameters:
        TC (TextCleaner): The TextCleaner object to be used

    Returns:
        None
    """
    #get max id
    maxId = TC.getMaxId()
    if TC.getMaxId() == None:
        maxId = 0
    else:
        maxId = int(maxId)

    #get data from database
    TC.getDataFromDatabase(maxId)
    #TC.printData()

    for i in TC.ProcessingArticles:
        if i[0] > maxId:
            #clean data
            currentArticle = TC.cleanData(i[8])
            #tokenise data
            currentArticle = TC.tokenise(currentArticle)
            #reduce data
            currentArticle = TC.reduceData(currentArticle)
            #lemmatize data
            currentArticle = TC.lemmatizeList(currentArticle)
            #save data
            TC.saveData(i[0], i[2], currentArticle)
        #TC.ProcessingArticles.remove(i)
    TC.ProcessingArticles = []


