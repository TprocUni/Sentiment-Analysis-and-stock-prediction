#SA to actual movement predictions


import pandas as pd
from Get_financial_data_MAIN import getTickerData4, getFTSE100Data, getNASDAQData
import sqlite3
import os
from datetime import datetime, timedelta



DB_PATH = os.path.join(r"D:\Users\ted\OneDrive\Documents\Computer_science\dissertation\FinalPythonCode\DB\data.db")


#get prediction from spreadsheet
def getArticles():
    #get data from spreadsheet
    # Read data from a .csv file
    filePath = 'exported_data_updated2Final-newCreatedByProgram.xlsx'
    dataFrame = pd.read_excel(filePath, engine='openpyxl')

    # Convert the data frame to a list of lists
    articleList = dataFrame.values.tolist()

    return articleList
    #print(articleList[0])
    # Read data from an .xlsx file
    # file_path = 'your_spreadsheet_file.xlsx'
    # data_frame = pd.read_excel(file_path)

#get ticker from database using name
def getTickerFromDB(companyName):
    #try FTSE100
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT ticker FROM FTSE100 WHERE name = ?", (companyName,))
    ticker = c.fetchone()
    if ticker is None:
        #try NASDAQ
        c.execute("SELECT ticker FROM NASDAQ WHERE name = ?", (companyName,))
        ticker = c.fetchone()
    return ticker[0]


#get actual movement for that day from get_financial_data_MAIN.py
def getFinDataForTicker(article, ticker):
    #name is i[1], date is i[2]
    date = article[2]
    print(date)

 # convert string to datetime object#making the second date
    date2 = datetime.strptime(date, '%Y-%m-%d')
    # increment date by one day
    nextDay = date2 + timedelta(days=1)
    # convert to string in the same format
    nextDayStr = datetime.strftime(nextDay, '%Y-%m-%d')

    print(nextDayStr) 

    print(f"ticker is: {ticker}")
    deData = getTickerData4(ticker, date, nextDayStr)
    if deData["Time Series (Daily)"] == {}:
            ticker = ticker+".L"
            print("trying ticker with .L")
            deData = getTickerData4(ticker, date, nextDayStr)
    if deData["Time Series (Daily)"] == {}:
            return "Error"
    print(deData)
    dailyChange = deData["Time Series (Daily)"][date]["4. close"] - deData["Time Series (Daily)"][date]["1. open"]
    print(dailyChange)
    return dailyChange


#compare prediction to actual movement, see if magnitude is the same, technique is is the column number of the prediction, 8-15
def comparePredictionToActual(article, ticker, technique = 8, threshold = 0):
    #get prediction [7-15]
    prediction = article[technique]
    #get actual movement
    actual = getFinDataForTicker(article, ticker)
    if actual == "Error":
        return 0
    #compare magnitude
    #1 is true positive, 2 is true negative, 3 is false positive, 4 is false negative
    outcome = compare_floats(prediction, actual, threshold)
    return outcome
    

#a is prediction, b is actual
def compare_floats(a, b, t = 0):
    print(f"a: {a}, b: {b}")
    if (a <= t and a >= t*-1):
        return 5  # Neutral
    elif a > t and b > 0:
        return 1  # True Positive
    elif a < t and b > 0:
        return 2  # False Positive
    elif a < t and b < 0:
        return 3  # True Negative
    elif a > t and b < 0:
        return 4  # False Negative
    #neutral assessment
    else:
        return 0

#record true positive, true negative, false positive, false negative,
#show as a pie chart

def diagnostics(accuracy):
    print(accuracy)
    print(f"number of true positives: {accuracy.count(1)}")
    print(f"number of false positives: {accuracy.count(2)}")
    print(f"number of true negatives: {accuracy.count(3)}")
    print(f"number of false negatives: {accuracy.count(4)}")
    print(f"number of neutral assessments: {accuracy.count(5)}")
    print(f"number of invalid predictions: {accuracy.count(0)}")



import matplotlib.pyplot as plt
from collections import Counter

