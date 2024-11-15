#Final results
import pandas as pd
from Modules.Get_financial_data_MAIN import Graph, Node, Edge, loadGraphState, getListOfTickersFromDB, getTickerData4
from datetime import datetime
import sqlite3
from datetime import timedelta



def get_names_from_table(table_name):
    conn = sqlite3.connect(r"D:\Users\ted\OneDrive\Documents\Computer_science\dissertation\FinalPythonCode\DB\data.db")
    cursor = conn.cursor()
    query = f"SELECT name FROM {table_name}"
    cursor.execute(query)
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names



def get_names_and_tickers_from_table(table_name):
    conn = sqlite3.connect(r"D:\Users\ted\OneDrive\Documents\Computer_science\dissertation\FinalPythonCode\DB\data.db")
    cursor = conn.cursor()
    query = f"SELECT name, ticker FROM {table_name}"
    cursor.execute(query)
    name_ticker_mapping = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return name_ticker_mapping



def printRows(data1):
    # Iterate through the rows of the DataFrame
    for index, row in data1.iterrows():
        # Access data using the column names
        print(f"Row {index}:")
        print(f"Column 1: {row[1]}")
        print(f"Column 2: {row[2]}")
        print(f"Column 3: {row[3]}")
        #print(f"Column 4: {row[4]}")
        print(f"Column 5: {row[5]}")
        print(f"Column 6: {row[6]}")
        print(f"Column 7: {row[7]}")
        print(f"Column 8: {row[8]}")
        print(f"Column 9: {row[9]}")
        print(f"Column 10: {row[10]}")
        print("\n")



nasdaq_name_ticker_mapping = get_names_and_tickers_from_table("Nasdaq")
ftse100_name_ticker_mapping = get_names_and_tickers_from_table("FTSE100")


HEURISTIC = 1
INDEX = "NASDAQ"
INDEX2 = "FTSE100"
threshold = 0.25
#get the article data from the excel spreadsheet
file_path = r"D:\Users\ted\OneDrive\Documents\Computer_science\dissertation\exported_data_updated2Final-newCreatedByProgram.xlsx"
# Read the Excel file
# Read the Excel file without headers and parse the dates in column 2 using the custom date parser
data = pd.read_excel(file_path, header=None, parse_dates=[2], date_format="%Y-%m-%d")

# Print the first few rows of the DataFrame

#get industry tickers
tickersN = getListOfTickersFromDB(INDEX)
tickersF = getListOfTickersFromDB(INDEX2)
#load graph from file - NASDAQ
GN = loadGraphState(INDEX+str(HEURISTIC))
GN.generateSubGraph(True, tickersN, threshold)
graphObj = GN.createPlotlyGraph(threshold, INDEX+str(HEURISTIC))
#graphObj.show()

#load graph from file - FTSE100
GF = loadGraphState(INDEX2+str(HEURISTIC))
GF.generateSubGraph(True, tickersF, threshold)
graphObj2 = GF.createPlotlyGraph(threshold, INDEX2+str(HEURISTIC))


#split data according to year

# Split the data based on the year in column 2
data_2018 = data[data[2].dt.year == 2018]
data_2020 = data[data[2].dt.year == 2020]

# Print the first few rows of each DataFrame







# Get the names from the "Nasdaq" and "FTSE100" tables in the database
nasdaq_names = get_names_from_table("Nasdaq")
ftse100_names = get_names_from_table("FTSE100")



# Filter the data_2018 and data_2020 DataFrames based on the names
data_2018_nasdaq = data_2018[data_2018[1].isin(nasdaq_names)]
data_2018_ftse100 = data_2018[data_2018[1].isin(ftse100_names)]
data_2020_nasdaq = data_2020[data_2020[1].isin(nasdaq_names)]
data_2020_ftse100 = data_2020[data_2020[1].isin(ftse100_names)]


data_2018_nasdaq[1] = data_2018_nasdaq[1].map(nasdaq_name_ticker_mapping)
data_2018_ftse100[1] = data_2018_ftse100[1].map(ftse100_name_ticker_mapping)
data_2020_nasdaq[1] = data_2020_nasdaq[1].map(nasdaq_name_ticker_mapping)
data_2020_ftse100[1] = data_2020_ftse100[1].map(ftse100_name_ticker_mapping)


# Sort the DataFrames by date
data_2018_nasdaq = data_2018_nasdaq.sort_values(by=2)
data_2018_ftse100 = data_2018_ftse100.sort_values(by=2)
data_2020_nasdaq = data_2020_nasdaq.sort_values(by=2)
data_2020_ftse100 = data_2020_ftse100.sort_values(by=2)




