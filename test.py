# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:18:55 2024

@author: woods
"""

import pandas as pd
import racemodule
from multielo import MultiElo, Player, Tracker

All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')

unique_combinations = All_Races[['year', 'round']].drop_duplicates().sort_values(['year', 'round']).reset_index(drop=True)
unique_combinations['date'] = unique_combinations.index

testrace, testdnf = racemodule.extract_race(1, All_Races)
test = racemodule.results_only_teammates(testrace)
test = racemodule.remove_single_row_dfs(test)

Current_Rating = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Current_Rating['rating'] = 1500

k = 20
base = 1

elo_custom = MultiElo(k_value=k, score_function_base=base)

driver_elo = {driver: idx for idx, driver in enumerate(All_Drivers.id)}

for row in All_Drivers.itertuples():
    driver = row.id
    driver_elo[driver] = Player(driver, rating=1500)

resultsdict = {}
for driver in test.keys():
    Race_Ratings = Current_Rating.merge(test[driver], left_on='id', right_on = 'driverId')
    Race_Ratings = Race_Ratings.sort_values(by = ['positionDisplayOrder'])
    Race_Ratings = Race_Ratings.drop_duplicates(subset = 'driverId', keep='first')
    resultsdict[driver] = Race_Ratings
    
for person in test.keys():
    df = resultsdict[person].reset_index(drop=True)
    person_idx = df[df['driverId'] == person].index
    result = resultsdict[person]['rating']
    new_rating = elo_custom.get_new_ratings(result)[person_idx]
    Current_Rating.loc[Current_Rating['id'] == person, 'rating'] = new_rating

    