def makepies(data1, data2, data3, data4):
    # Count occurrences of each number in the data
    print("making the pies")
    counter1 = Counter(data1)
    counter2 = Counter(data2)
    counter3 = Counter(data3)
    counter4 = Counter(data4)

    def compute_accuracy(counter):
        tp = counter[1]
        tn = counter[3]
        fp = counter[2]
        fn = counter[4]
        return (tp + tn) / (tp + tn + fp + fn)

    # Compute accuracy for each dataset
    accuracy1 = compute_accuracy(counter1)
    accuracy2 = compute_accuracy(counter2)
    accuracy3 = compute_accuracy(counter3)
    accuracy4 = compute_accuracy(counter4)

    # Create a 1x4 grid of subplots
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))

    # Function to plot pie chart with counts
    def plot_pie_chart(ax, counter, title, accuracy):
        labels = list(counter.keys())
        sizes = list(counter.values())
        colors = [plt.cm.tab10(i/4) for i in labels]
        ax.pie(sizes, labels=None, colors=colors, autopct=None)
        ax.set_title(title)
        ax.text(0, 0, f'Accuracy: {accuracy:.2%}', ha='center', va='center', fontsize=12)

    # Plot pie charts
    plot_pie_chart(axs[0], counter1, 'FTSE100 - 2018 April 03-09', accuracy1)
    plot_pie_chart(axs[1], counter2, 'NASDAQ - 2018 April 03-09', accuracy2)
    plot_pie_chart(axs[2], counter3, 'FTSE100 - 2020 January 13-19', accuracy3)
    plot_pie_chart(axs[3], counter4, 'NASDAQ - 2020 January 13-19', accuracy4)

    # Create a custom legend for all pie charts
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='0: Unavailable Financial Data', markerfacecolor=plt.cm.tab10(0/4), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='1: True Positive', markerfacecolor=plt.cm.tab10(1/4), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='2: False Positive', markerfacecolor=plt.cm.tab10(2/4), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='3: True Negative', markerfacecolor=plt.cm.tab10(3/4), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='4: False Negative', markerfacecolor=plt.cm.tab10(4/4), markersize=10),
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.95, 0.95), title='Categories')

    fig.suptitle("Accuracy of Sentiment Analysis on Single Stocks", fontsize=16)
   
    # Adjust layout to make room for the shared legend
    fig.subplots_adjust(top=0.8)

    # Display the plot
    plt.show()














a = getArticles()

accuracyF18 = []
accuracyN18 = []
accuracyF20 = []
accuracyN20 = []


tickerListFTSE = getFTSE100Data()
tickerListNASDAQ = getNASDAQData()  

symbolsFTSE = [d['symbol'] for d in tickerListFTSE]

symbolsNASDAQ = [d['symbol'] for d in tickerListNASDAQ]

input("err")

for i in a:
    ticker = getTickerFromDB(i[1])
    prediction = comparePredictionToActual(i, ticker, 8)
    if ticker in symbolsFTSE:
        if i[2][:4] == "2018":

            accuracyF18.append(prediction)
        else:
            accuracyF20.append(prediction)
    elif ticker in symbolsNASDAQ:
        if i[2][:4] == "2018":
            accuracyN18.append(prediction)
        else:
            accuracyN20.append(prediction)
    print("------------------------------------------what da hell------------------------------------------")

diagnostics(accuracyF18)
diagnostics(accuracyN18)
diagnostics(accuracyF20)
diagnostics(accuracyN20)    


makepies(accuracyF18, accuracyN18, accuracyF20, accuracyN20)









def getData(threshold, hChoice):
    a = getArticles()

    accuracyF18 = []
    accuracyN18 = []
    accuracyF20 = []
    accuracyN20 = []


    tickerListFTSE = getFTSE100Data()
    tickerListNASDAQ = getNASDAQData()  

    symbolsFTSE = [d['symbol'] for d in tickerListFTSE]

    symbolsNASDAQ = [d['symbol'] for d in tickerListNASDAQ]

    for i in a:
        ticker = getTickerFromDB(i[1])
        prediction = comparePredictionToActual(i, ticker, hChoice, threshold)
        if ticker in symbolsFTSE:
            if i[2][:4] == "2018":

                accuracyF18.append(prediction)
            else:
                accuracyF20.append(prediction)
        elif ticker in symbolsNASDAQ:
            if i[2][:4] == "2018":
                accuracyN18.append(prediction)
            else:
                accuracyN20.append(prediction)
        print("------------------------------------------what da hell------------------------------------------")

    diagnostics(accuracyF18)
    diagnostics(accuracyN18)
    diagnostics(accuracyF20)
    diagnostics(accuracyN20)    

    return accuracyF18, accuracyN18, accuracyF20, accuracyN20








