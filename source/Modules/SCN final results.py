#SCN final results
import csv
from matplotlib import pyplot as plt
import ast



#get data from csv files

#make function to get n best models, based off of the average accuracyof each week - or each combo of hyperparameter for all 4 sets of data
#make a dict of values, where the key is the combination of hyperparams, and the value is the average accuracy across all 4 sets of data

#reads file
def readFile(path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data[1:]


#removes all dictionary dates where data is repeated due to weekend circumstances
def removesRepeatDates(data):
    newData = []
    for row in data:
        if row == []:
            pass
        else:
            #convert row[7] to dict
            row7 = ast.literal_eval(row[7])
            newDict = {}
            for i in row7:
                if i == "2018-04-07" or i == "2018-04-08" or i == "2020-01-18" or i == "2020-01-18":
                    #remove from dict
                    pass
                else:
                    newDict[i] = row7[i]
            newRow = row[0:7] + [newDict]
            newData.append(newRow)
    return newData
    pass


#gets average accuracy of each week - can do by multiplying accuracy by count, then dividing by total count, or by doing accurcy/days
def calculate_averages(data):
    lengthOfData = len(data)
    weekAverage = 0
    countSum = 0

    for key, value in data.items():
        weekAverage += value[0]
        countSum += value[1]
    
    weekAverage = weekAverage/lengthOfData
    return weekAverage, countSum



#get average accross all values in the dict, figure out best n models
def getAveragesDict(data, noOfSets = 4):
    averagedData = {}
    #iterate through each row, and add the accuracy to the dict, and increment the count
    for i in data:
        #get the key 1 to 6
        key = (i[1], i[2], i[3], i[4], i[5], i[6])


        #calculate average of dictValues
        average, count = calculate_averages(i[7])


        #check if key is in dict
        if key in averagedData:
            #add the weekly accuracy
            oldVal = averagedData[key]
            newVal = (oldVal[0] + average, oldVal[1] + count)
            averagedData[key] = newVal
        else:
            #add new key
            averagedData[key] = (average, count)
    for row in averagedData:
        average, count = averagedData[row]
        averagedData[row] = ((average/noOfSets), count)
    return averagedData


#function that combines the data from both dictionaries, uses the keys to combine them, and then averages the accuracy uses the rate of appearance
def combineDicts(dict1, dict2):
    finalDict = {}
    for key, value in dict1.items():
        if key in dict2:
            #add the values together
            oldVal = dict2[key]
            #calculate accuracy using the count too TODO
            newAcc = (value[0]*value[1] + oldVal[0]*oldVal[1])/ (value[1] + oldVal[1])
            newVal = (newAcc, oldVal[1] + value[1])
            finalDict[key] = newVal
        else:
            #add the key to the dict
            finalDict[key] = value
    #go through Dict2 checking if all keys are in finalDict, if not in, add
    for key, value in dict2.items():
        if key not in finalDict:
            finalDict[key] = value
    return finalDict



#1 - use all sentiment analysis predictions
#2 - only use nodes that have initial correct prediction
path1 = "D:\\Users\\ted\\OneDrive\\Documents\\Computer_science\\dissertation\\NASsimResults1wCount2018old.csv"
path2 = "D:\\Users\\ted\\OneDrive\\Documents\\Computer_science\\dissertation\\NASsimResults2wCount2018old.csv"

path3 = "D:\\Users\\ted\\OneDrive\\Documents\\Computer_science\\dissertation\\FINALNASdAQ2018.csv"
path4 = "D:\\Users\\ted\\OneDrive\\Documents\\Computer_science\\dissertation\\FINALNASdAQ2020.csv"

#Will need to combine all the data values once acquired


data2018 = readFile(path3)
data2020 = readFile(path4)

data2018 = removesRepeatDates(data2018)
data2020 = removesRepeatDates(data2020)

averagedData2018 = getAveragesDict(data2018,1)
print(averagedData2018)
input()


#sort the dict
sorted_dict2018 = dict(sorted(averagedData2018.items(), key=lambda x: x[1][0], reverse=True))
#get the ten best models
count = 0
for key, value in sorted_dict2018.items():
    print(key, value)
    count += 1
    if count == 25:
        break

input()
#same for 2020
averagedData2020 = getAveragesDict(data2020,1)
#sort the dict
sorted_dict2020 = dict(sorted(averagedData2020.items(), key=lambda x: x[1][0], reverse=True))
#get the ten best models
count = 0
for key, value in sorted_dict2020.items():
    print(key, value)
    count += 1
    #if count == 100:
     #   break


#fix the dict for erroneous data
def fixDict(dict):
    for key, value in dict.items():
        if value[1] > 999:
            dict[key] = (value[0], 930)
    return dict

#call function to fix

averagedData2020 = fixDict(averagedData2020)
averagedData2018 = fixDict(averagedData2018)


#combine the dicts
finalDict = combineDicts(averagedData2018, averagedData2020)
#sort the dict
sorted_dict = dict(sorted(finalDict.items(), key=lambda x: x[1][0], reverse=True))
#get the ten best models
count = 0
for key, value in sorted_dict.items():
    print(key, value)
    count += 1
    if count == 50:
        break




#get 5 best models
bestModels = []
count = 0
for key, value in sorted_dict.items():
    newData = [key[0], key[1], key[2], key[3], key[4], key[5], value[0], value[1]]
    bestModels.append(newData)
    count += 1
    if count == 10:
        break

#run sim of best models with prop depth 3
print(bestModels)
input("^best models")

import pandas as pd
import matplotlib.pyplot as plt

def create_table_image(data, headers, output_file='table_image.png'):
    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=headers)

    # Calculate the aspect ratio of the figure to make sure the whole table fits
    width = len(df.columns) * 3
    height = len(df.index) * 0.4 + 2  # Increased figure height to accommodate larger headers
    fig, ax = plt.subplots(figsize=(width, height)) 

    # Remove axes
    ax.axis('off')

    # Create table and center columns
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc = 'center', loc='center')

    # Auto-adjust the width of the columns
    table.auto_set_column_width(col=list(range(len(df.columns))))

    # Set font size
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    # Increase the height of the header cells
    cell_dict = table.get_celld()
    for i in range(len(df.columns)):
        cell_dict[(0, i)].set_height(0.1)  # Modify this value as needed

    # Save the figure as an image
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.05)


