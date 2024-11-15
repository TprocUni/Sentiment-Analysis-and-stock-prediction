#Get financial data

#------------------------------------------Imports--------------------------------------------------------------
import requests
from pytickersymbols import PyTickerSymbols
import sqlite3
import os
import csv
import json
import yfinance as yf
import pandas as pd
from datetime import datetime
import numpy as np
from scipy.stats import spearmanr
import random
import time
import ast
import plotly.graph_objects as go
import networkx as nx
from plotly.subplots import make_subplots
import pickle
import joblib




#------------------------------------------constants------------------------------------------------------------
# Replace YOUR_API_KEY with your actual API key
API_KEY = "XR43KVWO8E8BYI66"
SYMBOL = '^FTSE'

#Database path
parentDirectory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
configPath = os.path.join(parentDirectory, 'config.json')

# Get data from the config file
with open(configPath, 'r') as f:
    configData = json.load(f)

# Database path
DB_PATH = os.path.join(parentDirectory, configData["DB_PATH"])
CSV_PATH = os.path.join(os.getcwd(), configData["CSV_PATH"])
SAVED_GRAPH_STATE_PATH = os.path.join(os.getcwd(), configData["GRAPH_PATH"])

START_DATE = "2015-01-01"
END_DATE = "2020-01-01"
SERVER_IP = "http://127.0.0.1:5000/"




#------------------------------------------Database operations------------------------------------------------------
#Function to create FTSE100 DB
def createFTSE100DB():
    """
    Function to create FTSE100 DB
    
    Parameters:
        NONE
    
    Returns:
        Nothing
    """
    statement = "CREATE TABLE IF NOT EXISTS FTSE100 (name TEXT, ticker TEXT, industries TEXT, associatedCSV TEXT)"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    print("DB created FTSE")


#Function to create SP500 DB
def createSP500DB():
    """
    Function to create SP500 DB

    Parameters:
        NONE
    
    Returns:
        Nothing
    """
    statement = "CREATE TABLE IF NOT EXISTS SP500 (name TEXT, ticker TEXT, industries TEXT, associatedCSV TEXT)"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    print("DB created SP500")


#Function to create Nasdaq DB
def createNASDAQDB():
    """
    Function to create Nasdaq DB
    
    Parameters:
        NONE
    
    Returns:
        Nothing
    """
    statement = "CREATE TABLE IF NOT EXISTS Nasdaq (name TEXT, ticker TEXT, industries TEXT, associatedCSV TEXT)"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    print("DB created Nasdaq")


#add entry to one of the DBs
def addToDB(db, name, ticker, industries, associatedCSV):
    """
    add entry to one of the DBs

    Parameters:
        db (str): name of the database table to add to
        name (str): name of the company
        ticker (str): ticker of the company
        industries (list): industries the company is in
        associatedCSV (str): name of the CSV file associated with the company

    Returns:
        Nothing
    """
    statement = "INSERT INTO " + db + " (name, ticker, industries, associatedCSV) VALUES (?,?,?,?)"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    jsonIndustries = json.dumps(industries)
    cursor.execute(statement, (name, ticker, jsonIndustries, associatedCSV))
    #commit changes
    conn.commit()
    #close connection
    conn.close()


#get data from the DB for a specific ticker and index
def getDataFromDB(ticker, index):
    """
    Get data from the DB for a specific ticker and index

    Parameters:
        ticker (str): ticker of the company
        index (str): index the company is in (e.g. "FTSE100")
    
    Returns:
        newTuple (tuple): tuple containing the data for the company
    """
    #statement to get data from db
    statement = "SELECT * FROM " + index + " WHERE ticker = '" + ticker + "'"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #get data
    data = cursor.fetchall()
    #close connection
    conn.close()
    #DO STUFF TO CONVERT TO GOOD FORM
    newTuple = (data[0][0], data[0][1], json.loads(data[0][2]), data[0][3])
    #return data
    return newTuple


#get list of tickers from database
def getListOfTickersFromDB(index):
    """
    get list of tickers from database

    Parameters:
        index (str): some index (e.g. "FTSE100")

    Returns:
        data (list): list of tickers

    """
    #statement to get data from db
    if index == "NASDAQ":
        index = "Nasdaq"
    statement = "SELECT ticker FROM " + index
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #get data
    data = cursor.fetchall()
    #close connection
    conn.close()
    #format data
    data = [x[0] for x in data]
    #return data
    return data


#get list of names from database
def getListOfNamesFromDB(index):
    """
    get list of names from database

    Parameters:
        index (str): some index (e.g. "FTSE100")

    Returns:
        data (list): list of names

    """
    #statement to get data from db
    statement = "SELECT name FROM " + index
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #get data
    data = cursor.fetchall()
    #close connection
    conn.close()
    #format data
    data = [x[0] for x in data]
    #return data
    return data


#Check for content in the given table
def checkTableContent(index):
    """
    Check for content in the given table

    Parameters:
        index (str): some index (e.g. "FTSE100")
    
    Returns:
        result (int): 1 if table has content, 0 if not

    """
    #connect to DB
    conn = sqlite3.connect(DB_PATH)  
    cursor = conn.cursor()
    #execute statement
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {index})")
    #check if table has content
    result = cursor.fetchone()[0]
    #close DB connection
    conn.close()
    #return result
    return result


#Deletes all data from a table
def delTableContents(index):
    """
    Deletes all data from a table

    Parameters:
        index (str): some index (e.g. "FTSE100")
    
    Returns:
        Nothing
    
    """
    #statement to delete table contents
    statement = "DELETE FROM " + index
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #commit changes
    conn.commit()
    #close connection
    conn.close()


#gets all available industries from the database under some index
def getIndexIndustries(index):
    """
    gets all available industries from the database under some index and returns the rate of appearance too

    Parameters:
        index (str): some index (e.g. "FTSE100")

    Returns:
        industries (dictionary): dictionary of industries (industry: rate of appearance)
    
    """
    #statement to get data from db
    statement = "SELECT industries FROM " + index
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #get data
    data = cursor.fetchall()
    #close connection
    conn.close()
    #create industries dict
    industries = {}
    #go through the fetched data and add to industries dict, or increment if already in dict
    for tuple in data:
        for element in tuple:
            element = ast.literal_eval(element)
            for item in element:
                if item in industries:
                    industries[item] += 1
                else:
                    industries[item] = 1

    return industries


#gets all tickers for a given industry under some index
def getIndustryTickers(index, industry):
    """
    gets all tickers for a given industry under some index
    
    Parameters:
        index (str): some index (e.g. "FTSE100")
        industry (str): some industry (e.g. "Technology")

    Returns:
        tickers (list): list of tickers for a given industry under some index
    
    """
    #statement to get data from db
    statement = "SELECT ticker FROM " + index + " WHERE industries LIKE '%" + industry + "%'"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #get data
    data = cursor.fetchall()
    #close connection
    conn.close()
    #format data
    data = [x[0] for x in data]
    #return data
    return data


#find the tickre of a company from its name
def findTickerFromName(name, index):
    """
    finds the ticker of a company from its name
    
    Parameters:
        name (str): name of the company
        index (str): index to get tickers from
    
    Returns:
        ticker (str): ticker of the company
    """
    #statement to get data from db
    if index == "NASDAQ":
        index = "Nasdaq"
    statement = "SELECT ticker FROM " + index + " WHERE name = '" + name + "'"
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    #execute statement
    cursor.execute(statement)
    #get data
    data = cursor.fetchall()
    #close connection
    conn.close()
    #format data
    data = [x[0] for x in data]
    #return data
    return data[0]

#--------------------------------------------Data acquisition-------------------------------------------------------
#gets the up to date list of tickers in the FTSE100 using PyTickerSymbols
def getFTSE100Data():
    """
    gets the up to date list of tickers in the FTSE100 using PyTickerSymbols
    
    Parameters:
        None
        
    Returns:
        ftse100 (list): list of tickers in the FTSE100 (up to date)"""
    #set up PyTickerSymbols object
    stockData = PyTickerSymbols()
    #get data
    ftse100 = stockData.get_stocks_by_index('FTSE 100')
    #return data
    return list(ftse100)


#gets the up to date list of tickers in the SP500 using PyTickerSymbols
def getSP500Data():
    """
    gets the up to date list of tickers in the SP500 using PyTickerSymbols
    
    Parameters:
        None
    
    Returns:
        sp500 (list): list of tickers in the SP500 (up to date)"""
    #set up PyTickerSymbols object
    stockData = PyTickerSymbols()
    #get data
    sp500 = stockData.get_stocks_by_index('S&P 500')
    #return data
    return list(sp500)


#gets the up to date list of tickers in the Nasdaq using PyTickerSymbols
def getNASDAQData():
    """
    gets the up to date list of tickers in the Nasdaq using PyTickerSymbols
    
    Parameters:
        None
    
    Returns:
        nasdaq (list): list of tickers in the Nasdaq (up to date)
    """
    #set up PyTickerSymbols object
    stockData = PyTickerSymbols()
    #get data
    nasdaq = stockData.get_stocks_by_index('NASDAQ 100')
    #return data
    return list(nasdaq)


#get a list of tickers for an index using PyTickerSymbols
def getIndexData(index):
    """
    gets the up to date list of tickers in the index using PyTickerSymbols
    
    Parameters:
        None
        
    Returns:
        tickers (list): list of tickers in the index (up to date)"""
    #set up PyTickerSymbols object
    stockData = PyTickerSymbols()
    #get data
    tickers = stockData.get_stocks_by_index(index)
    #return data
    return list(tickers)


