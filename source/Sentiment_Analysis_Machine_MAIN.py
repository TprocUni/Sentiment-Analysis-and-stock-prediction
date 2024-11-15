#Sentiment_Analysis_Machine_MAIN
from Modules.Sentiment_Analysis_MAIN import SentimentEngine, Article
from Modules.Text_Processing_MAIN import TextCleaner
import json
import os
import time
import datetime

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


def changeConfigData(configTarget, newValue):
    '''
    Changes the config data
    
    Parameters:
        configTarget (str): the target of the config data to be changed
        newValue (str): the new value of the config data

    Returns:
        None
    '''
    current_directory = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_directory, 'config.json')
    with open(config_path, 'r') as f:
        configData = json.load(f)
        configData[configTarget] = newValue
    with open(config_path, 'w') as f:
        json.dump(configData, f, indent=4)


def main():
    pass
    #Set up onjects and data structures
    SE = SentimentEngine()
    TC = TextCleaner()
    last_run = datetime.datetime.now()

    while True:
        #get config data
        configData = getConfigData()
        SA_HEURISTIC = int(configData["SA_HEURISTIC"])

        #time stuff to ensure that data is not gotten too often from DB
        now = datetime.datetime.now()
        elapsed_time = (now - last_run).total_seconds()
        #add tolerance to let it work i
        if elapsed_time%3600 <= 1:  # Check if 1 hour (3600 seconds) has passed
            # This should be done only once an hour
            SE.getWordList()
            print("getting the unprocessed word list")
            SE.getWordListUnprocessed()
            last_run = now
        

        #CURRENT_ARTICLE is a list with the following elements [ID, COMPANY, WORDS, SENTIMENT, PROCESSED]
        currentArticle = configData["CURRENT_ARTICLE"]
        
        
        #case where no articles have been examined
        if currentArticle == []:
            #get first article in database
            #SE.readyArticles is a object with 5 attributes, id, company ,and words [], SA, and processed
            targetArticle = SE.readyArticles[0]
            currentArticle = [targetArticle.id, targetArticle.company, 0, False]
            currentArticleWords = targetArticle.words
        elif currentArticle[3] == True and int(currentArticle[0]) < len(SE.readyArticles):
            #get next article in database
            print("updating article")
            oldArticle = currentArticle
            newArticle = SE.readyArticles[int(oldArticle[0])]
            currentArticle = [newArticle.id, newArticle.company, 0, False]
            currentArticleWords = newArticle.words
        else:
            #get current article from config
            currentArticleID = currentArticle[0]
            currentArticleWords = SE.readyArticles[int(currentArticleID)].words


        #deduce sentiment based off of CONFIG sentiment analysis method
        if currentArticle[3] == False:
            sentiment = 0
            if SA_HEURISTIC in [x for x in range(1,5)]:
                #do sentiment analysis
                if SA_HEURISTIC == 1:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisVader1(currentArticleWords)["compound"]
                elif SA_HEURISTIC == 2:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisVader2(currentArticleWords)["compound"]
                elif SA_HEURISTIC == 3:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisNLTK(currentArticleWords)["compound"]
                elif SA_HEURISTIC == 4:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisTextBlob(currentArticleWords)[0]
                    #do sentiment analysis
            #check if we are doing unprocessed data
            elif SA_HEURISTIC in [x for x in range(5,9)]:
                #get unprocessed data
                #tokenize
                currentArticleData = SE.processingArticles[int(currentArticle[0])]
                currentArticleDataTokenised = TC.tokenise(currentArticleData[8])
                if SA_HEURISTIC == 5:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisVader1(currentArticleDataTokenised)["compound"]
                elif SA_HEURISTIC == 6:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisVader2(currentArticleDataTokenised)["compound"]
                elif SA_HEURISTIC == 7:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisNLTK(currentArticleDataTokenised)["compound"]
                elif SA_HEURISTIC == 8:
                    #do sentiment analysis
                    sentiment = SE.sentimentAnalysisTextBlob(currentArticleDataTokenised)[0]
            else:
                print("Invalid SA_HEURISTIC value in config.json")
            #apply sentiment to currentArticle
            currentArticle[2] = sentiment


            #push currentArticle to CONFIG
            sendArticle = [currentArticle[0], currentArticle[1], currentArticle[2], currentArticle[3]]
            print
            changeConfigData("CURRENT_ARTICLE", sendArticle)
            print(f"sending article to config: {sendArticle}")
            #wait for SCN to apply

        #start next cycle
        #use input or sleep
        input()
        #time.sleep(10)



if __name__ == "__main__":
    main()










#final graph
#do same as above, end of day check predicted moves against actual moves
#make graphs