#Data acquisition and processing
from Modules.Text_Processing_MAIN import TextCleaner, processArticle
from Modules.News_Sourcing_MAIN import NewsAPISourcer
from Modules.Get_financial_data_MAIN import getListOfNamesFromDB
import time
import json
import os


import schedule
from datetime import datetime



#gets data from config file
def getConfigData():
    '''
    Gets the data from the config file
    
    Parameters:
        None

    Returns:
        configData (dict): dictionary of the config data'''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_directory, 'config.json')
    with open(config_path, 'r') as f:
        configData = json.load(f)
    return configData



#read from config file
#main
def main():
    #set up needed objects
    NAPIS = NewsAPISourcer()
    TC = TextCleaner()
    #get config data
    configData = getConfigData()
    
    #deletingTables
    #NAPIS.delTable("NewsArticles")
    #NAPIS.delTable("ProcessedArticles")

    input()

    NAPIS.createTable()
    TC.checkTablePAExists()

    #GET NEW ARTICLES
    #generate topic for getting data
    index = configData["INDEX"]

    #create list of queries based on the names in the database
    names = getListOfNamesFromDB(index)
    #queries = NAPIS.makeQuerys(names)
    NAPIS.getURLs(names)
    NAPIS.storeReadyArticlesToDatabase()

    print("processing articles")

    #important variables for processing data
    idOfMaxNewsArticle = NAPIS.getMaxId() #last gotten article
    idOfMaxProcessedArticle = TC.getMaxId() #this is the last processed article, since ids are keys

    #PROCESS NEW ARTICLES
    print(f"max news article: {idOfMaxNewsArticle}")
    print(f"max processed article: {idOfMaxProcessedArticle}")

    if idOfMaxNewsArticle > idOfMaxProcessedArticle:
        TC.getDataFromDatabase(idOfMaxProcessedArticle)
        processArticle(TC)
        idOfMaxProcessedArticle += 1

    print("added articles")




main()

#Functionality to make the call at xx:45 for each hour between 08 and 15, slightly before open and close of each market
#add functionality to adjust range based on market location.
if __name__ == "main":
    # Schedule the job to run at xx:45 for each hour between 08 and 15
    for hour in range(8, 15):
        schedule.every().day.at(f"{hour}:45").do(main)
    # Run the scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)