#gets data for a ticker within a specified date range, uses Alpha Vantage API - MAX 5 CALLS PER MINUTE BAD
def getTickerData3(ticker, startDate=START_DATE, endDate=END_DATE):
    """
    Gets data for a ticker within a specified date range, uses Alpha Vantage API - MAX 5 CALLS PER MINUTE BAD
    
    Parameters:
        ticker (str): ticker of the company, default value stored in constant START_DATE
        startDate (str): start date of the data, default value stored in constant END_DATE
        endDate (str): end date of the data

    Returns:
        data (dictionary): list of financial data for the company between the specified dates
    """
    #get data from API
    response = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + ticker + "&outputsize=full&apikey=" + API_KEY)
    #transform data into json
    response = response.json()
    #check if data is valid
    if "Error Message" in response:
        print("Error: ", response["Error Message"])
        return None
    #get only data within the specified date range
    data = {}
    for date, values in response["Time Series (Daily)"].items():
        if startDate <= date <= endDate:
            data[date] = values
    response["Time Series (Daily)"] = data
    #return data
    return response


# gets data for a ticker within a specified date range, uses yfinance - MAX 2 CALLS PER SECOND GOOD
def getTickerData4(ticker, startDate=START_DATE, endDate=END_DATE):
    """
    Gets data for a ticker within a specified date range, uses yfinance - MAX 2 CALLS PER SECOND GOOD

    Parameters:
            ticker (str): ticker of the company, default value stored in constant START_DATE
            startDate (str): start date of the data, default value stored in constant END_DATE
            endDate (str): end date of the data
    
    Returns:
        data (dictionary): list of financial data for the company between the specified dates
    """
    # retrieve data using yfinance
    data = yf.download(ticker, start=startDate, end=endDate)
    # change column names to lower case and replace spaces with underscores
    data.columns = [col.lower().replace(' ', '_') for col in data.columns]
    # convert dataframe to dictionary
    dataDict = data.to_dict('index')
    # reformat dictionary to match response from previous function
    response = {}
    response['Meta Data'] = {}
    response['Meta Data']['Symbol'] = ticker
    response['Time Series (Daily)'] = {}
    for date, values in dataDict.items():
        response['Time Series (Daily)'][date.strftime('%Y-%m-%d')] = {}
        response['Time Series (Daily)'][date.strftime('%Y-%m-%d')]['1. open'] = values['open']
        response['Time Series (Daily)'][date.strftime('%Y-%m-%d')]['2. high'] = values['high']
        response['Time Series (Daily)'][date.strftime('%Y-%m-%d')]['3. low'] = values['low']
        response['Time Series (Daily)'][date.strftime('%Y-%m-%d')]['4. close'] = values['close']
        response['Time Series (Daily)'][date.strftime('%Y-%m-%d')]['5. volume'] = values['volume'] 
    # return data
    return response


#--------------------------------------------CSV operations------------------------------------------------------------
#Function to create CSV file containing historical data for a ticker
def createCSV(ticker, data, index):
    """
    Function to create CSV file containing historical data for a ticker
    
    Parameters:
        ticker (str): ticker of the company
        data (dictionary): data to be written to the CSV file
        index (str): index to get tickers from
        
    Returns:
        None
    """
    #create csv file
    with open(os.path.join(CSV_PATH, os.path.join(index, (ticker + ".csv"))), "w", newline="") as csvfile:
        #create writer object
        writer = csv.writer(csvfile)
        #write headers
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        #write data
        for date, values in data.items():
            writer.writerow([date, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["5. volume"]])


# Function to create training and testing CSV files for a ticker, takes last testSize% of data points as testing data (default is 25%)
def createTrainTestCSVsSplit(ticker, data, index, testSize=0.25):
    """
    Function to create training and testing CSV files for a ticker, takes last testSize% of data points as testing data (default is 25%)
    
    Parameters:
        ticker (str): ticker of the company
        data (dictionary): data to be split into training and testing sets, as a dictionary with keys "Date", "Open", "High", "Low", "Close", and "Volume"
        index (str): index to get tickers from

    Returns:
        None
    """
    # check if testSize is valid
    if testSize < 0 or testSize > 1:
        print("Error: testSize must be between 0 and 1")
        return
    # Create the training and testing data
    trainData = {}
    testData = {}
    #find index to split at
    splitIndex = int(len(data) * (1 - testSize))
    #split the data by checking the count
    for key in data:
        #check if the count is greater than the split index
        if len(trainData) < splitIndex:
            trainData[key] = data[key]
        else:
            testData[key] = data[key]
    # Save the training data to a CSV file
    trainFile = os.path.join(CSV_PATH, os.path.join(index, (ticker + "Train.csv")))
    with open(trainFile, "w", newline="") as csvfile:
        # create writer object
        writer = csv.writer(csvfile)
        # write headers
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        # write data
        for key, values in trainData.items():
            row = [key, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["5. volume"]]
            writer.writerow(row)
    # Save the testing data to a CSV file
    test_filename = os.path.join(CSV_PATH, os.path.join(index, (ticker + "Test.csv")))
    with open(test_filename, "w", newline="") as csvfile:
        # create writer object
        writer = csv.writer(csvfile)
        # write headers
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        # write data
        for key, values in testData.items():
            row = [key, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["5. volume"]]
            writer.writerow(row)


# Function to create training and testing CSV files for a ticker, takes every nth data point as testing data, default n = 4
def createTrainTestCSVsEveryN(ticker, data, index, n = 4):
    """
    Function to create training and testing CSV files for a ticker, takes every nth data point as testing data

    Parameters:
        ticker (str): ticker of the company
        data (dictionary): data to be split into training and testing sets, as a dictionary with keys "Date", "Open", "High", "Low", "Close", and "Volume"
        index (str): index to get tickers from
        n (int): number of data points to skip between testing data points, default is n = 4

    Returns:
        None
    """
    # Split the data into training and testing sets
    trainData = {}
    testData = {}
    i = 0
    for key in data:
        if i % n == 0:
            testData[key] = data[key]
        else:
            trainData[key] = data[key]
        i += 1
    # Save the training data to a CSV file
    trainFilename = os.path.join(CSV_PATH, os.path.join(index, (ticker + "Train.csv")))
    with open(trainFilename, "w", newline="") as csvfile:
        # create writer object
        writer = csv.writer(csvfile)
        # write headers
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        # write data
        for key, values in trainData.items():
            row = [key, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["5. volume"]]
            writer.writerow(row)
    # Save the testing data to a CSV file
    testFilename = os.path.join(CSV_PATH, os.path.join(index, (ticker + "Test.csv")))
    with open(testFilename, "w", newline="") as csvfile:
        # create writer object
        writer = csv.writer(csvfile)
        # write headers
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
        # write data
        for key, values in testData.items():
            row = [key, values["1. open"], values["2. high"], values["3. low"], values["4. close"], values["5. volume"]]
            writer.writerow(row)


#Function to read CSV file containing historical data for a ticker
def readCSV(ticker, index, train = ""):
    """
    Function to read CSV file containing historical data for a ticker
    
    Parameters:
        ticker (str): ticker of the company
        index (str): index to get tickers from
        train (str): string to append to the end of the filename, default is empty string, can be "Train" or "Test"
    
    Returns:
        data (list): historical data for a ticker in the specified index file
    """
    #open csv file
    with open(os.path.join(CSV_PATH, os.path.join(index ,(ticker + train + ".csv"))), "r") as csvfile:
        #create reader object
        reader = csv.reader(csvfile)
        #skip headers
        next(reader)
        #read data
        data = []
        for row in reader:
            data.append(row)
        #return data
        return data
    

#Deletes all CSV files in a directory
def deleteCSVFiles(index):
    """
    Deletes all CSV files in a directory

    Parameters:
        index (str): index referencing the directory

    Returns:
        Nothing
    """
    #create path to directory
    path = os.path.join(CSV_PATH, index)
    #iterate through all files in directory
    for filename in os.listdir(path):
        #remove if file is a CSV file
        if filename.endswith(".csv"):
            os.remove(os.path.join(path, filename))


#--------------------------------------------Diagnostics------------------------------------------------------------
#checks length of a list
def checkLen(lst):
    """
    Checks length of a list
    
    Parameters:
            lst (List): list to check length of
            
    Returns:
            Nothing
    """
    #check if list is empty
    if len(lst) == 0:
        print("List is empty")
    else:
        print("List is not empty: ", len(lst))


#finds the n most frequently appearing industries in a dictionary
def getMostFrequentIndustries(industryDict, n):
    """
    Finds the n most frequently appearing industries in a dictionary
    
    Parameters:
            industryDict (Dict): dictionary of industries 
            n (int): number of industries to return
    """
    #create list of tuples containing industries and their frequencies
    industries = [(industry, industryDict[industry]) for industry in industryDict]
    #sort list by frequency
    industries.sort(key = lambda x: x[1], reverse = True)
    #return n most frequent industries
    return industries[:n]


#--------------------------------------------Data Processing------------------------------------------------------------

