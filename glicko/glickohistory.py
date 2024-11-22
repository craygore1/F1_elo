# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import glicko2
import racemodule



All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')

Driver_Glicko = {driver: idx for idx, driver in enumerate(All_Drivers.id)}
Driver_Glicko_Team = {driver: idx for idx, driver in enumerate(All_Drivers.id)}

for row in All_Drivers.itertuples():
    temp = glicko2.Player()
    driver = row.id
    Driver_Glicko[driver] = temp
    Driver_Glicko_Team[driver] = temp

# Initializing rating
Current_Rating = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Current_Rating['Rating'] = 1500
Current_Rating['RD'] = 350

Rating_History = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Rating_History[0] = Current_Rating['Rating']

update_dict = {}
    
# Initializing team rating
Current_Rating_Team = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Current_Rating_Team['Rating'] = 1500
Current_Rating_Team['RD'] = 350

Blended_Rating = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Blended_Rating['Rating'] = 0.14*Current_Rating['Rating'] + 0.86*Current_Rating_Team['Rating']
Blended_Rating['RD'] = 0.14*Current_Rating['RD'] + 0.86*Current_Rating_Team['RD']

Rating_History_Team = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Rating_History_Team[0] = Current_Rating['Rating']

update_dict_team = {}

for i in range(1, max(All_Races['raceId'])+1):
    updated_ratings, single_race = racemodule.run_race(i,Blended_Rating, Driver_Glicko, All_Races)
    Current_Rating['Rating'] = updated_ratings['Rating']
    Current_Rating['RD'] = updated_ratings['RD']
    update_dict[i] = Current_Rating['Rating']
    
    team_ratings = racemodule.run_race_team(i,Blended_Rating, Driver_Glicko_Team, All_Races)
    Current_Rating_Team['Rating'] = team_ratings['Rating']
    Current_Rating_Team['RD'] = team_ratings['RD']
    update_dict_team[i] = Current_Rating_Team['Rating']
    
    Blended_Rating['Rating'] = 0.14*Current_Rating['Rating'] + 0.86*Current_Rating_Team['Rating']
    Blended_Rating['RD'] = 0.14*Current_Rating['RD'] + 0.86*Current_Rating_Team['RD']


Rating_History = pd.concat([Rating_History, pd.DataFrame(update_dict, index=Current_Rating.index)], axis=1)
numeric_RH = Rating_History.select_dtypes(include='number')
string_RH = Rating_History.iloc[:, :2]

Career_High = string_RH.copy()
Career_High['Max'] = numeric_RH.max(axis=1)

Rating_History_Team = pd.concat([Rating_History_Team, pd.DataFrame(update_dict_team, index=Current_Rating_Team.index)], axis=1)
numeric_RH_Team = Rating_History_Team.select_dtypes(include='number')
string_RH_Team = Rating_History_Team.iloc[:, :2]

Career_High_Team = string_RH_Team.copy()
Career_High_Team['Max'] = numeric_RH_Team.max(axis=1)   



    