#split the excel file data into date specific datasets based on NASDAQ and FTSE100

#go through each week dataset for the graph object, testing the different 
# propagation methods, different propagation depths, and different thresholds, different heuristics, different SA techniques

#for SA techniques, use VADER1, VADER2 or VADERNLTK
#for prop depths 0 to 3
#for prop methods 1 to 3
#for thresholds 0. to 0.8 in increments of 0.1
#for heuristics 1 to 7, need to regenerate graph

def RunSim(dataset, SAM, PropDepth, PropMethod, threshold, heuristic, index, tickerList, pT):
    print("starting")
    dailyAccuracys = {}
    #generate graph object
    g = loadGraphState(index+str(heuristic))
    g.generateSubGraph(True, tickerList, threshold)
    #set up data structures
    correctPredictions = 0
    totalPredictions = 0
    #deduce SAM index
    SAMIndex = 0
    if SAM == "VADER1":
        SAMIndex = 7
    elif SAM == "VADER2":
        SAMIndex = 8
    elif SAM == "VADERNLTK":
        SAMIndex = 9
    elif SAM == "TextBlob":
        SAMIndex = 10

    #go thoough each day in the dataset
    i = 0
    while i < len(dataset):
        print("-----------------------------------------------------------------------------------------------------------------------------")
        current_date = dataset.iloc[i, 2]
        daily_rows = []

        # Process all rows with the same date
        while i < len(dataset) and dataset.iloc[i, 2] == current_date:  # Use iloc instead of at
            daily_rows.append(dataset.iloc[i])
            print(dataset.iloc[i, 2])
            i += 1
            
        print(f"length of dataset: {len(dataset)}")
        print(f"i is : {i}")
        print(f"length of dailyrows: {len(daily_rows)}")

        #do stuff to the graph
        for row in daily_rows:
            print(row[1])
            print(row[SAMIndex])
            if PropMethod == 1:
                g.POPropagation1(PropDepth, row[1], row[SAMIndex], threshold)
            elif PropMethod == 2:
                g.POPropagation2(PropDepth, row[1], row[SAMIndex], threshold)
            elif PropMethod == 3:
                g.POPropagation2(PropDepth, row[1], row[SAMIndex], threshold)
            else:
                print("Invalid Propagation Method")
        #check if date is the same

        #g2= g.createPlotlyGraph(threshold, index+str(heuristic))
        #g2.show()

        #get the predictions for that day for each ticker in the graph
        #iterate through nodes in graph, storing all that have a prediction made with the ticker.
        nodeTuples = []
        for node in g.subNodes:
            if node.getChange() != 0:
                nodeTuples.append((node.getTicker(), node.getChange()))


        next_date = current_date + timedelta(days=1)
        print(f"current date: {current_date}, next date: {next_date}")
        current_date_only = str(current_date.date())

        for j in range(len(nodeTuples)):
            print(nodeTuples[j])
            #get fin data for that ticker
            try:
                currentNodeFinData = getTickerData4(nodeTuples[j][0], current_date, next_date)['Time Series (Daily)'][current_date_only]  #next dates is current Date +=1
                dailyChange = currentNodeFinData["4. close"] - currentNodeFinData["1. open"]

                #check against actual results, maybe implement a threshold
                if (nodeTuples[j][1] > pT and dailyChange > pT) or (nodeTuples[j][1] < pT and dailyChange < pT) or (nodeTuples[j][1] == 0 and dailyChange == 0):
                    correctPredictions += 1
                totalPredictions += 1
            except:
                print("no fin data for that date")
        #return accuracy
        if totalPredictions > 0:
            accuracy = correctPredictions/totalPredictions
        else:
            accuracy = 0
        dailyAccuracys[current_date_only] = (accuracy, totalPredictions)
        #make second dictionary, where we check if the initial prediction was correct, and if it was, check if the prediction was correct at the end of the day

    return dailyAccuracys



