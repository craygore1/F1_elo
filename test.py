# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:18:55 2024

@author: woods
"""

import glicko2
import pandas as pd
import racemodule


All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')
Driver_Glicko = {driver: idx for idx, driver in enumerate(All_Drivers.id)}

for row in All_Drivers.itertuples():
    temp = glicko2.Player()
    driver = row.id
    Driver_Glicko[driver] = temp

# Initializing rating
Current_Rating = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Current_Rating['Rating'] = 1500
Current_Rating['RD'] = 350

race, dnf = racemodule.extract_race(1119, All_Races)
    
teamdict = {k: v for k, v in race.groupby("constructorId")}
teamdict = {key: df for key, df in teamdict.items() if df.shape[0] > 1}

h2h_dict = {}
New_Rating = []
for team in teamdict.keys():
    h2h = racemodule.race_to_h2h_team(teamdict[team]['driverId'])
    h2h_dict[team] = h2h

for team in teamdict.keys():
    for i, driver in enumerate(h2h_dict[team]):
        Race_Ratings = Current_Rating[Current_Rating['id'].isin(teamdict[team]['driverId'])]
        Race_Ratings = Race_Ratings[Race_Ratings['id'].isin([driver]) == False]

        Driver_Glicko[driver].update_player(Race_Ratings['Rating'], 
                                            Race_Ratings['RD'], h2h_dict[team][driver])
         
        New_Rating.append(Driver_Glicko[driver].getRating())
         
        Current_Rating.loc[Current_Rating['id'] == driver, 'Rating'] = Driver_Glicko[driver].getRating()
        Current_Rating.loc[Current_Rating['id'] == driver, 'RD'] = Driver_Glicko[driver].getRd()
