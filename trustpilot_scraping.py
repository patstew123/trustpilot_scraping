from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import json
import time
import requests
from pathlib import Path
import re
import datetime
import collections

trustpilot_reviews = []
trustpilot_ratings = []
trustpilot_responses = []
trustpilot_times = []
trustpilot_ids = []
trustpilot_url_link = 'https://uk.trustpilot.com/review/theaccessgroup.com'

# TQDM - progressbar
stage = 'processing'
page = 0
start_time = time.time()
seconds = 100000
while stage == 'processing':
    URL = trustpilot_url_link + "?page=" + str(page)
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, 'html.parser')
    # check if there is next page, break if not
    next_link = soup.find("a", text="next")
    review_div = soup.find_all('article', {'class','paper_paper__1PY90 paper_square__lJX8a card_card__lQWDv styles_reviewCard__hcAvl'})
    for i in range(len(review_div)): 
        trustpilot_ids.append(i)
        reviewer = review_div[i]
        try:
            trustpilot_review = reviewer.find('p', attrs={'class': "typography_typography__QgicV typography_body__9UBeQ typography_color-black__5LYEn typography_weight-regular__TWEnf typography_fontstyle-normal__kHyN3"}).text
            trustpilot_reviews.append(trustpilot_review)
        except:
            trustpilot_review = None
            trustpilot_reviews.append(trustpilot_review)
        star_rating = ""
        try:
            star_rating = star_rating + reviewer.find('img').get('alt')
        except:
            star_rating = star_rating
        m = re.search(r"\d", star_rating)
        try:
            trustpilot_ratings.append(int(m.group()))
        except:
            trustpilot_ratings.append(None)
        try:
            G_response = reviewer.find('p', attrs={'class':'typography_typography__QgicV typography_bodysmall__irytL typography_color-gray-7__9Ut3K typography_weight-regular__TWEnf typography_fontstyle-normal__kHyN3 styles_message__shHhX'}).text
            trustpilot_responses.append(G_response)
        except:
            G_response = None
            trustpilot_responses.append(G_response)
        try:
            date = reviewer.find('time').get('datetime')
            trustpilot_times.append(date)
        except:
            date = None
            trustpilot_times.append(date)
    # Build up duplicate list and exit if duplicates on exact datetime is greater than 10
    duplicate_list = [item for item, count in collections.Counter(trustpilot_times).items() if count > 1]
    if len(duplicate_list) > 10:
        stage = 'end'
    # Add time control as well
    current_time = time.time()
    elapsed_time = current_time - start_time
    if elapsed_time > seconds:
        stage = 'end'
    page += 1
    time.sleep(5)
    print(page)

# Implement full_dataframe
new_dataframe = pd.DataFrame(list(zip(trustpilot_reviews, trustpilot_ratings,trustpilot_responses,trustpilot_times)), columns=['Verbatim','Star_ratings','G_response','Date'])
new_dataframe = new_dataframe.drop_duplicates()
new_dataframe['Date'] = pd.to_datetime(new_dataframe['Date'])
new_dataframe['Datetime'] = new_dataframe['Date']

# Add the other data columns
new_dataframe['Provided_Verbatim'] = np.where(new_dataframe['Verbatim'].isnull(),"No","Yes")
new_dataframe['Provided_Response'] = np.where(new_dataframe['G_response'].isnull(), "No","Yes")
new_dataframe['Verbatim_Binary'] = np.where(new_dataframe['Verbatim'].isnull(),0,1)
new_dataframe['Response_Binary'] = np.where(new_dataframe['G_response'].isnull(),0,1)
new_dataframe['Good_Review'] = np.where(new_dataframe['Star_ratings'] >= 4, "Yes","No")

filepath = Path('0 combining data/trustpilot_data.csv')
new_dataframe.to_csv(filepath, index=False)