#this is the method that checks if the initial prediction was correct, and if it was, checks if the prediction was correct at the end of the day
def RunSim2(dataset, SAM, PropDepth, PropMethod, threshold, heuristic, index, tickerList, pT):
    print("starting")
    dailyAccuracys = {}
    #generate graph object
    g = loadGraphState(index+str(heuristic))
    g.generateSubGraph(True, tickerList, threshold)
    #set up data structures
    correctPredictions = 0
    totalPredictions = 0
    #deduce SAM index
    SAMIndex = 0
    if SAM == "VADER1":
        SAMIndex = 7
    elif SAM == "VADER2":
        SAMIndex = 8
    elif SAM == "VADERNLTK":
        SAMIndex = 9
    elif SAM == "TextBlob":
        SAMIndex = 10

    #go thoough each day in the dataset
    i = 0
    while i < len(dataset):
        print("-----------------------------------------------------------------------------------------------------------------------------")
        current_date = dataset.iloc[i, 2]
        daily_rows = []

        # Process all rows with the same date
        while i < len(dataset) and dataset.iloc[i, 2] == current_date:  # Use iloc instead of at
            daily_rows.append(dataset.iloc[i])
            print(dataset.iloc[i, 2])
            i += 1
            
        print(f"length of dataset: {len(dataset)}")
        print(f"i is : {i}")
        print(f"length of dailyrows: {len(daily_rows)}")

        next_date = current_date + timedelta(days=1)
        print(f"current date: {current_date}, next date: {next_date}")
        current_date_only = str(current_date.date())


        #do stuff to the graph
        for row in daily_rows:
            #check if initial prediction is correct, apply propagation of it is
            #get fin data for that ticker
            correctPredictio4Node = False
            try:
                    #get ticker for that row
                print(row[1])
                currentNodeFinData = getTickerData4(row[1], current_date, next_date)['Time Series (Daily)'][current_date_only]  #next dates is current Date +=1
                dailyChange = currentNodeFinData["4. close"] - currentNodeFinData["1. open"]
                #check against actual results, maybe implement a threshold
                if (float(row[SAMIndex]) > pT and dailyChange > pT) or (float(row[SAMIndex]) < pT and dailyChange < pT) or (float(row[SAMIndex]) == 0 and dailyChange == 0):
                    print("prediction for original node was correct")
                    correctPredictio4Node = True
                else:
                    print("original prediction was incorrect")
            except:
                print("it bugs out")
            

            if correctPredictio4Node == True: #apply propagation
                print(row[1])
                print(row[SAMIndex])
                if PropMethod == 1:
                    g.POPropagation1(PropDepth, row[1], row[SAMIndex], threshold)
                    print(f"Propmethod is: {PropMethod}")
                elif PropMethod == 2:
                    g.POPropagation2(PropDepth, row[1], row[SAMIndex], threshold)
                    print(f"Propmethod is: {PropMethod}")
                elif PropMethod == 3:
                    g.POPropagation2(PropDepth, row[1], row[SAMIndex], threshold)
                    print(f"Propmethod is: {PropMethod}")
                else:
                    print("Invalid Propagation Method")
        #check if date is the same

        #g2= g.createPlotlyGraph(threshold, index+str(heuristic))
        #g2.show()

        #get the predictions for that day for each ticker in the graph
        #iterate through nodes in graph, storing all that have a prediction made with the ticker.
        nodeTuples = []
        for node in g.subNodes:
            if node.getChange() != 0:
                nodeTuples.append((node.getTicker(), node.getChange()))




        for j in range(len(nodeTuples)):
            print(nodeTuples[j])
            #get fin data for that ticker
            try:
                currentNodeFinData = getTickerData4(nodeTuples[j][0], current_date, next_date)['Time Series (Daily)'][current_date_only]  #next dates is current Date +=1
                dailyChange = currentNodeFinData["4. close"] - currentNodeFinData["1. open"]

                #check against actual results, maybe implement a threshold
                if (nodeTuples[j][1] > 0 and dailyChange > 0) or (nodeTuples[j][1] < 0 and dailyChange < 0) or (nodeTuples[j][1] == 0 and dailyChange == 0):
                    correctPredictions += 1
                totalPredictions += 1
            except:
                print("no fin data for that date")
        #return accuracy
        if totalPredictions > 0:
            accuracy = correctPredictions/totalPredictions
        else:
            accuracy = 0
        dailyAccuracys[current_date_only] = (accuracy, totalPredictions)
        #make second dictionary, where we check if the initial prediction was correct, and if it was, check if the prediction was correct at the end of the day
    return dailyAccuracys




# propagation methods, different propagation depths, and different thresholds, different heuristics, different SA techniques

#for SA techniques, use VADER1, VADER2 or VADERNLTK
#for prop depths 0 to 3
#for prop methods 1 to 3
#for thresholds 0. to 0.8 in increments of 0.1
#for heuristics 1 to 7, need to regenerate graph

indices = ["NASDAQ", "FTSE100"]
SATechniques = ["VADER1", "VADERNLTK", "TextBlob"]
propDepths = [0, 1, 2, 3]
propMethods = [1, 2, 3]
thresholds = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
heuristics = [2, 5]
predictionThresholds = [0.05, 0.075, 0.1, 0.125, 0.15]