#;asnlaskblakhsb
def MakeAveragedPiesWithThresholds(data1, data2, data3, data4, thresholds):
    counter1 = Counter(data1)
    counter2 = Counter(data2)
    counter3 = Counter(data3)
    counter4 = Counter(data4)

    def compute_accuracy(counter):
        tp = counter[1]
        tn = counter[3]
        fp = counter[2]
        fn = counter[4]
        na = counter[5]
        print(f"tp: {tp}, tn: {tn}, fp: {fp}, fn: {fn}, na: {na}")
        return (tp + tn) / (tp + tn + fp + fn)
    
    #average results across all databases

    # Compute accuracy for each dataset
    accuracy1 = compute_accuracy(counter1)
    input("accuracys 1")
    accuracy2 = compute_accuracy(counter2)
    accuracy3 = compute_accuracy(counter3)
    accuracy4 = compute_accuracy(counter4)

    # Create a 1x4 grid of subplots
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))

    # Function to plot pie chart with counts
    def plot_pie_chart(ax, counter, title, accuracy):
        labels = [0, 1, 2, 3, 4, 5]  # include all categories
        sizes = [counter.get(label, 0) for label in labels]  # get count for each category, default to 0 if not present
        colors = [plt.cm.tab10(i/5) for i in labels]

        # Add counts to the segments
        def autopct_format(values):
            def my_format(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return '{v:d}'.format(v=val)
            return my_format

        ax.pie(sizes, labels=None, colors=colors, autopct=autopct_format(sizes))
        ax.set_title(title)
        ax.text(0, 0, f'Accuracy: {accuracy:.2%}', ha='center', va='center', fontsize=12)



    # Plot pie charts
    plot_pie_chart(axs[0], counter1, f'Averaged across all training sets,\n Threshold = {thresholds[0]}', accuracy1)
    plot_pie_chart(axs[1], counter2, f'Averaged across all training sets,\n Threshold = {thresholds[1]}', accuracy2)
    plot_pie_chart(axs[2], counter3, f'Averaged across all training sets,\n Threshold = {thresholds[2]}', accuracy3)
    plot_pie_chart(axs[3], counter4, f'Averaged across all training sets,\n Threshold = {thresholds[3]}', accuracy4)

    # Create a custom legend for all pie charts
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='0: Unavailable Financial Data', markerfacecolor=plt.cm.tab10(0/5), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='1: True Positive', markerfacecolor=plt.cm.tab10(1/5), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='2: False Positive', markerfacecolor=plt.cm.tab10(2/5), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='3: True Negative', markerfacecolor=plt.cm.tab10(3/5), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='4: False Negative', markerfacecolor=plt.cm.tab10(4/5), markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='5: Neutral Assessment', markerfacecolor=plt.cm.tab10(5/5), markersize=10),
    ]
    fig.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(0.95, 0.95), title='Categories')

    fig.suptitle("Accuracy of Sentiment Analysis on Single Stocks", fontsize=16)
   
    # Adjust layout to make room for the shared legend
    fig.subplots_adjust(top=0.8)

    # Display the plot
    plt.show()









#h7
#thresholds = [0.01, 0.02, 0.03, 0.04]
#h9
#thresholds = [0.5,0.65,0.8,0.95]
#thresholds  = [0.1,0.2,0.3,0.4]
#h10
thresholds = [0.05,0.1,0.15,0.2]
h = 10
threshAndData = {}
for i in thresholds:
    #do 7, 9 , 10
    af18, an18, af20, an20 = getData(i, h)
    alldatas = []
    alldatas.extend(af18)
    alldatas.extend(an18)
    alldatas.extend(af20)
    alldatas.extend(an20)
    threshAndData[i] = alldatas
#average each of these sets

print(threshAndData)


MakeAveragedPiesWithThresholds(threshAndData[thresholds[0]], threshAndData[thresholds[1]], threshAndData[thresholds[2]], threshAndData[thresholds[3]], thresholds)
