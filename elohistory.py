# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import glicko2
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

Rating_History = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Rating_History[0] = Current_Rating['Rating']

update_dict = {}

for i in range(1, max(All_Races['raceId']) + 1):
    updated_ratings, single_race, test, h2h = racemodule.run_race(i,Current_Rating, Driver_Glicko, All_Races)
    Current_Rating['Rating'] = updated_ratings['Rating']
    Current_Rating['RD'] = updated_ratings['RD']
    update_dict[i] = Current_Rating['Rating']


Rating_History = pd.concat([Rating_History, pd.DataFrame(update_dict, index=Current_Rating.index)], axis=1)
numeric_RH = Rating_History.select_dtypes(include='number')
string_RH = Rating_History.iloc[:, :2]

Career_High = string_RH.copy()
Career_High['Max'] = numeric_RH.max(axis=1)
    

#max(All_Races['raceId'])

    