import csv
'''with open('testingbigThing.csv', 'w') as f:
    print("starting")
    w = csv.writer(f)
    b = RunSim(data_2018_nasdaq, "VADER1", 3, 2, 0.1, 2, "NASDAQ", tickersN, 0.1)
    w.writerow(b)
    print("done")


input("stop here")

print("bruh")
# Create csv writers for simResults1 and simResults2
with open('NASsimResults1wCount2020.csv', 'w') as f1, open('NASsimResults2wCount2020.csv', 'w') as f2, open('FTSEsimResults1wCount2020.csv', 'w') as f3, open('FTSEsimResults2wCount2020.csv', 'w') as f4, open('FTSEsimResults1wCount2018.csv', 'w') as f5, open('FTSEsimResults2wCount2018.csv', 'w') as f6, open('NASsimResults1wCount2018.csv', 'w') as f7, open('NASsimResults2wCount2018.csv', 'w') as f8:
    w1 = csv.writer(f1)
    w2 = csv.writer(f2)
    w3 = csv.writer(f3)
    w4 = csv.writer(f4)
    w5 = csv.writer(f5)
    w6 = csv.writer(f6)
    w7 = csv.writer(f7)
    w8 = csv.writer(f8)


    # Write headers to the csv files
    w1.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w2.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w3.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w4.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w5.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w6.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w7.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])
    w8.writerow(['index', 'SATechnique', 'propDepth', 'propMethod', 'threshold', 'heuristic', 'dailyAccs', 'predictionThreshold'])




    for index in indices:
        for SATechnique in SATechniques:
            for propDepth in propDepths:
                for propMethod in propMethods:
                    for threshold in thresholds:
                        for heuristic in heuristics:
                            for predictionThreshold in predictionThresholds:
                                print(f"Index: {index}, SA Technique: {SATechnique}, Prop Depth: {propDepth}, Prop Method: {propMethod}, Threshold: {threshold}, Heuristic: {heuristic}, predictionThreshold: {predictionThreshold}")


                                #NASDAQ2018
                                # Run RunSim and write the results to simResults1.csv
                                dailyAccs = RunSim(data_2018_nasdaq, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w1.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])

                                # Run RunSim2 and write the results to simResults2.csv
                                dailyAccs2 = RunSim2(data_2018_nasdaq, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w2.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs2])



                                #2020NADDAQ

                                # Run RunSim and write the results to simResults1.csv
                                dailyAccs = RunSim(data_2020_nasdaq, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w1.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])

                                # Run RunSim2 and write the results to simResults2.csv
                                dailyAccs2 = RunSim2(data_2020_nasdaq, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w2.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs2])


                                #2018FTSE

                                # Run RunSim and write the results to simResults1.csv
                                dailyAccs = RunSim(data_2018_ftse100, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w1.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])

                                # Run RunSim2 and write the results to simResults2.csv
                                dailyAccs2 = RunSim2(data_2018_ftse100, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w2.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs2])


                                #2020FTSE

                                # Run RunSim and write the results to simResults1.csv
                                dailyAccs = RunSim(data_2020_ftse100, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w1.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])

                                # Run RunSim2 and write the results to simResults2.csv
                                dailyAccs2 = RunSim2(data_2020_ftse100, SATechnique, propDepth, propMethod, threshold, heuristic, index, tickersN, predictionThreshold)
                                w2.writerow([index, SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs2])


'''

#todo
# regenerate the data - it always dies, do it 
#split it into a few sections of writing into the same file, so it doesnt die#
import time

# Start the timer
start_time = time.time()

SATechniques = ["VADER1", "VADERNLTK", "TextBlob"]


'''print("starting")
SATechnique = "VADER1"
for propDepth in propDepths:
    with open("FINALNASDAQ2020.csv", 'a') as f:
        w = csv.writer(f)
        w = csv.writer(f)
        for propMethod in propMethods:
            for threshold in thresholds:
                for heuristic in heuristics:
                    for predictionThreshold in predictionThresholds:
                        dailyAccs = RunSim(data_2020_nasdaq, SATechnique, propDepth, propMethod, threshold, heuristic, "NASDAQ", tickersN, predictionThreshold)
                        w.writerow(["NASDAQ", SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])
                f.flush()


'''


