import argparse
import re
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import csv
import os

ap = argparse.ArgumentParser(description="Scrape class times and terms from UC Davis")
ap.add_argument('-t','--term',
                required=False, type=str, default=None,
                help="term from which to scrape from")
args = vars(ap.parse_args())
term = args['term'] if args['term'] != None else input("Provide term to search classes for: ")

driver = webdriver.Chrome()
url='https://registrar-apps.ucdavis.edu/courses/search/index.cfm'
driver.get(url)

search_button = driver.find_element_by_name('search')
subject_area = Select(driver.find_element_by_name('subject'))
term_selector = Select(driver.find_element_by_name('termCode'))

def read_data(x):

    #select the item of index x and click the search button
    subject_area.select_by_index(x)
    search_button.click()

    try:
        #find the element with all of the data, get that data, then parse it
        element = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mc_win, #courseResultsDiv h2 #home_tablez')))
        table_content = element.get_attribute('outerHTML')
        soup = BeautifulSoup(table_content, 'lxml')

        #get the table with all the pertinent data and get all the rows from that
        course_table = soup.find('table', attrs={'id': 'mc_win'})
        course_table_data = course_table.tbody.find_all('tr', {'onmouseover':re.compile('this.*')})

        #for every row that we got
        for tr in course_table_data:

            #make a dictionary for that row
            t_row = {}
            td_count = 0 #counter to track which column we're on

            #for every element in that row
            for td in tr.find_all('td'):

                td_count+=1 #update the counter

                #if we're on the first column (which holds the CRN, time, and days)
                if td_count == 1:
                    #get the CRN
                    CRN = td.find('strong').text.strip()
                    t_row["CRN"] = td.find('strong').text.strip()

                    days = ["M","T","W","R","F"] #a list of all days
                    try:
                        #convert the string into start and end times
                        raw_days = td.find('em').text.strip().split(',')[1].strip()
                        raw_time = td.find('em').text.strip().split(',')[0].strip()
                        raw_start_time = raw_time.split('-')[0].strip()
                        raw_end_time = raw_time.split('-')[1].strip()
                        start_time = (60 * int(raw_start_time.split(':')[0])) + int(raw_start_time.split(':')[1])
                        end_time = (60 * int(raw_end_time.split(':')[0])) + int(raw_end_time.split(':')[1].split(' ')[0])
                        if raw_end_time.find('PM') > -1:
                            if raw_start_time.find('12') < 0: start_time += 12*60
                            if raw_end_time.find('12') < 0: end_time += 12*60

                        #put those start and end times into a column for each day
                        for day in days:
                            if raw_days.find(day) > -1:
                                t_row[day + "StartTime"] = start_time
                                t_row[day + "EndTime"] = end_time
                            else:
                                t_row[day + "StartTime"] = ''
                                t_row[day + "EndTime"] = ''

                    #exception for when no times or days are provided
                    except IndexError:
                        for day in days:
                            t_row[day + "StartTime"] = ''
                            t_row[day + "EndTime"] = ''

                #if we're on column two, get the course code
                elif td_count == 2: t_row["Code"] = td.text.strip().split('\n')[0]
                elif td_count == 5: t_row["Instructor"] = td.text.strip().split('\n')[0].strip()

            #add the row's data we just got to the list of row dictionaries
            table_data.append(t_row)

        print("Data found for " + subject_area.first_selected_option.get_attribute("value"))

    except AttributeError:
        print("Couldn't find any data for " + subject_area.first_selected_option.get_attribute("value"))
    except selenium.common.exceptions.TimeoutException:
        print("Couldn't find any data for " + subject_area.first_selected_option.get_attribute("value"))

#function to write all the data we got to a csv file
def write_data():
    with open(f"{term}.csv", 'w', newline='') as out_file:

        #get the keys and declare the dict writer
        keys = table_data[0].keys()
        writer = csv.DictWriter(out_file, keys)

        #write the header and all the data
        writer.writeheader()
        writer.writerows(table_data)

max_index = len(subject_area.options) # gets length of the selector
delay = 7 # maximum time to wait to find elements on search (shouldn't take that longg anyway)
x = 1 # should start at 1 since 0 is the default selection and won't give any data
table_data = []
while x < max_index:
    term_selector.select_by_visible_text(term)
    read_data(x)
    x+=1

driver.quit()

write_data()