#Function to get two key data points from financial history lists
def makeTuples(list, comparator1, comparator2):
    """
    Function to get two key data points from financial history lists

    Parameters:
        list (list): list of financial data
        comparator1 (str): first data point to be extracted, e.g. "Open"
        comparator2 (str): second data point to be extracted, e.g. "Close"
    
    Returns:
        tuples (list): list of tuples containing the two data points
    """
    #create list to store tuples
    tuples = []
    #deduce index of comparator1 - order chosen for max efficiency
    if comparator1.lower() == "open":
        compInd1 = 1
    elif comparator1.lower() == "close":
        compInd1 = 4
    elif comparator1.lower() == "high":
        compInd1 = 2
    elif comparator1.lower() == "low":
        compInd1 = 3
    else:
        print("Invalid argument: comparator1")
        return None
    #deduce index of comparator2 - order chosen for max efficiency
    if comparator2.lower() == "open":
        compInd2 = 1
    elif comparator2.lower() == "close":
        compInd2 = 4
    elif comparator2.lower() == "high":
        compInd2 = 2
    elif comparator2.lower() == "low":
        compInd2 = 3
    else:
        print("Invalid argument: comparator2")
        return None
    #iterate through list
    for row in list:
        #create tuple
        tup = (row[0], row[compInd1], row[compInd2])
        #add tuple to list
        tuples.append(tup)
    #return list of tuples
    return tuples


#Function to compare two lists of tuples
def compareTuplesLists(list1, list2):
    """
    Function to compare two lists of tuples

    Parameters:
        list1 (list): first list of tuples
        list2 (list): second list of tuples

    Returns:
        results (list): list of values comparing the polarity of the results (1,0,-1) meaning (both went the same way (e.g. both rose), both remained the same, couple went opposite rounds
    """
    # create list to store results
    results = []
    # iterate through list1
    for i in range(len(list1)):
        # check if the date in list1 is in list2
        for j in range(len(list2)):
            if list1[i][0] == list2[j][0]:
                # create variables to store polarity of each tuple - did the stock go up or down
                list1CurrentPolarity = float(list1[i][1]) - float(list1[i][2])
                list2CurrentPolarity = float(list2[j][1]) - float(list2[j][2])
                # check if both went the same way
                if (list1CurrentPolarity > 0 and list2CurrentPolarity > 0) or (list1CurrentPolarity < 0 and list2CurrentPolarity < 0):
                    results.append(1)
                # check if both remained the same
                elif list1CurrentPolarity == 0 and list2CurrentPolarity == 0:
                    results.append(0)
                # check if both went the opposite ways
                else:
                    results.append(-1)
    # return results
    return results


#Function to create a list of polarity values from a list of tuples
def createPolarityLists(tupleList1, tupleList2):
    """
    Function to create a list of polarity values from a list of tuples
    
    Parameters:
        tupleList1 (list): first list of tuples
        tupleList2 (list): second list of tuples
        
    Returns:
        polarityList1 (list): list of polarity values for tupleList1
    """
    #create list to store polarity values
    polarityList1 = []
    polarityList2 = []
    #create var to see which list is longer
    longerListLen = len(tupleList1) if len(tupleList1) < len(tupleList2) else len(tupleList2)
    #iterate through tuples
    for i in range(longerListLen):
        try:
            date1 = tupleList1[i][0]
            #check for matching date in second list
            for j in range(len(tupleList2)):
                date2 = tupleList2[j][0]
                if date1 == date2:              
                    #check if stock went up
                    if float(tupleList1[i][1]) - float(tupleList1[i][2]) > 0:
                        #append a one to the polarityList
                        polarityList1.append(1)
                    #check if stock remained the same
                    elif float(tupleList1[i][1]) - float(tupleList1[i][2]) == 0:
                        #append a zero to the polarityList
                        polarityList1.append(0)
                    else:
                        #append a negative one to the polarityList
                        polarityList1.append(-1)
                    #check for second list
                    if float(tupleList2[j][1]) - float(tupleList2[j][2]) > 0:
                        polarityList2.append(1)
                    elif float(tupleList2[j][1]) - float(tupleList2[j][2]) == 0:
                        polarityList2.append(0)
                    else:
                        polarityList2.append(-1)
                    #break out of inner loop
                    break
        except IndexError:
            pass
    #return both lists
    return polarityList1, polarityList2


#Polarity Ratio
#Heuristic 1 uses a ratio of the number of positive values to the number of negative values to determine the overall polarity of the list, 
def heuristic1(lst):
    """
    Polarity Ratio
    Heuristic 1 uses a ratio of the number of positive values to the number of negative values to determine the overall polarity of the list
    
    Parameters:
        lst (list): list of polarity values
        
    Returns:
        corrCoef (float): value between -1 and 1 representing the overall polarity of the list
    """
    #count number of positive, negative and neutral values
    ones = lst.count(1)
    negOnes = lst.count(-1)
    zeroes = lst.count(0)
    #discard boundary cases
    if ones + negOnes == 0:
        return 0
    elif negOnes + zeroes == 0:
        return 1
    elif ones + zeroes == 0:
        return -1
    else:
        #perform calculation
        ratio = ones / (ones + negOnes)
        corrCoef = 2*(ratio-0.5)
        return corrCoef


#Cumulative Increment method - first day onwards
#Heuristic 2 - uses an algorithm to iteratively calculate the value of x, n starting on 1 so that each day has impact
def heuristic2(lst):    
    """
    Cumulative Increment method - first day onwards
    Heuristic 2 - uses an algorithm to iteratively calculate the value of x, n starting on 1 so that each day has impact
    formula is:  x += (p * n * (1 - abs(x))**2) / z        x is calculated val where p is the polarity, n is the number of consecutive polarity values, z is the length of the list
    
    Parameters:
        lst (list): list of polarity values
        
    Returns:
        x (float): value between -1 and 1 representing the overall polarity of the list
    """
    if len(lst) == 0:
        return 0
    x = 0.0         #current value of the calculation   
    p = lst[0]      #polarity (1 or -1)
    n = 1            #no. of consecutive polarity values
    z = len(lst)    #length of the list
    #iterate through the list amending the value of x each time
    for i in range(z):
        x += (p * n * (1 - abs(x))**2) / z
        #checks if the polarity is the same as the previous one
        if lst[i] == p:
            n += 1
        #else reset n and change p
        else:
            p = lst[i]
            n = 1
    return x


#ISSUES - when values tend to 1 or -1 the calc becomes unstable and finds it difficult to leave said values
#Heuristic 3 - uses an algorithm to iteratively calculate the value of x, n starting on 0 so that only runs of days with the same polarity have impact
def heuristic3(lst):
    """
    Cumulative Increment method - second day onwards
    Heuristic 3 - uses an algorithm to iteratively calculate the value of x, n starting on 0 so that only runs of days with the same polarity have impact
    formula is: x += ((p * n * (1 - abs(x))**2) / z)        x is calculated val where p is the polarity, n is the number of consecutive polarity values, z is the length of the list

    Parameters:
        lst (list): list of polarity values
        
    Returns:
        x (float): value between -1 and 1 representing the overall polarity of the list
    """
    if len(lst) == 0:
        return 0
    x = 0.0         #current value of the calculation
    p = lst[0]      #polarity (1 or -1)
    n = 0           #no. of consecutive polarity values
    z = len(lst)    #length of the list
    #iterate through the list
    for i in range(z):
        #perform the calculation
        x += ((p * n * (1 - abs(x))**2) / z)
        #check if polarity is the same as the previous one
        if lst[i] == p:
            n += 1
        #else reset n and change p
        else:
            n = 0
            p = lst[i]    
    return x


#Heuristic 4 - uses pearson correlation to calculate the correlation between the two lists
def heuristic4 (index, ticker1, ticker2, Train = ""):
    """
    Heuristic 4 - uses pearson correlation to calculate the correlation between the two lists of raw data

    Parameters:
        index (string): index to use
        ticker1 (string): ticker of first stock
        ticker2 (string): ticker of second stock
        Train (string): string to append to the end of the file name, Train or Test, default is ""

    Returns:
        corrCoef (float): value between -1 and 1 representing the correlation between the two lists
    """
    # Load the two datasets into pandas dataframes
    df1 = pd.read_csv(os.path.join(CSV_PATH, os.path.join(index ,(ticker1 + Train + ".csv"))))
    df2 = pd.read_csv(os.path.join(CSV_PATH, os.path.join(index ,(ticker2 + Train + ".csv"))))
    # Calculate the difference between open and close prices for each stock
    df1['priceDiff'] = df1['Close'] - df1['Open']
    df2['priceDiff'] = df2['Close'] - df2['Open']

    # Remove rows where priceDiff is 0
    df1 = df1[df1.priceDiff != 0]
    df2 = df2[df2.priceDiff != 0]
    # Merge the two dataframes into a single dataframe based on the date column
    mergedDf= pd.merge(df1[['Date', 'priceDiff']], df2[['Date', 'priceDiff']], on='Date', suffixes=('_1', '_2'))
    # Add if statement to check if all values under priceDiff columns are 
    #check if dataFrame is empty if so return 0 impying no correlation
    if mergedDf.empty:
        print("empty")
        return 0

    #if (mergedDf['priceDiff_1']).all() or (mergedDf['priceDiff_1']).all():
    #    print("has procd")
    #    return "bad data"
    # Calculate the Pearson correlation coefficient between the two stocks' price differences
    corrCoef = np.corrcoef(mergedDf['priceDiff_1'], mergedDf['priceDiff_2'])[0, 1]
    #return the correlation coefficient)
    return corrCoef


