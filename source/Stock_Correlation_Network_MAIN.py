#Stock_Correlation_Network
from Modules.Get_financial_data_MAIN import Graph, Node, Edge, loadGraphState, getHeuristicName, getIndustryTickers, getListOfTickersFromDB, findTickerFromName
import json
import os
import subprocess
import requests
import time
import plotly.graph_objects as go
import networkx as nx
from plotly.subplots import make_subplots

INDEXCHANGE = False

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


#Check if config data has changed
def checkConfigData(currentConfigData):
    '''
    Checks if the config data has changed
    
    Parameters:
        currentConfigData (dict): the current config data

    Returns:
        bool: whether the config data has changed
    '''
    global INDEXCHANGE
    configData = getConfigData()
    print(f"current thresh: {currentConfigData['THRESHOLD']}")
    print(f"new thresh: {configData['THRESHOLD']}")
    if configData != currentConfigData:
        #needs to refresh
        print("needs a refresh----------------------------------------")
        if configData["INDEX"] != currentConfigData["INDEX"] or configData["HEURISTIC"] != currentConfigData["HEURISTIC"]:
            INDEXCHANGE = True
        return True
    else:
        return False


#main
def main():
    #get config data
    configData = getConfigData()
    INDEX = configData["INDEX"]
    HEURISTIC = configData["HEURISTIC"]
    SERVER_IP = configData["SERVER_IP"]
    THRESHOLD = configData["THRESHOLD"]
    INDUSTRY = configData["INDUSTRY"]
    SA_DATA = configData["CURRENT_ARTICLE"]
    PROPAGATION_METHOD = configData["PROPAGATION_METHOD"]
    PROPAGATION_DEPTH = configData["PROPAGATION_DEPTH"]
    global INDEXCHANGE
    #INDEXCHANGE = False

    #launch the server
    flaskServerPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Modules\\flask_server.py')
    flaskServerDir = os.path.dirname(flaskServerPath)
    server_process = subprocess.Popen(['python', flaskServerPath], cwd=flaskServerDir)


    #generate initial graph object
    graph = Graph(INDEX)
    graph = loadGraphState(INDEX+HEURISTIC)
    heuristicName = getHeuristicName(int(HEURISTIC))
    #get list of tickers
    tickers = getListOfTickersFromDB(INDEX)
    graph.generateSubGraph(True, tickers, THRESHOLD)
    graphObj = graph.createPlotlyGraph(THRESHOLD, heuristicName)
    graphJson = json.loads(graphObj.to_json())
    #send graph to server
    response = requests.post(SERVER_IP+'update-graph', json=graphJson)
    #print server IP
    print(f"SERVER IP: {SERVER_IP}")
    #run live graph
    while True:
        refresh = checkConfigData(configData)
        if refresh == True:
            #get new config data
            configData = getConfigData()
            INDEX = configData["INDEX"]
            HEURISTIC = configData["HEURISTIC"]
            SERVER_IP = configData["SERVER_IP"]
            THRESHOLD = configData["THRESHOLD"]
            INDUSTRY = configData["INDUSTRY"]
            SA_DATA = configData["CURRENT_ARTICLE"]
            PROPAGATION_METHOD = configData["PROPAGATION_METHOD"]
            PROPAGATION_DEPTH = configData["PROPAGATION_DEPTH"]
            #get heuristic name
            heuristicName = getHeuristicName(int(HEURISTIC))
            #check if index has changed
            if INDEXCHANGE == True:
                print(f"INDEX: {INDEX}, HEURISTIC: {HEURISTIC}")
                graph = loadGraphState(INDEX+HEURISTIC)
                INDEXCHANGE = False
            #check if user wants a subgraph
            if INDUSTRY != "":
                #get industry specific tickers
                industryTickers = getIndustryTickers(INDEX, INDUSTRY)
            else:
                industryTickers = getListOfTickersFromDB(INDEX)


            #check for SA changes here - if there are changes, apply them to the graph
            try:
                if SA_DATA[3] == False:

                    #check for change in SA part

                    #get node ticker
                    nodeName = SA_DATA[1]
                    #get node object with matching name
                    nodeTicker = findTickerFromName(nodeName, INDEX)
                    #if change, apply to the graph

                    #apply propagation
                    if PROPAGATION_METHOD == 1:
                        graph.POPropagation1(PROPAGATION_DEPTH, nodeTicker, SA_DATA[2], THRESHOLD)
                    elif PROPAGATION_METHOD == 2:
                        graph.POPropagation2(PROPAGATION_DEPTH, nodeTicker, SA_DATA[2], THRESHOLD)
                    elif PROPAGATION_METHOD == 3:
                        graph.POPropagation3(PROPAGATION_DEPTH, nodeTicker, SA_DATA[2], THRESHOLD)
                    else:
                        print("Invalid Propagation Method")

                    #update config
                    changeConfigData("CURRENT_ARTICLE", [SA_DATA[0], SA_DATA[1], SA_DATA[2], True])
            except:
                pass

            graph.generateSubGraph(True, industryTickers, THRESHOLD)
            #get heuristic name
            #regenerate graph object
            graphObj = graph.createPlotlyGraph(THRESHOLD, heuristicName)

            #convert graph to json
            graphJson = json.loads(graphObj.to_json())
            #send graph to server
            response = requests.post(SERVER_IP+'update-graph', json=graphJson)
                # Check if the request was successful
            if response.status_code == 200:
                print("Sucessfully sent graph data")
            else:
                print("Error sending graph data")
                print(response.content)
    
        #check fir new data look at config file
        #apply SA to new data
        #put sentiment score into the network
        #regularly check for new data, and update graph

        #in SCN
        #add checker for sentiment analysis data
        #if there is update apply it to graph
        #apply propagation method 0 = none to 3 
        #push to config that it has been applied







        time.sleep(10)


#getConfigData()
#changeConfigData("THRESHOLD", 0.4)
main()