'''print("starting")
SATechnique = "TextBlob"
for propDepth in propDepths:
    with open("FINALNASDAQ2020.csv", 'a') as f:
        w = csv.writer(f)
        for propMethod in propMethods:
            for threshold in thresholds:
                for heuristic in heuristics:
                    for predictionThreshold in predictionThresholds:
                        dailyAccs = RunSim(data_2020_nasdaq, SATechnique, propDepth, propMethod, threshold, heuristic, "NASDAQ", tickersN, predictionThreshold)
                        w.writerow(["NASDAQ", SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])
                f.flush()

'''
#ftse stuff

'''print("starting")
SATechnique = "VADER1"
for propDepth in propDepths:
    with open("FINALFTSE2018.csv", 'a') as f:
        w = csv.writer(f)
        for propMethod in propMethods:
            for threshold in thresholds:
                for heuristic in heuristics:
                    for predictionThreshold in predictionThresholds:
                        dailyAccs = RunSim(data_2018_ftse100, SATechnique, propDepth, propMethod, threshold, heuristic, "FTSE100", tickersF, predictionThreshold)
                        w.writerow(["FTSE100", SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])
                f.flush()





print("starting")
SATechnique = "TextBlob"
for propDepth in propDepths:
    with open("FINALFTSE2018.csv", 'a') as f:
        w = csv.writer(f)
        w = csv.writer(f)
        for propMethod in propMethods:
            for threshold in thresholds:
                for heuristic in heuristics:
                    for predictionThreshold in predictionThresholds:
                        dailyAccs = RunSim(data_2018_ftse100, SATechnique, propDepth, propMethod, threshold, heuristic, "FTSE100", tickersF, predictionThreshold)
                        w.writerow(["FTSE100", SATechnique, propDepth, propMethod, threshold, heuristic, predictionThreshold, dailyAccs])
                f.flush()



'''


#run best models with prop depth of 3
#save to csvFile
bestModels = [('VADER1', '2', '1', '0.1', '2', '0.15'), ('VADER1', '2', '1', '0.1', '5', '0.15'), ('TextBlob', '2', '1', '0.1', '2', '0.1'), ('VADER1', '2', '1', '0.1', '2', '0.125'), ('VADER1', '2', '1', '0.1', '5', '0.125'), ('VADER1', '2', '1', '0.1', '2', '0.1'), ('VADER1', '2', '1', '0.1', '5', '0.1'), ('TextBlob', '2', '1', '0.1', '5', '0.15'), ('VADER1', '2', '1', '0.1', '2', '0.075'), ('VADER1', '2', '1', '0.1', '5', '0.075'), ('TextBlob', '2', '1', '0.1', '2', '0.125'), ('TextBlob', '2', '1', '0.1', '5', '0.075'), ('TextBlob', '2', '1', '0.1', '5', '0.05'), ('VADER1', '2', '1', '0.1', '5', '0.05'), ('TextBlob', '2', '1', '0.1', '5', '0.125'), ('TextBlob', '1', '1', '0.3', '2', '0.1'), ('TextBlob', '1', '1', '0.0', '2', '0.1'), ('TextBlob', '1', '1', '0.1', '2', '0.1'), ('TextBlob', '1', '1', '0.2', '2', '0.1'), ('VADER1', '2', '1', '0.1', '2', '0.05'), ('TextBlob', '2', '1', '0.0', '2', '0.1'), ('VADERNLTK', '1', '2', '0.0', '2', '0.1'), ('VADERNLTK', '1', '2', '0.0', '2', '0.125'), ('VADERNLTK', '1', '3', '0.0', '2', '0.1'), ('VADERNLTK', '1', '3', '0.0', '2', '0.125')]
input("starting")
#write to CSV

for i in bestModels:
        #index,SATechnique,propDepth,propMethod,threshold,heuristic,dailyAccs,predictionThreshold
        dailyAccs = RunSim(data_2018_nasdaq, i[0], 3, int(i[2]), float(i[3]), int(i[4]), "NASDAQ", tickersN, float(i[5]))
        with open("BESTMODELS.csv", 'a') as f:
            w = csv.writer(f)
            w.writerow(["2018", "NASDAQ", i[0], 3, i[2], i[3], i[4], i[5], dailyAccs])


        dailyAccs = RunSim(data_2020_nasdaq, i[0], 3, int(i[2]), float(i[3]), int(i[4]), "NASDAQ", tickersN, float(i[5]))
        with open("BESTMODELS.csv", 'a') as f:
            w = csv.writer(f)
            w.writerow(["2020", "NASDAQ", i[0], 3, i[2], i[3], i[4], i[5], dailyAccs])
















print("done")
# Stop the timer
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time
print("Execution time: ", execution_time, " seconds")

