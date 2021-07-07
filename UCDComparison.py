import csv
import pandas as pd

def day_difference():
    for day in days:
        if list1[i1][day + " Start Time"].find(list1[i1][day + " Start Time"]) < 0: return True
        elif list1[i1][day + " End Time"].find(list1[i1][day + " End Time"]) < 0: return True
    return False

with open("Fall Quarter 2020 Classes - Copy.csv",'r') as f1, open("Fall Quarter 2019 Classes - Copy.csv",'r') as f2:
    reader1 = csv.DictReader(f1, delimiter=',')
    reader2 = csv.DictReader(f2, delimiter=',')

    list1 = list(reader1)
    list2 = list(reader2)

    count1 = len(list1)
    count2 = len(list2)
    if count1 < count2: small_count = count1
    else: small_count = count2

    code = 'Course Code'
    current_code = list1[0][code]
    prev_code1 = list1[0][code]
    prev_code2 = list1[0][code]

    days = ["M","T","W","R","F"] #a list of all days

    differences = 0

    i1 = 0
    i2 = 0

    while i1 < small_count and i2 < small_count:

        code1 = list1[i1][code]
        code2 = list2[i2][code]

        print("Code 1 is: " + code1 + " and Code 2 is: " + code2)
        
        #if the two course codes are different
        if code1.find(code2) < 0:
            #if course code for list 1 is different from the current course code whle course code 2 is the same, then advance list 2 until it equals list 1
            if code1.find(prev_code1) < 0 and code2.find(prev_code2) >= 0:
                i2 += 1
                prev_code2 = code2
                differences += 1
            #if course code for list 2 is different from the current course code whle course code 1 is the same, then advance list 1 until it equals list 2
            elif code2.find(prev_code2) < 0 and code1.find(prev_code1) >= 0:
                i1 += 1
                prev_code1 = code1
                differences += 1
            else:
                i1 += 1
                i2 += 1
                differences += 1
        else:
            if code1.find(prev_code1) < 0:
                prev_code1 = code1
                prev_code2 = code2
                i1 += 1
                i2 += 1
                if day_difference(): differences += 1
            else:
                i1 += 1
                i2 += 1
                if day_difference(): differences += 1

    print("The # of differences is: " + str(differences))

#data_2020 = pd.read_csv("Fall Quarter 2020 Classes.csv")
#data_2019 = pd.read_csv("Fall Quarter 2019 Classes.csv")

#print(data_2020.shape)