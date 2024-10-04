# -*- coding: utf-8 -*-

import pandas as pd
import racemodule
from multielo import MultiElo, Player, Tracker

All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')

unique_combinations = All_Races[['year', 'round']].drop_duplicates().sort_values(['year', 'round']).reset_index(drop=True)

# Step 2: Create a sequence of unique dates starting from an arbitrary date (e.g., "2000-01-01")
unique_combinations['date'] = pd.date_range(start='2000-01-01', periods=len(unique_combinations), freq='D')

resultsdict = {}
for i in range(1, max(All_Races['raceId'])+1):
    race, dnf = racemodule.extract_race(i, All_Races)
    resultsdict[i] = pd.Series(race['driverId'].tolist())
    temp = set(resultsdict[i])
    resultsdict[i] = list(resultsdict[i])
    
results = pd.DataFrame().from_dict(resultsdict, orient='index')
results = results.reset_index(drop=True)
results.insert(0, 'date', unique_combinations['date'])

tracker = Tracker()
tracker.process_data(results)

ratings = tracker.get_current_ratings()
history = tracker.get_history_df()
historygroup = history.groupby('player_id')['rating'].max()

testrace, testdnf = racemodule.extract_race(3, All_Races)
test = racemodule.results_without_teammates(testrace)