#Heuristic 5 - uses spearman correlation to calculate the correlation between the two lists
def heuristic5(index, ticker1, ticker2, Train = ""):
    """
    Heuristic 5 - uses spearman correlation to calculate the correlation between the two lists of raw data
    
    Parameters:
        index (string): index to use
        ticker1 (string): ticker of first stock
        ticker2 (string): ticker of second stock
        Train (string): string to append to the end of the file name, Train or Test, default is ""
        
    Returns:
        corrCoef (float): value between -1 and 1 representing the correlation between the two lists
    """
    # Load the two datasets into pandas dataframes
    df1 = pd.read_csv(os.path.join(CSV_PATH, os.path.join(index ,(ticker1 + Train + ".csv"))))
    df2 = pd.read_csv(os.path.join(CSV_PATH, os.path.join(index ,(ticker2 + Train + ".csv"))))
    # Calculate the difference between open and close prices for each stock
    df1['priceDiff'] = df1['Close'] - df1['Open']
    df2['priceDiff'] = df2['Close'] - df2['Open']
    # Remove rows where priceDiff is 0
    df1 = df1[df1.priceDiff != 0]
    df2 = df2[df2.priceDiff != 0]
    # Merge the two dataframes into a single dataframe based on the date column
    mergedDf= pd.merge(df1[['Date', 'priceDiff']], df2[['Date', 'priceDiff']], on='Date', suffixes=('_1', '_2'))
    # Add if statement to check if all values under priceDiff columns are 
    #check if dataFrame is empty, if so return 0 impying no correlation
    if mergedDf.empty:
        print("empty")
        return 0
    # Merge the two dataframes into a single dataframe based on the date column
    mergedDf= pd.merge(df1[['Date', 'priceDiff']], df2[['Date', 'priceDiff']], on='Date', suffixes=('_1', '_2'))
    # Calculate the Spearman correlation coefficient between the two stocks' price differences
    corrCoef = mergedDf[['priceDiff_1', 'priceDiff_2']].corr(method='spearman').iloc[0, 1]
    #return the correlation coefficient
    return corrCoef


#same as h5, uses pearson correlation to calculate the correlation between the two lists, uses polarity values instead of price differences
def heuristic6(lst1, lst2):
    """
    Heuristic 6 - uses pearson correlation to calculate the correlation between the two lists of polarity values
    
    Parameters:
        lst1 (list): list of polarity values for first stock
        lst2 (list): list of polarity values for second stock
        
    Returns:
        corrCoef (float): value between -1 and 1 representing the correlation between the two lists
    """
    # Calculate the Pearson correlation coefficient between the two stocks' polarity values
    corrCoef = np.corrcoef(lst1, lst2)[0, 1]
    #return the correlation coefficient
    return corrCoef


# Calculate the Spearman correlation coefficient between two lists of polarity values
def heuristic7(lst1, lst2):
    """
    Calculate the Spearman correlation coefficient between two lists of polarity values
    
    Parameters:
        lst1 (list): list of polarity values for first stock
        lst2 (list): list of polarity values for second stock
        
    Returns:
        corrCoef (float): value between -1 and 1 representing the correlation between the two lists
    """
    # Calculate the Spearman correlation coefficient between the two stocks' polarity values
    corrCoef = spearmanr(lst1, lst2)[0]
    # Return the correlation coefficient
    return corrCoef


#---------------------------------------------------Fitness functions------------------------------------------------------------------------------------------------------------------------

#Fitness function one - calcs multiplier/correlation value using a given heuristic for training data, then on test data and sees how similar they are
# works by seeing the difference between the tw0 values
def fitness1(f1, f2):
    """
    Fitness function one - calcs multiplier/correlation value using a given heuristic for training data, then on test data and sees how similar they are
    works by seeing the difference between the tw0 values

    Parameters:
        f1 (float): multiplier of training data
        f2 (float): multiplier of test data

    Returns:
        fitness (float): value that represents percentage difference between the two
    """
    if f1 == 0 or f2 == 0:
        #print("provided fitesses are 0, indicating no correlation")
        return 10000000
    #check if the two multipliers are the same sign 
    if (f1 < 0 and f2 > 0) or (f1 > 0 and f2 < 0):
        #if so, return 100000 - error code
        #print("provided fitesses are of opposite polarity")
        return 20000000
    #else return the difference between the two and make it as a percentage difference of the first
    else:
        #print(f"f1 is {f1} and f2 is {f2}")
        fitness = abs(f1 - f2)*100/f1
        return fitness
    

#compares the generated list of polarity values with the actual list of polarity values, and returns the percentage difference
def fitness2(r, lst, lst2):
    """
    Compares the generated list of polarity values with the actual list of polarity values, and returns the percentage difference
    
    Parameters:
        r (float): correlation multiplier value
        lst (list): list of polarity values from test set of 1st company
        lst2 (list): list of polarity values from test set of 2nd company
        
    Returns:
        fitness (float): value that represents percentage of incorrect predictions
    """
    #initialise list of predicted polarity values
    predicted = []
    #create list
    for i in lst:
        currentRand = random.random()
        #implies positive correlation
        if r > 0:
            if currentRand < r:
                predicted.append(i)
        #implies negative correlation
        elif r < 0:
            if currentRand*-1 > r:
                predicted.append(i*-1)
        #implies no correlation so there should be no change in polarity
        else:
            predicted.append(0)
    
    correctPredictions = 0
    incorrectPredictions = 0
    #compare the two lists and return the percentage difference
    for i in range(len(lst2)):
        if predicted[i] == lst2[i]:
            correctPredictions += 1
        elif predicted[i] == 0:
            pass
        else:
            incorrectPredictions += 1
    #get values for correct and incorrect prediction rates
    correctRatio = correctPredictions/len(predicted)
    incorrectRatio = incorrectPredictions/len(predicted)
    correctToIncorrectRatio = correctRatio/incorrectRatio
    return correctToIncorrectRatio


#Runs the fitness 1 function
def runFitness1(ticker1, ticker2, index, heuristic = 1):
    """
    Runs the fitness 1 function

    Parameters:
        ticker1 (string): ticker of first company
        ticker2 (string): ticker of second company
        index (string): index to use

    Returns:
        fitness (float): value to get the fitness of the heuristic used for the two companies
    """
    #check which heuristic is being used
    if heuristic == 1 or heuristic == 2 or heuristic == 3:
        #split data into training and test sets - two options, get data
        training1 = readCSV(ticker1, index, "Train")
        testing1 = readCSV(ticker1, index, "Test")
        training2 = readCSV(ticker2, index, "Train")
        testing2 = readCSV(ticker2, index, "Test") 
        #make tuples of the data
        trainingTups1 = makeTuples(training1, "Open", "Close")
        testingTups1 = makeTuples(testing1, "Open", "Close")
        trainingTups2 = makeTuples(training2, "Open", "Close")
        testingTups2 = makeTuples(testing2, "Open", "Close")
        #compare tups
        trainingPol = compareTuplesLists(trainingTups1, trainingTups2)
        testingPol = compareTuplesLists(testingTups1, testingTups2)
        if len(trainingPol) == 0 or len(testingPol) == 0:
            #error code for incompatible datasets
            return 30000000
        #see which heuristic to use
        if heuristic == 1:
            #train model on training
            x = heuristic1(trainingPol)
            #train model on test
            y = heuristic1(testingPol)
        elif heuristic == 2:
            x = heuristic2(trainingPol)
            y = heuristic2(testingPol)
        elif heuristic == 3:
            x = heuristic3(trainingPol)
            y = heuristic3(testingPol)
        #produce fitness value
    elif heuristic == 4:
        x = heuristic4(index, ticker1, ticker2, "Train")
        y = heuristic4(index, ticker1, ticker2, "Test")
        #bad data
        if x == "bad data" or y == "bad data":
            return 30000000
    elif heuristic == 5:
        x = heuristic5(index, ticker1, ticker2, "Train")
        y = heuristic5(index, ticker1, ticker2, "Test")
        #bad data
        if x == "bad data" or y == "bad data":
            return 30000000
    elif heuristic == 6 or heuristic == 7:
        #get data
        training1 = readCSV(ticker1, index, "Train")
        testing1 = readCSV(ticker1, index, "Test")
        training2 = readCSV(ticker2, index, "Train")
        testing2 = readCSV(ticker2, index, "Test") 
        #make tuples of the data
        trainingTups1 = makeTuples(training1, "Open", "Close")
        testingTups1 = makeTuples(testing1, "Open", "Close")
        trainingTups2 = makeTuples(training2, "Open", "Close")
        testingTups2 = makeTuples(testing2, "Open", "Close")
        #get polarity lists
        trainP1,trainP2 = createPolarityLists(trainingTups1, trainingTups2)
        testP1,testP2 = createPolarityLists(testingTups1, testingTups2)
        if heuristic == 6:
            x = heuristic6(trainP1, trainP2)
            y = heuristic6(testP1, testP2)
        elif heuristic == 7:
            x = heuristic7(trainP1, trainP2)
            y = heuristic7(testP1, testP2)

    #compare the two models
    fitness = fitness1(x, y)
    #print(f"fitness is {fitness} for {ticker1} and {ticker2}")
    #have some boundary that shows its ok
    return fitness