# Example usage
data = [('VADER1', '2', '1', '0.1', '2', '0.15'), (0.6892174432497012, 1953)]
image_path = 'FinalTable.png'
headers = ["Sentiment Analysis\nModel", "Propagation Depth\n(range 0-3)", "Propagation Method\n(1,2,3)", "Correlation Coefficient\nThreshold (range 0-0.7)", "Correlation Coefficient\nHeuristic", "Sentiment Threshold\n(range 0.05-0.15)", "Average Accuracy", "Number of Predictions"]
create_table_image(bestModels, headers, image_path)
print("finished")


#removes all dictionary dates where data is repeated due to weekend circumstances
def removesRepeatDates2(data):
    newData = []
    for row in data:
        if row == []:
            pass
        else:
            #convert row[7] to dict
            row8 = ast.literal_eval(row[8])
            newDict = {}
            for i in row8:
                if i == "2018-04-07" or i == "2018-04-08" or i == "2020-01-18" or i == "2020-01-18":
                    #remove from dict
                    pass
                else:
                    newDict[i] = row8[i]
            newRow = row[0:8] + [newDict]
            newData.append(newRow)
    return newData
    pass

#get average accross all values in the dict, figure out best n models
def getAveragesDict2(data, noOfSets = 4):
    averagedData = {}
    #iterate through each row, and add the accuracy to the dict, and increment the count
    for i in data:
        #get the key 1 to 6
        key = (i[1], i[2], i[3], i[4], i[5], i[6], i[7])


        #calculate average of dictValues
        average, count = calculate_averages(i[8])


        #check if key is in dict
        if key in averagedData:
            #add the weekly accuracy
            oldVal = averagedData[key]
            newVal = (oldVal[0] + average, oldVal[1] + count)
            averagedData[key] = newVal
        else:
            #add new key
            averagedData[key] = (average, count)
    for row in averagedData:
        average, count = averagedData[row]
        averagedData[row] = ((average/noOfSets), count)
    return averagedData

#fix the dict for erroneous data
def fixDict2(dict):
    newRows = []
    for row in dict:
        dictindex = row[8]
        newDict = {}
        for key, value in dictindex.items():
            if value[1] > 100:
                newDict[key] = (value[0], 93)

        print(newDict)
        newRows.append([row[0:7], newDict])

#reads file
def readFile2(path):
    with open(path, 'r') as f:
        reader = csv.reader(f)
        data = list(reader)
    return data

def print_and_avg(data):
    for sublist in data:
        # print the first 7 elements
        print(sublist[:8])
        
        # the 8th element is a dictionary
        dict_data = sublist[8]
        
        # calculate the average of the 0th elements in the tuples in the dictionary
        avg = sum(val[0] for val in dict_data.values()) / len(dict_data)
        
        print(f'Average: {avg}\n')


#study best models
path5 = "D:\\Users\\ted\\OneDrive\\Documents\\Computer_science\\dissertation\\BESTMODELS.csv"
bestModels = readFile2(path5)
bestModels = removesRepeatDates2(bestModels)
print(bestModels)
input()
print_and_avg(bestModels)