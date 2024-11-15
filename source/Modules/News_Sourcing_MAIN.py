#imports
import requests    
import bs4
import sqlite3
import os
from urllib.parse import quote
import json
import string

#---------------------------------------------------------Constants---------------------------------------------------------

parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
configPath = os.path.join(parentDirectory, 'config.json')

# Get data from the config file
with open(configPath, 'r') as f:
    configData = json.load(f)

# Database path
DB_PATH = os.path.join(parentDirectory, configData["DB_PATH"])


# your own API key
API_KEY = configData["API_KEY"]


#---------------------------------------------------------news sourcing class---------------------------------------------------------
class NewsAPISourcer:
    '''
    class to peform news sourcing
    '''
    #------------------------------------------------------Getting articles------------------------------------------------------
    #data structure to store data
    def __init__(self):
        self.newArticles = []
        self.readyArticles = []


    #gets the articles from the API
    def getURLs (self, names):
        """
        gets the articles from the API

        Parameters:
            query (string): the query to search for

        Returns:
            None
        """

        #add function to determine which name article is based off
        for query in names:
            #end point
            url = 'https://newsapi.org/v2/everything?'
            # Specify the query and number of returns
            parameters = {
            'q': query, # query phrase
            'pageSize': 20,  # maximum is 100
            'apiKey': API_KEY 
            }
            # Make the request            
            response = requests.get(url, params=parameters)
            response_json = response.json()

            #figure out which name article is based off of here

            #call storeNewArticles to store new articles
            self.storeNewArticles(response_json, query)


    #extracts the text from a url
    def getTextFromURL (self, url):
        """
        extracts the text from a url

        Parameters:
            url (string): the url to extract text from
        
        Returns:
            body (string): the text from the url
        """
        #get data from provided url
        response = requests.get(url)
        #set up beautifulsoup
        theSoup = bs4.BeautifulSoup(response.content, 'html.parser')
        body = theSoup.body
        return body


    #helper functiont to print body
    def printBody (body):
        for string in body.strings:
            print(string)


    #helper function to print one ready article
    def printReadyArticle (self, index):
        print(self.readyArticles[index])


    #store new articles within object
    def storeNewArticles (self, newAs, comp):
        """
        store new articles within the object

        Parameters:
            newAs (dict): the dictionary of new articles

        Returns:
            None
        """
        #go through each article and store
        for i in range (len(newAs["articles"])):
            finishedArticle = self.getArticleBody(newAs["articles"][i])
            if finishedArticle["body"] != "":
                finishedArticle["company"] = comp
                self.readyArticles.append(finishedArticle)


    #helper function to print new articles
    def printNewArticles (self):
        #go through each line and print
        for i in range (len(self.newArticles)):
            print(self.newArticles[i])


    #helper function to print ready articles
    def printReadyArticles (self):
        #go through each line and print
        for i in range (len(self.readyArticles)):
            print(self.readyArticles[i])
    

    #retrieves the body of an article adds it to the end of the dict
    def getArticleBody (self, currentArticle):
        """
        retrieves the body of an article adds it to the end of the dict

        Parameters:
            currentArticle (dict): the article to get the body of

        Returns:
            currentArticle (dict): the article with the body
        """
        #get articles body
        currentBody = self.getTextFromURL(currentArticle["url"])
        #get rid of all the html tags
        if currentBody == None:
            currentArticle["body"] = ""
            return currentArticle
        realBody = ""
        for string in currentBody.strings:
            realBody += string
            realBody += " "

        currentArticle["body"] = realBody
        #return articel dict with body
        return currentArticle


    #iterates through the list of new articles and gets the body of each
    def getArticleBodies (self):
        """
        iterates through the list of new articles and gets the body of each

        Parameters:
            None
        
        Returns:
            None
        """
        for i in self.newArticles:
            #temp store i
            temp = i
            #remove from original list
            self.newArticles.remove(i)
            #acquire body and add to ready articles
            tempBody = self.getArticleBody(temp)
            self.readyArticles.append(tempBody)


    #-------------------------------------------Database operations-------------------------------------------

    #checks if database exists
    def connectToDatabase(self):
        """
        checks if database exists

        Parameters:
            None
        
        Returns:
            None
        """
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print("Database exists with tables: ", tables)
        else:
            print("2")
            print("Database does not exist. Creating new database...")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS NewsArticles (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              title TEXT NOT NULL,
                              company TEXT
                              author TEXT,
                              sourceID TEXT,
                              sourceName TEXT,
                              publishedAt DATETIME NOT NULL,
                              url TEXT NOT NULL,
                              body TEXT
                              );''')
            print("New table created in the database.")
        conn.close()


    #create Table
    def createTable(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS NewsArticles (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            company TEXT,
                            author TEXT,
                            sourceID TEXT,
                            sourceName TEXT,
                            publishedAt DATETIME NOT NULL,
                            url TEXT NOT NULL,
                            body TEXT
                            );''')
        conn.close()
        print("table created")


    #store a ready article to a database
    def storeToDatabase (self, article):
        """
        store a ready article to a database

        Parameters:
            article (dict): the article to store

        Returns:
            None
        """
        conn = sqlite3.connect(DB_PATH)
        #setting up cursor
        c = conn.cursor()
        #setting up statement
        t = article["title"]
        comp = article["company"]
        a = article["author"]
        sID = article["source"]["Id"]
        sN = article["source"]["Name"]
        pA = article["publishedAt"]
        u = article["url"]
        b = article["body"]
        statement = ("INSERT INTO NewsArticles (title, company,  author, sourceID, sourceName, publishedAt, url, body) VALUES (?,?,?,?,?,?,?,?)")
        #execute statment
        c.execute(statement, (t, comp, a, sID, sN, pA, u, b))
        #commit changes
        conn.commit()
        #close connection
        conn.close()


    #get highest id value stored in database
    def getMaxId(self):
        """
        get highest id value stored in database

        Parameters:
            None

        Returns:
            maxId (int): the highest id value stored in the database
        """
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Execute SQL query to get maximum ID value
        c.execute("SELECT MAX(id) FROM NewsArticles")
        maxId = c.fetchone()[0]
        # Close connection and return result
        conn.close()
        return int(maxId)


    #store ready articles to database
    def storeReadyArticlesToDatabase(self):
        '''
        store ready articles to database

        Parameters:
            None

        Returns:
            None
        '''
        #check if article already in DB
        for i in self.readyArticles:
            #if article not in DB
            if (self.checkIfArticleInDB(i) == False):
                #store article
                self.storeToDatabase(i)

    
    #check if article is in database
    def checkIfArticleInDB(self, article):
        '''
        check if article is in database

        Parameters:
            article (dict): the article to check

        Returns:
            True if article in database, False if not
        '''
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Execute SQL query to get maximum ID value
        c.execute("SELECT * FROM NewsArticles WHERE title = ?", (article["title"],))
        result = c.fetchone()
        # Close connection and return result
        conn.close()
        if result == None:
            return False
        else:
            return True


    #delete table from database
    def delTable(self, table):
        '''
        delete table from database

        Parameters:
            table (string): the table to delete

        Returns:
            None
        '''
        # Connect to the database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Execute SQL query to get maximum ID value
        c.execute("DROP TABLE {}".format(table))
        # Close connection and return result
        conn.close()

    #------------------------------------------Diagnostic section -------------------------------------------
    
    #find longest title in ready articles
    def findLongestTitle (self):
        """
        find longest title in ready articles

        Parameters:
            None
        
        Returns:
            longest (int): the length of the longest title
        """
        #store length of longest title
        longest = 0
        #go through each article
        for i in self.readyArticles:
            #if title is longer than longest
            if (len(i["title"]) > longest):
                #set longest to new longest
                longest = len(i["title"])
        #return longest
        return longest


    #find longest body in ready articles
    def findLongestBody (self):
        """
        find longest body in ready articles 

        Parameters:
            None

        Returns:
            longest (int): the length of the longest body
        """
        #store length of longest body
        longest = 0
        #go through each article
        for i in self.readyArticles:
            #if body is longer than longest
            if (len(i["body"]) > longest):
                #set longest to new longest
                longest = len(i["body"])
        #return longest
        return longest


    #find longest url in ready articles
    def findLongestURL (self):
        """
        find longest url in ready articles
        
        Parameters:
            None
            
        Returns:
            longest (int): the length of the longest url
        """
        #store length of longest url
        longest = 0
        #go through each article
        for i in self.readyArticles:
            #if url is longer than longest
            if (len(i["url"]) > longest):
                #set longest to new longest
                longest = len(i["url"])
        #return longest
        return longest