#Goes through each element of the index to check the fitness of the heuristic
def runAllFitness1(tickers, index, heuristic = 1):
    """
    Goes through each element of the index to check the fitness of the heuristic
    
    Parameters:
        tickers (list): list of tickers to use
        index (string): index to use
        heuristic (int): heuristic to use, default is 1
        
    Returns:
        tickerTupleFitnesses (list): list of tuples of the tickers and their fitnesses
    """
    #iterate through all possible edge combinations
    tickerTupleFitnesses = []
    for ticker1 in range(len(tickers)):
        for ticker2 in range(ticker1 + 1, len(tickers)):
            fitness = runFitness1(tickers[ticker1], tickers[ticker2], index, heuristic)
            tickerTupleFitnesses.append((tickers[ticker1]+" to "+tickers[ticker2], fitness))

    #have textual and graphical outputs
    return tickerTupleFitnesses


#---------------------------------------------------Node class-------------------------------------------------------------------------------------------------------------------------

#class to represent nodes in the semantic network
class Node:
    """
    Class to represent nodes in the semantic network

    Attributes:
        name (string): name of the company
        PO (float): public opinion of the company
        change (float): daily change of the company
        ticker (string): ticker of the company
        index (string): index of the company
        edges (list): list of edges connected to the node

    Methods:
        addEdge(edge): adds an edge to the node
        getEdges(): gets all edges connected to the node
        getName(): gets the name of the company
        getPO(): gets the public opinion of the company
        getTicker(): gets the ticker of the company
        getIndex(): gets the index of the company
        getChange(): gets the daily change of the company
        resetChange(): resets the daily change of the company

    """


    def __init__(self, name, ticker, index):
        """
        Constructor for the node class
        
        Parameters:
            name (string): name of the company
            ticker (string): ticker of the company
            index (string): index of the company
        """
        self.name = name
        self.PO = 0
        self.change = 0
        self.ticker = ticker
        self.index = index
        self.edges = []
        self.subEdges = []

    # Getters and setters for the node class
    #Adds edge
    def addEdge(self, edge):
        self.edges.append(edge)

    #adds sub edge
    def addSubEdge(self, edge):
        self.subEdges.append(edge)

    #gets all edges
    def getNodeEdges(self):
        return self.edges
    
    #gets name
    def getName(self):
        return self.name
    
    #gets Public opinion
    def getPO(self):
        return self.PO
    
    #set Public opinion
    def setPO(self, PO):
        self.PO = PO
    
    #gets ticker
    def getTicker(self):
        return self.ticker
    
    #gets index
    def getIndex(self):
        return self.index
    
    #gets daily change
    def getChange(self):  
        return self.change
    
    #sets daily change
    def setChange(self, change):
        self.change = change
    
    #reset daily change
    def resetChange(self):
        self.change = 0
    
    #Real functions
    

#---------------------------------------------------Edge class-------------------------------------------------------------

#class to represent edges in the semantic network
class Edge:
    """
    Class to represent edges in the semantic network

    Attributes:
        originalNode (Node): original node of the edge
        targetNode (Node): target node of the edge
        correlation (float): correlation between the two nodes
        edgeName (string): name of the edge

    Methods:
        getOriginalNode(): gets the original node of the edge
        getTargetNode(): gets the target node of the edge
        getCorrelation(): gets the correlation between the two nodes
        getEdgeName(): gets the name of the edge
    """
    def __init__(self, oNode, tNode, correlation):
        """
        Constructor for the edge class

        Parameters:
            oNode (Node): original node of the edge
            tNode (Node): target node of the edge
            correlation (float): correlation between the two nodes
        """
        self.originalNode = oNode
        self.targetNode = tNode
        self.correlation = correlation
        self.edgeName = oNode.getName() + " to " + tNode.getName()

    # Getters and setters for the edge class
    #gets original node
    def getOriginalNode(self):
        return self.originalNode
    
    #gets target node
    def getTargetNode(self):
        return self.targetNode
    
    #gets connectivity
    def getCorrelation(self):
        return self.correlation
    
    #gets edge name
    def getEdgeName(self):
        return self.edgeName
    

    #Real functions


#---------------------------------------------------Graph class-------------------------------------------------------------


