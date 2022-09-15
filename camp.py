from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
from bs4 import BeautifulSoup
from IPython.display import display
import numpy as np
import requests
import json


#park = "Garibaldi Park"
park = "Joffre Lakes Park"
campground = "Upper Lakes Campground"

cal_month = 'October'
cal_date = '11'
num_ppl = '2'
num_days = 2
#campground = "Garibaldi Lake Campground"

chrome_options = Options()
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")

DRIVER_PATH = '/home/hassan/Desktop/python_files/camping_bot/driver/chromedriver'
driver = webdriver.Chrome(DRIVER_PATH, options=chrome_options)
#driver = webdriver.Chrome(DRIVER_PATH)
driver.get('https://discovercamping.ca/BCCWeb/Facilities/TrailRiverCampingSearchView.aspx')

#select park name from dropdown

#camp_site = driver.find_element_by_id('ddlPlaces')
#Select camp_site = new Select(camp_site)
camp_site = Select(driver.find_element_by_id('ddlPlaces'))
#camp_site.selectByVisibleText(park) 
camp_site.select_by_visible_text(park) 

#select date 
driver.find_element_by_id('mainContent_homeContent_txtArrivalDate').click()


def date_select(mon):

	month1 = driver.find_element_by_xpath('//span[@class ="ui-datepicker-month"]').text

	if month1 == mon:
		driver.find_element_by_xpath(f'//a[text()={cal_date}]').click()
	else:
		#driver.find_element_by_xpath('//a[@class="ui-datepicker-next ui-corner-all"]').click()
		driver.find_element_by_xpath('//span[@class="ui-icon ui-icon-circle-triangle-e"]').click()
		month2 = driver.find_element_by_xpath('//span[@class ="ui-datepicker-month"]').text
		return (date_select(month2))

date_select(cal_month)


#no. of people
#people_num = Select(driver.find_element_by_id('ddlParty'))
#camp_site.selectByVisibleText(num_ppl)

select = Select(driver.find_element_by_id('ddlParty'))
select.select_by_visible_text('2')
#select.select_by_value('2')


#click search 

click_search = driver.find_element_by_id('btnSearch').click()

#find campground
time.sleep(3)

driver.get_screenshot_as_file("screenshot.png")


#retreive reservation table
tbl = driver.find_element_by_xpath("//html/body/form/div[10]/main/div/div[5]/div[3]/div[4]/div[6]/div/div/div[1]/table").get_attribute('outerHTML')
reso_cal = pd.read_html(tbl)

#display(reso_cal)

dr = list(range(int(cal_date), (int(cal_date)+12)))
dr.insert(0, 'campground')
#col_list = temp.append(list(range(int(cal_date), (int(cal_date)+12))))

df1 = pd.DataFrame(np.concatenate(reso_cal), columns=dr)

#display(df1)

df2 = df1.loc[df1['campground'] == campground]

#display(df2)


#dates_available = df2.apply(lambda row:row[row != 'Not Available'])

dates_available = df2.columns[(~df2.isin(['Not Available'])).any()]
list_dates_available = dates_available.tolist()

list_dates_available.remove('campground')

#print(list_dates_available)

#print([str(x) for x in dates_available.tolist()])

#send slack notification

range_date = list(range(int(cal_date), (int(cal_date)+int(num_days))))

if all(elem in list_dates_available for elem in range_date):
	#message = "site available"
	message = f"{campground} available for {','.join([str(i) for i in range_date])}"
else:
	message = f"{campground} not available for {','.join([str(i) for i in range_date])}"

#message = str(range_date)

webhook_url = 'https://hooks.slack.com/services/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'
message = {'text': message}

response = requests.post(
	webhook_url, data=json.dumps(message),
	headers = {'Content-Type': 'appliaction/json'})

if response.status_code != 200:
	raise ValueError(
		'Request to slack returned an error %s, the response is:\n%s'
		% (response.status_code, response.text))

print("site probed")

driver.quit()