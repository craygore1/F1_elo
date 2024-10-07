# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:18:55 2024

@author: woods
"""

import pandas as pd
import racemodule
from multielo import MultiElo, Player, Tracker
import time

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
    
def elo_race_team_gpt(racenumber, ratings, elo, df):
    # Extract race and teammate information
    race, dnf = racemodule.extract_race(racenumber, df)
    temp = racemodule.results_only_teammates(race)
    temp = racemodule.remove_single_row_dfs(temp)
    
    # Merge ratings with all drivers in the race at once (outside loop)
    merged_race_ratings = ratings.merge(race, left_on='id', right_on='driverId')
    merged_race_ratings = merged_race_ratings.sort_values(by='positionDisplayOrder').drop_duplicates(subset='driverId', keep='first')
    
    # Dictionary to store filtered DataFrames for each driver
    resultsdict = {}
    for driver in temp.keys():
        # Filter for each driver's data only once using the precomputed merged DataFrame
        resultsdict[driver] = merged_race_ratings[merged_race_ratings['driverId'].isin(temp[driver]['driverId'])]
    
    # Calculate new ratings for each driver and update
    for person in temp.keys():
        tempdf = resultsdict[person].reset_index(drop=True)
        person_idx = tempdf[tempdf['driverId'] == person].index
        result = tempdf['rating']
        new_rating = elo.get_new_ratings(result)[person_idx]
        
        # Update ratings for each person based on the new calculated ratings
        ratings.loc[ratings['id'] == person, 'rating'] = new_rating

    return ratings

orgfunc = Current_Rating.copy()
gptfunc = Current_Rating.copy()
start_time = time.time()
for i in range(1, 1000): 
    orgfunc = racemodule.elo_race_team(i, orgfunc, elo_custom, All_Races)
end_time = time.time()

elapsed_time = end_time - start_time

start_time_gpt = time.time()
for i in range(1, 1000): 
    gptfunc = racemodule.elo_race_team(i, gptfunc, elo_custom, All_Races)
end_time_gpt = time.time()

elapsed_time_gpt = end_time_gpt - start_time_gpt

    