#class to represent the semantic network
class Graph:
    """
    class to represent the semantic network

    Attributes:
        nodes (list): list of nodes in the network
        edges (list): list of edges in the network
        subGraph (boolean): whether the graph is a subgraph or not
        subNodes (list): list of nodes in the subgraph
        subEdges (list): list of edges in the subgraph
        name (string): name of the graph

    Methods:
        addNode(node): adds a node to the graph
        addEdge(edge): adds an edge to the graph
        getNodes(): gets all nodes in the graph
        getEdges(): gets all edges in the graph
        getSubNodes(): gets all nodes in the subgraph
        getSubEdges(): gets all edges in the subgraph
        generateSubGraph(subGraph, subGraphTickerList, threshold): generates a subgraph
        populateGraph(): populates the graph with nodes and edges
        createEdges(): creates edges between nodes
        createPlotlyGraph(): creates a plotly graph
        POPropagation1(): propagates public opinion through the graph, method 1 - if a previous change value has lower abs value than
                          one produced in a previous iteration, it is replaced.
        POPropagation2(): propagates public opinion through the graph, method 2 - averages out the change values from each iteration, 
                          cannot go back to original node.
        POPropagation3(): propagates public opinion through the graph, method 3 - once a value is set it cannot change
        applyChanges(): applies the changes to the graph
    
    """
    def __init__(self, index):
        self.nodes = []
        self.edges = []
        self.subGraph = False
        self.subNodes = []
        self.subEdges =[]
        self.name = "Stock Correlation Network - " + index
    
    # Getters and setters for the graph class
    #adds node
    def addNode(self, node):
        self.nodes.append(node)


    #adds edge
    def addEdge(self, edge):
        self.edges.append(edge)


    #gets all nodes
    def getNodes(self):
        return self.nodes
    

    #gets all edges
    def getEdges(self):
        return self.edges


    #gets all subnodes
    def getSubNodes(self):
        return self.subNodes
    

    #gets all subedges
    def getSubEdges(self):
        return self.subEdges
    

    #generate subgraph
    def generateSubGraph(self, subGraph, subGraphTickerList, threshold):
        """
        generates a subgraph of the graph

        Parameters:
            subGraph (boolean): whether or not to generate a subgraph
            subGraphTickerList (list): list of tickers to include in the subgraph
            threshold (float): threshold to use for ignoring correlation values
            
        Returns:
            None    
        """
        nodeList = []
        edgeList = []
        #get all relevant nodes
        if subGraph == True:
            for node in self.getNodes():
                if node.getTicker() in subGraphTickerList:
                    nodeList.append(node)
        else:
            nodeList = self.getNodes()
        #get all relevant edges
        for node in nodeList:
            #print(f"{node.getName()} has {len(node.getNodeEdges())} edges")
            for edge in node.getNodeEdges():
                #can change to strict inequalities to reduce edges with extreme correlation values
                if edge.getOriginalNode() in nodeList and edge.getTargetNode() in nodeList and (edge.getCorrelation() >= threshold or edge.getCorrelation() <= -1*threshold):
                    node.addSubEdge(edge)
                    if edge not in edgeList:
                        edgeList.append(edge)
                    
  
                
        #set subgraph
        self.subNodes = nodeList
        self.subEdges = edgeList


    #populate graph with nodes
    def populateGraph(self, index, tickerList):
        """
        Populates the graph with nodes
        
        Parameters:
            index (string): index to use
            tickerList (list): list of tickers to use
        
        Returns:
            None
        """
        #add tickers to the graph
        for i in tickerList:
            #get ticker data
            tickerData = getDataFromDB(i, index)
            #create node
            node = Node(tickerData[0], tickerData[1], index)
            #add node to graph
            self.addNode(node)


    #create edges between all nodes in the graph
    def createEdges(self, threshold = 0, heuristic = 1, train = ""):
        """
        Creates edges between all nodes in the graph
        
        Parameters:
            threshold (float): threshold to use for ignoring correlation values
            heuristic (int): heuristic to use for calculating correlation values
            train (string): training data to use for calculating correlation values, can be Train or Test
            
        Returns:
            None
        """
        #iterate through all nodes, make an edge between each node and every other node
        for i in range(len(self.nodes)):
            for j in range(i+1, len(self.nodes)):
                #create edge
                corrCoef = self.calculateEdgeValue(self.nodes[i], self.nodes[j], heuristic, train)
                if corrCoef > threshold or corrCoef < (-1*threshold):
                    edge = Edge(self.nodes[i], self.nodes[j], corrCoef)
                    #add edge to graph
                    self.addEdge(edge)


    #Calculates edge value for a given edge
    def calculateEdgeValue(self, node1, node2, heuristic = 1, train = ""):
        """
        Calculates the edge value for a given edge
        
        Parameters:
            edge (Edge): edge to calculate the value for
            
        Returns:
            corrCoef (float): correlation coefficient between the two nodes
        """
                
        #check which heuristic is being used
        if heuristic == 1 or heuristic == 2 or heuristic == 3:
            #get all necesary data and process it
            x = readCSV(node1.getTicker(), node1.getIndex(), train)
            x1 = readCSV(node2.getTicker(), node2.getIndex(), train)
            y = makeTuples(x, "open", "close")
            y1 = makeTuples(x1, "open", "close")
            fis = compareTuplesLists(y, y1)
            #check which heuristic precisely is being used
            if heuristic == 1:
                #calculate correlation coefficient
                corrCoef = heuristic1(fis)
            elif heuristic == 2:
                #calculate correlation coefficient
                corrCoef = heuristic2(fis)
            elif heuristic == 3:
                #calculate correlation coefficient
                corrCoef = heuristic3(fis)
        #check if heuristic 4 is being used
        elif heuristic == 4:
            corrCoef = heuristic4(node1.getIndex(), node1.getTicker(), node2.getTicker())
        #check if heuristic 5 is being used    
        elif heuristic == 5:
            corrCoef = heuristic5(node1.getIndex(), node1.getTicker(), node2.getTicker())
        #check if heuristic 6 or 7 is being used
        elif heuristic == 6 or heuristic == 7:  
            #get all necesary data and process it
            x = readCSV(node1.getTicker(), node1.getIndex(), train)
            x1 = readCSV(node2.getTicker(), node2.getIndex(), train)
            y = makeTuples(x, "open", "close")
            y1 = makeTuples(x1, "open", "close")
            q,q1 = createPolarityLists(y,y1)
            if heuristic == 6:
                corrCoef = heuristic6(q,q1)
            elif heuristic == 7:
                corrCoef = heuristic7(q,q1)

        #return correlation coefficient
        return corrCoef

        #get csv data for both nodes

        #make function to get list of tupled data from csv
        #make function which changes the csv data into a list of [1,0,-1] by comparing the open and close price
        # 
        #  
        #make alternate function using the high and low price

        #maybe try one which doesnt even use [1,0,-1] -> perhaps difference in price for each 


        #make different hueristics to calc edge value based off of comparison list


    #creates an interactive graph using plotly
    def createPlotlyGraph(self, threshHold, graphName):
        """
        creates an interactive graph using plotly

        Parameters:
            threshHold (float): threshold for edge creation - values beneath the thrwshold won't be shown as they dont have high enough correlation
            graphName (string): name of the graph


        Returns:
            fig (plotly figure): figure of the graph uses NetworkX
        """
        #get all nodes and edges, if subgraph make accordingly


        # Create a networkx graph and add nodes and edges
        G = nx.Graph()
        for node in self.subNodes:
            G.add_node(node.getName())

        for edge in self.subEdges:
            if edge.getCorrelation() > threshHold or edge.getCorrelation() < (threshHold)*-1:
                G.add_edge(edge.getOriginalNode().getName(), edge.getTargetNode().getName(), weight=edge.getCorrelation())


        # Compute node positions
        pos = nx.spring_layout(G, seed=42)

        # Prepare nodes, edges, and edge labels for plotly
        node_x = []
        node_y = []
        node_text = []
        edge_x = []
        edge_y = []
        edge_labels = []

        # Create a list to store the number of connections for each node
        node_connections = []

        # Create nodes on graph
        for node in G.nodes():
            x, y = pos[node]
            connections = G.degree(node)
            if connections == 0:
                continue
            node_x.append(x)
            node_y.append(y)
            # Find the corresponding node in the original graph (g) to access its PO and change values
            original_node = [n for n in self.getNodes() if n.getName() == node][0]
            node_text.append(f"Name: {node}<br>PO: {original_node.getPO()}<br>Change: {original_node.getChange()} <br>No. of Connections: {connections}")

            # Count the number of connections for the node
            node_connections.append(connections)

        # Create a color list based on the number of connections for each node
        color = node_connections

        # Create edges on graph
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.append(x0)
            edge_x.append(x1)
            edge_x.append(None)
            edge_y.append(y0)
            edge_y.append(y1)
            edge_y.append(None)

            # Add edge labels
            edge_center_x = (x0 + x1) / 2
            edge_center_y = (y0 + y1) / 2
            edge_labels.append(
                go.Scatter(
                    x=[edge_center_x],
                    y=[edge_center_y],
                    text=[f"{G.edges[edge]['weight']:.3f}"],  # Format weight to 3 decimal places
                    mode="lines",
                    hoverinfo="text",
                    showlegend=False,
                    textfont=dict(size=10),
                )
            )

        # Create plotly scatter trace for edges
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            mode='lines')
        # Create plotly scatter trace for nodes
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            hovertext=node_text,  # Add this line to set the hovertext
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=color,
                size=10,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line=dict(width=2)))

        # Set the hover text for nodes
        node_trace.text = node_text

        # Create the figure
        fig = go.Figure(
            data=[edge_trace, node_trace, *edge_labels],
            layout=go.Layout(
                title= self.name + str(graphName),
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        )

        # Show the figure
        #   fig.show()
        return fig


    #updates a node with a new PO value, propagates that value accross the graph method 1
    def POPropagation1 (self, depth, nodeTicker, nodeIncrement, threshold):
        """
        updates a node with a new change value, propagates that value accross the graph, if a previous change value has lower abs value than
        one produced in a previous iteration, it is replaced.
        
        Parameters:
            depth (int): depth of propagation
            nodeTicker (string): ticker of node to update
            nodeIncrement (float): amount to increment node by
            
        Returns:
            None
        """
        print("------------------------------------------------------------------------------------------------------------------------1")
        #find node
        workingNode = None
        for i in self.subNodes:
            if i.getTicker() == nodeTicker:
                workingNode = i

        if workingNode == None:
            print("Node not found")
            return
        #locate changed value
        workingNode.setChange(workingNode.getChange() + nodeIncrement)
        workingNodes = [workingNode]
        #do number of times = to depth
        for i in range(depth):
            print(f"on loop {i}")
            for node in workingNodes:
                print(f"on node: {node.getName()}")
                print(f"Change = {node.getChange()}")
                print(f"number of connecting edges = {len(node.subEdges)}")
                newWorkingNodes = []
                for edge in node.subEdges:
                    if abs(edge.getCorrelation()) > threshold:
                        #check if currentNode is targetNode or originalNode
                        if edge.getTargetNode() == node:
                            print(f"the target node is {edge.originalNode.getName()}")
                            #change value of original node
                            changeVal = edge.getCorrelation()*node.getChange()
                            print(f"changeVal is {changeVal}")
                            #see if changeVal is greater than originalNode daily change
                            if abs(changeVal) > abs(edge.originalNode.getChange()):
                                print(f"changing val")
                                edge.originalNode.setChange(changeVal)
                            #add originalNode to newWorkingNodes
                            if edge.originalNode not in newWorkingNodes:
                                newWorkingNodes.append(edge.originalNode)
                        else:
                            print(f"the target node is {edge.targetNode.getName()}")
                            #change value of target node
                            changeVal = edge.getCorrelation()*node.getChange()
                            print(f"changeVal is {changeVal}")
                            #see if changeVal is greater than targetNode daily change
                            if abs(changeVal) > abs(edge.targetNode.getChange()):
                                print(f"changing val")
                                edge.targetNode.setChange(changeVal)
                            #add targetNode to newWorkingNodes
                            if edge.targetNode not in newWorkingNodes:
                                newWorkingNodes.append(edge.targetNode)
            #find all nodes connected by edges to workingNodes
            workingNodes = newWorkingNodes


    #updates a node with a new PO value, propagates that value accross the graph method 2
    def POPropagation2 (self, depth, nodeTicker, nodeIncrement, threshold):
        """
        updates a node with a new change value, propagates that value accross the graph, averages out the change values from each iteration, cannot go back 
        to original node.

        Parameters:
            depth (int): depth of propagation
            nodeTicker (string): ticker of node to update
            nodeIncrement (float): amount to increment node by
        
        Returns:
            None
        """
        #find node
        originalNode = None
        for i in self.subNodes:
            if i.getTicker() == nodeTicker:
                originalNode = i

        if originalNode == None:
            print("Node not found")
            return
        #locate changed value
        originalNode.setChange(originalNode.getChange() + nodeIncrement)
        workingNodes = [originalNode]
        #do number of times = to depth
        for i in range(depth):
            print(f"on loop {i}")
            for node in workingNodes:
                print(f"on node: {node.getName()}")
                print(f"Change = {node.getChange()}")
                print(f"number of connecting nodes = {len(node.subEdges)}")
                newWorkingNodes = []
                for edge in node.subEdges:
                    if edge.getCorrelation() < threshold:
                        print(f"on edge: {edge.edgeName}")
                        #check if currentNode is targetNode or originalNode
                        if edge.getTargetNode() == node and edge.originalNode != originalNode:
                            print(f"the target node is {edge.originalNode.getName()}")
                            #change value of original node
                            changeVal = edge.getCorrelation()*node.getChange()
                            print(f"changeVal is {changeVal/depth}")
                            #add changeVal/depth to originalNode daily change
                            edge.originalNode.change += changeVal/depth
                            #add originalNode to newWorkingNodes
                            if edge.originalNode not in newWorkingNodes:
                                newWorkingNodes.append(edge.originalNode)

                        elif edge.targetNode != originalNode:
                            print(f"the target node is {edge.targetNode.getName()}")
                            #change value of target node
                            changeVal = edge.getCorrelation()*node.getChange()
                            print(f"changeVal is {changeVal}")
                            #add changeVal/depth to targetNode daily change
                            edge.targetNode.change += changeVal/depth
                            #add targetNode to newWorkingNodes
                            if edge.targetNode not in newWorkingNodes:
                                newWorkingNodes.append(edge.targetNode)
                        else:
                            pass
            #find all nodes connected by edges to workingNodes
            workingNodes = newWorkingNodes


    #updates a node with a new PO value, propagates that value accross the graph method 3
    def POPropagation3 (self, depth, nodeTicker, nodeIncrement, threshold):
        """
        updates a node with a new change value, propagates that value accross the graph, once a value is set it cannot change

        Parameters:
            depth (int): depth of propagation
            nodeTicker (string): ticker of node to update
            nodeIncrement (float): amount to increment node by
        
        Returns:
            None
        """
        #find node
        originalNode = None
        for i in self.subNodes:
            if i.getTicker() == nodeTicker:
                originalNode = i

        if originalNode == None:
            print("Node not found")
            return
        #locate changed value
        originalNode.setChange(originalNode.getChange() + nodeIncrement)
        workingNodes = [originalNode]
        #do number of times = to depth
        for i in range(depth):
            print(f"on loop {i}")
            for node in workingNodes:
                print(f"on node: {node.getName()}")
                print(f"Change = {node.getChange()}")
                print(f"number of connecting nodes = {len(node.subEdges)}")
                newWorkingNodes = []
                for edge in node.subEdges:
                    if edge.getCorrelation() < threshold:
                        print(f"on edge: {edge.edgeName}")
                        #check if currentNode is targetNode or originalNode
                        if edge.getTargetNode() == node and edge.originalNode != originalNode:
                            print(f"the target node is {edge.originalNode.getName()}")
                            #change value of original node
                            changeVal = edge.getCorrelation()*node.getChange()
                            #check of targets dailychange is 0, if so update it to changeVal
                            if edge.originalNode.getChange() == 0:
                                edge.originalNode.setChange(changeVal)
                            #add originalNode to newWorkingNodes
                            if edge.originalNode not in newWorkingNodes:
                                newWorkingNodes.append(edge.originalNode)

                        elif edge.targetNode != originalNode:
                            print(f"the target node is {edge.targetNode.getName()}")
                            #change value of target node
                            changeVal = edge.getCorrelation()*node.getChange()
                            #check of targets dailychange is 0, if so update it to changeVal
                            if edge.targetNode.getChange() == 0:
                                edge.targetNode.setChange(changeVal)
                            #add targetNode to newWorkingNodes
                            if edge.targetNode not in newWorkingNodes:
                                newWorkingNodes.append(edge.targetNode)
                        else:
                            pass
            #find all nodes connected by edges to workingNodes
            workingNodes = newWorkingNodes        


    # apply changes to PO the graph
    def applyChanges (self):
        """
        Applies the daily change to the PO value of each node

        Parameters:
            None
        
        Returns:
            None
        """
        for node in self.subNodes:
            node.setPO(node.getPO() + node.getChange())
            node.setChange(0)

    #adds edges to appropriate nodes
    def addEdgesToNodes(self):
        """
        Adds edges to nodes

        Parameters:
            None
        
        Returns:
            None
        """
        for edge in self.edges:
            edge.originalNode.addEdge(edge)
            edge.targetNode.addEdge(edge)

#--------------------------------------------Save State------------------------------------------------------------

#save the state of the graph to a file
def saveGraphState(graph, filename):
    """
    Saves the state of the graph to a file
    
    Parameters:
        filename (string): the name of the file to save the state to
    
    Returns:
        None
    """
    '''
    path = os.path.join(SAVED_GRAPH_STATE_PATH, (filename+"pkl"))
    with open(path, 'wb') as f:
        pickle.dump(graph, f)
    print("Graph state saved to file:", path)
    '''
    path = os.path.join(SAVED_GRAPH_STATE_PATH, (filename + ".joblib"))
    joblib.dump(graph, path, compress='lz4')
    print("Graph state saved to file:", path)


#Loads the state of the graph from a file
def loadGraphState(filename):
    """
    Loads the state of the graph from a file
    
    Parameters:
        filename (string): the name of the file to load the state from
    
    Returns:
        graph (Graph): a new Graph object with the state restored from the file
    """
    '''
    path = os.path.join(SAVED_GRAPH_STATE_PATH, (filename+"pkl"))
    with open(path, 'rb') as f:
        graph = pickle.load(f)
    print("Graph state loaded from file:", path)
    return graph
    '''
    path = os.path.join(SAVED_GRAPH_STATE_PATH, (filename + ".joblib"))
    graph = joblib.load(path)
    graph.addEdgesToNodes()
    return graph



#--------------------------------------------Testing functions------------------------------------------------------------

#function to randomly update all the nodes daily change values
def updateAllNodesChange(graph):
    """
    Randomly updates all the nodes daily change values
    
    Parameters:
        graph (Graph): the graph to update the nodes on
    
    Returns:
        None
    """
    for node in graph.getNodes():
        node.setChange(random.uniform(-0.1, 0.1))



#--------------------------------------------Main------------------------------------------------------------
#check if database tables exist if not create them
def checkDBTablesExist():
    """
    Checks if the database tables exist, if not creates them
    
    Parameters:
        None
        
    Returns:
        None
    """
    #connect to DB
    conn = sqlite3.connect(DB_PATH)
    #create cursor
    c = conn.cursor()
    #check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='FTSE100'")
    if c.fetchone() == None:
        #create table
        createFTSE100DB()
    #check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='SP500'")
    if c.fetchone() == None:
        #create table
        createSP500DB()
    #check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='NASDAQ'")
    if c.fetchone() == None:
        #create table
        createNASDAQDB()
    #commit changes
    conn.commit()
    #close connection
    conn.close()


#go through all tickers in given index, create CSVs for each ticker and save to a DB
def getAllTickersAndData(index, whichTrain = 0):
    """
    Goes through all tickers in given index, creates CSVs for each ticker and saves to a DB
    
    Parameters:
        index (str): index to get tickers from
        whichTrain (int): 0 = train on all data, 1 = nth element split, 2 = split at pivot
        
    Returns:
        None
    """
    #get list of tickers
    if index == "FTSE100":
        tickers = getFTSE100Data()
    elif index == "SP500":
        tickers = getSP500Data()
    elif index == "NASDAQ":
        tickers = getNASDAQData()
    else:
        print("Invalid index")
        return None
    #go through each element in tickers
    for ticker in tickers:
        print("\n\n")
        #get ticker data
        data = getTickerData4(ticker["symbol"])
        #check if data is none, if so try a different ticker
        if len(data["Time Series (Daily)"]) == 0:
            #get new ticker data and retry
            newTicker = getCorrectTicker(ticker["symbols"], index)
            data = getTickerData4(newTicker)
        #ensure that there is available data for the ticker
        if len(data["Time Series (Daily)"]) != 0:
            #IF DATA IS NOT NONE MAKE CSV AND ADD TO DB
            #create csv file
            if whichTrain == 0:
                createCSV(ticker["symbol"], data["Time Series (Daily)"], index)
            elif whichTrain == 1:
                createTrainTestCSVsEveryN(ticker["symbol"], data["Time Series (Daily)"], index)
            elif whichTrain == 2:
                createTrainTestCSVsSplit(ticker["symbol"], data["Time Series (Daily)"], index)

            #add to DB
            #=================================ANSWER=================================
            #industries needs to be converted into a string and back into a list
            print(f"index: {index}, name: {type(ticker['name'])}, symbol: {type(ticker['symbol'])}, industries: {type(ticker['industries'])}, csv: {type(ticker['symbol'] + '.csv')}")
            addToDB(index, ticker["name"], ticker["symbol"], ticker["industries"], ticker["symbol"] + ".csv")
        #if no data print error
        else:
            print("No data for ticker: ", ticker["symbol"])


#go through data and extract alternate ticker
def getCorrectTicker(tickerData, index):
    """
    Goes through data and extracts alternate ticker

    Parameters:
        tickerData (list): data from the ticker
        index (str): index to get tickers from

    Returns:
        ticker (str): returns the correct ticker
    """
    for i in tickerData:
        if index == "FTSE100":
            if i["currency"] == "GBP":
                ticker = i["yahoo"]
        elif index == "SP500":
            if i["currency"] == "USD":
                ticker = i["yahoo"]
        elif index == "NASDAQ":
            if i["currency"] == "USD":
                ticker = i["yahoo"]
    return ticker


#main function - does all necessary operations
def main():
    """
    Main function - does all necessary operations

    Parameters:
        None

    Returns:
        None
    """
    #check DB tables exists
    checkDBTablesExist()

    #fills tables if they are empty
    if checkTableContent("FTSE100") == 0:
        getAllTickersAndData("FTSE100")
    if checkTableContent("SP500") == 0:
        getAllTickersAndData("SP500")
    if checkTableContent("NASDAQ") == 0:
        getAllTickersAndData("NASDAQ")

    

    refreshTables = input("Would you like to refresh the financial Data (y/n): ").lower()
    if refreshTables == "y":
        #empty tables
        delTableContents("FTSE100")
        delTableContents("SP500")
        delTableContents("NASDAQ")
        #delete CSV files
        deleteCSVFiles("FTSE100")
        deleteCSVFiles("SP500")
        deleteCSVFiles("NASDAQ")
        #Fill the database with data and get CSV data
        getAllTickersAndData("FTSE100")
        getAllTickersAndData("SP500")
        getAllTickersAndData("NASDAQ")


    #training y/n
    trainingFitness = input("Would you like to train the network (y/n): ").lower()
    if trainingFitness == "y":
        whichTrain = input("Which training method would you like to use (0 = train on all data, 1 = nth element split, 2 = split at pivot): ")
        delTableContents("FTSE100")
        delTableContents("SP500")
        delTableContents("NASDAQ")
        #delete CSV files
        deleteCSVFiles("FTSE100")
        deleteCSVFiles("SP500")
        deleteCSVFiles("NASDAQ")
        if whichTrain == "1":
            getAllTickersAndData("FTSE100", 1)
            getAllTickersAndData("SP500", 1)
            getAllTickersAndData("NASDAQ", 1)
        elif whichTrain == "2":
            getAllTickersAndData("FTSE100", 2)
            getAllTickersAndData("SP500", 2)
            getAllTickersAndData("NASDAQ", 2)

        #which index to train on
        whichIndex = input("Which index would you like to train on (1 = FTSE100,2 = SP500,3 = NASDAQ): ")
        if whichIndex == "1":
            index = "FTSE100"
        elif whichIndex == "2":
            index = "SP500"
        elif whichIndex == "3":
            index = "NASDAQ"
        else:
            print("Invalid index")
            return None
        
        #get tickers from DB
        tickers = getListOfTickersFromDB(index)
        #run fitness function


#INPUT  - refreshData - boolean to refresh data or not
#INPUT  - splitMethod - which split method to use 1 = nth element split, 2 = split at pivot
#OUTPUT - refreshData - boolean to refresh data or not
def EvalNetwork(refreshData, splitMethod):  
    """
    Evaluates the network, comparing the predicted values to the actual values, goes through each index and each heuristic combination

    Parameters:
        refreshData (bool): boolean to refresh data or not
        splitMethod (int): which split method to use 1 = nth element split, 2 = split at pivot

    Returns:
        None
    """ 
    #check DB tables exists
    checkDBTablesExist()
    #create dictionary of fitnesse evals
    evaledFitnesses = {}
    if splitMethod == 1:
        SM = "nth element split"
    elif splitMethod == 2:
        SM = "split at pivot"
    
    #refresh data if needs be
    if refreshData == True:         
        delTableContents("FTSE100")
        delTableContents("SP500")
        delTableContents("NASDAQ")
        #delete CSV files
        deleteCSVFiles("FTSE100")
        deleteCSVFiles("SP500")
        deleteCSVFiles("NASDAQ")
        #Fill the database with data and get CSV data
        getAllTickersAndData("FTSE100", splitMethod)
        getAllTickersAndData("SP500", splitMethod)
        getAllTickersAndData("NASDAQ", splitMethod)
    
    indices = ["FTSE100", "SP500", "NASDAQ"]
    #indices = ["NASDAQ"]
    #heuristics = [i for i in range(1, 8)]
    heuristics = [1]
    #run fitness checker for heuristic 1

    for index in indices:
        for heuristic in heuristics:
            print(f"running fitness function for {index} and heuristic {heuristic}")
            h1Fitnesses = runAllFitness1(getListOfTickersFromDB(index), index, heuristic)
            evaledH1Fitnesses = evalNetworkData(h1Fitnesses)
            evaledFitnesses[SM + " " + index + " " + str(heuristic)] = evaledH1Fitnesses
            print(f"average variation from trimmed dataset: {evaledH1Fitnesses['averageVariationTrimmed']}")
            print(f"ratio of statistically relevant data: {evaledH1Fitnesses['ratioOfStatisticallyRelevant']}")
            print(f"ratio of incorrect assessments: {evaledH1Fitnesses['ratioOfIncorrectAssessments']}")

    for key, values in evaledFitnesses.items():
        print(f"key: {key}")
        print(f"average variation from trimmed dataset: {values['averageVariationTrimmed']}")
        print(f"ratio of statistically relevant data: {values['ratioOfStatisticallyRelevant']}")
        print(f"ratio of incorrect assessments: {values['ratioOfIncorrectAssessments']}")
        print("\n\n")

    # Open a text file in write mode
    with open('evalFitnesses'+str(splitMethod)+'.txt', 'w') as f:
        # Write the dictionary to the file using json.dump
        json.dump(evaledFitnesses, f)


#function that derives all important data from a configurations fitnesses
def evalNetworkData(fitnesses):
    """
    function that derives all important data from a configurations fitnesses

    Parameters:
        fitnesses (list): fitnesses of a configuration

    Returns:
        dictionary: containing important information - averageVariationTrimmed, ratioOfStatisticallyRelevant, ratioOfIncorrectAssessments, noOfincompatibleDatasets, noOfNaNs
    """
    h1FitnessesTrimmed = []
    noOfOppositePolarities = 0
    noOfNonCollatoryValues = 0
    noOfIncompatibleDatasets = 0
    noOfNaNs = 0
    for i in fitnesses:
        if i[1] == 10000000:
            noOfNonCollatoryValues += 1
        elif i[1] == 20000000:
            noOfOppositePolarities += 1
        elif i[1] == 30000000:
            noOfIncompatibleDatasets += 1
        #check if i[1] is nan
        elif np.isnan(i[1]):
            noOfNaNs += 1
        if i[1] < 2000 and i[1] > -2000:
            h1FitnessesTrimmed.append(i)
    averageVariationTrimmed = 0
    for i in h1FitnessesTrimmed:
        averageVariationTrimmed += i[1]
    print(f"fitnesses: {fitnesses}")
    print(f"trimmed fitnesses: {h1FitnessesTrimmed}")
    print(f"length of fitnesses: {len(fitnesses)}")
    print(f"length of trimmed fitnesses: {len(h1FitnessesTrimmed)}")
    averageVariationTrimmed = averageVariationTrimmed / len(h1FitnessesTrimmed)
    ratioOfStatisticallyRelevant = len(h1FitnessesTrimmed)/(len(fitnesses) - noOfNonCollatoryValues - noOfIncompatibleDatasets)
    ratioOfIncorrectAssessments = noOfOppositePolarities / len(fitnesses)
    #return dictionary of results
    return {"averageVariationTrimmed": averageVariationTrimmed, "ratioOfStatisticallyRelevant": ratioOfStatisticallyRelevant, "ratioOfIncorrectAssessments": ratioOfIncorrectAssessments, "noOfincompatibleDatasets": noOfIncompatibleDatasets, "noOfNaNs": noOfNaNs}

    #CHECK RETURN DATA STUFF
    #these two functions need testing
    
    #readCSV


#create a number of trained graphs
def createSavedGraphs(indices, heuristics, threshold = 0):
    """
    Creates a number of graphs and saves them to file
    
    Parameters:
        indices (list): list of indices to create graphs for
        heuristics (list): list of heuristics to create graphs for
        
    Returns:
        None
    """
    #go througb provided indices
    for index in indices:
        #go through provided heuristics
        for heuristic in heuristics:
            #create graph object
            graph = Graph(str(index))
            #populate graph with nodes
            tickerList = getListOfTickersFromDB(index)
            graph.populateGraph(index, tickerList)
            graph.createEdges(threshold, heuristic)
            #save graph
            saveGraphState(graph, str(index)+str(heuristic))
            print(f"saved graph for {index} and heuristic {heuristic}")


#gets the name of a heuristic from its correlating number
def getHeuristicName(h):
    """
    Returns the name of a heuristic given its number

    Parameters:
        h (int): heuristic number
    
    Returns:
        name (string): name of heuristic
    """
    name = ""
    if h == 1:
        name = " - Polarity Ratio"
    elif h == 2:
        name = " - Cumulative Increment (First Day Onwards)"
    elif h == 3:
        name = " - Cumulative Increment (Second Day Onwards)"
    elif h == 4:
        name = " - Pearson Correlation (Raw Data)"
    elif h == 5:
        name = " - Spearman Correlation (Raw Data)"
    elif h == 6:
        name = " - Pearson Correlation (Polarity Lists)"
    elif h == 7:
        name = " - Spearman Correlation (Polarity Lists)"
    return f"{name} Heuristic"


#returns the name of an industry selected by the user from an index
def selectIndustry (index):
    """
    Returns the name of an industry selected by the user

    Parameters:
        index (string): name of index
    
    Returns:
        subGraphBool (bool): whether or not to create a subgraph
        industryTickers (list): list of industry tickers

    """
    specifyIndustry = input("Would you like to specify an industry? (y/n): ")
    if specifyIndustry.lower() == "y":
        #get list of industries
        industries = getIndexIndustries(index)
        #print list of industries
        i = 1
        tuples = []
        print("No.   Industry.            Appearance Rate")
        for key, value in industries.items():
            print(f"{i}.  {key}. {value}")
            tuples.append((i, key, value))
            i += 1
        #get user input
        industry = input("Select an industry: ")
        #check if input is valid
        while not industry.isdigit() or int(industry) < 1 or int(industry) > len(industries):
            industry = input("Invalid input. Select an industry: ")
        #get list of tickers corresponding to that industry
        tickers = getIndustryTickers(index, tuples[int(industry)-1][1])
        #return industry
        return True, tickers
    else:
        return False, []


def getIndustryName(index):
    '''
    Returns the name of an industry selected by the user

    Parameters:
        index (string): name of index
    
    Returns:
        industryName (string): name of industry
    '''
    pass
    industries = getIndexIndustries(index)
    tuples = []
    i = 1
    print("No.   Industry.            Appearance Rate")
    for key, value in industries.items():
        print(f"{i}.  {key}. {value}")
        tuples.append((i, key, value))
        i += 1
    industry = input("Select an industry: ")
    #check if input is valid
    while not industry.isdigit() or int(industry) < 1 or int(industry) > len(industries):
        industry = input("Invalid input. Select an industry: ")
    return tuples[int(industry)-1][1]


