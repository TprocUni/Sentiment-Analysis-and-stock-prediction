import os
import json
from Modules.Get_financial_data_MAIN import getIndustryName, getListOfTickersFromDB

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
    while True:
        choice = input('''
Please select a config option to change: 
    0. Exit
    1. Index
    2. Graph Training Heuristic
    3. Threshold
    4. Industry
    5. Sentiment Analysis Method
    6. Propagation Method
    7. Propagation Depth
''')
        #exit
        if choice == '0':
            break
        elif choice == '1':
            newIndex = input('''
Please enter the new index choice (number, anything else to cancel):
    1. NASDAQ
    2. FTSE100
    3. S&P500
''')    
            changeConfigData('INDUSTRY', '')
            if newIndex == '1':
                changeConfigData('INDEX', 'NASDAQ')
            elif newIndex == '2':
                changeConfigData('INDEX', 'FTSE100')
            elif newIndex == '3':
                changeConfigData('INDEX', 'SP500')
            else:
                print("Cancelled")
        elif choice == '2':
            graphTrainingMethod = input('''
Please enter the new graph training heuristic choice (number, anything else to cancel):
1. Polarity ratio
2. Cumulative increment method (day one onwards)
3. Cumulative increment method (day two onwards)
4. Pearson correlation coefficient (raw data)
5. Spearman correlation coefficient (raw data)
6. Pearson correlation coefficient (polarity lists)
7. Spearman correlation coefficient (polarity lists)
''')
            if graphTrainingMethod == 1 or graphTrainingMethod == 2 or graphTrainingMethod == 3 or graphTrainingMethod == 4 or graphTrainingMethod == 5 or graphTrainingMethod == 6 or graphTrainingMethod == 7:
                changeConfigData('HEURISTIC', graphTrainingMethod)
            else:
                print("Cancelled")  
        elif choice == '3':
            newThreshold = input('''
Please enter the new threshold (float between 0 and 1, anything else to cancel):
''')
            if float(newThreshold) >= 0 and float(newThreshold) <= 1:
                changeConfigData('THRESHOLD', float(newThreshold))
            else:
                print("Cancelled")
        elif choice == '4':
            #print industries
            chosenIndustry = input('''
Please select an industry (number, anything else to cancel):
    1. See industry list
    2. No industry specified
''')
            if chosenIndustry == '1':
                industry = getIndustryName(getConfigData()['INDEX'])
                changeConfigData('INDUSTRY', industry)
            else:
                industry = ""
                changeConfigData('INDUSTRY', industry)
        elif choice == "5":
            #stuff for heuristic selection
            newHeuristic = input('''
Please enter the new heuristic choice (number, anything else to cancel):
    1. VADER method 1, preprocessed
    2. VADER method 2, preprocessed
    3. NLTK VADER, preprocessed
    4. TextBlob, preprocessed
    5. VADER method 1, unprocessed
    6. VADER method 2, unprocessed
    7. NLTK VADER, unprocessed
    8. TextBlob, unprocessed
''')
            if newHeuristic == '1':
                changeConfigData('HEURISTIC', '1')
            elif newHeuristic == '2':
                changeConfigData('HEURISTIC', '2')
            elif newHeuristic == '3':
                changeConfigData('HEURISTIC', '3')
            elif newHeuristic == '4':
                changeConfigData('HEURISTIC', '4')
            elif newHeuristic == '5':
                changeConfigData('HEURISTIC', '5')
            elif newHeuristic == '6':
                changeConfigData('HEURISTIC', '6')
            elif newHeuristic == '7':
                changeConfigData('HEURISTIC', '7')
            elif newHeuristic == '8':
                changeConfigData('HEURISTIC', '8')
            else:
                print("Cancelled")
        elif choice == "6":
            propMethod = input('''
Please enter the new propagation method choice (number, anything else to cancel):
1. Greatest Propagation value
2. Average Propagation value
3. First Propagation value
''')
            if propMethod == '1':
                changeConfigData('PROPAGATION_METHOD', '1')
            elif propMethod == '2':
                changeConfigData('PROPAGATION_METHOD', '2')
            elif propMethod == '3':
                changeConfigData('PROPAGATION_METHOD', '3')
            else:
                print("Cancelled")
        elif choice == "7":
            propDepth = input('''
Please enter the new propagation depth (integer value - recommended 3 or less, 0 means no propagation, anything else to cancel):
''')        
            if int(propDepth) >= 0:
                changeConfigData('PROPAGATION_DEPTH', int(propDepth))
            else:
                print("Cancelled")

if __name__ == '__main__':
    main()
            
