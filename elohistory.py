# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import racemodule
from multielo import MultiElo, Player, Tracker

All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')

unique_combinations = All_Races[['year', 'round']].drop_duplicates().sort_values(['year', 'round']).reset_index(drop=True)
unique_combinations['date'] = unique_combinations.index

Current_Rating = pd.DataFrame(data=All_Drivers, columns=['id', 'name', 'dateOfBirth'])
Current_Rating['dateOfBirth'] = pd.to_datetime(Current_Rating['dateOfBirth'])
Current_Rating['rating'] = np.where(Current_Rating['dateOfBirth'].dt.year < 1928, 1500, 1450)

Rating_History = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Rating_History[0] = Current_Rating['rating']

Current_Rating_Team = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Current_Rating_Team['rating'] = Current_Rating['rating']

Rating_History_Team = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Rating_History_Team[0] = Current_Rating_Team['rating']

Blended_Rating = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Blended_Rating['rating'] = 0.14*Current_Rating['rating'] + 0.86*Current_Rating_Team['rating']
Blended_History = pd.DataFrame(data=All_Drivers, columns=['id', 'name'])
Blended_History[0] = Blended_Rating['rating']

k = 20
base = 1

elo_custom = MultiElo(k_value=k, score_function_base=base)

update_dict = {}
update_dict_team = {}
update_dict_blended = {}
for i in range(1, max(All_Races['raceId'])+1):
    updated_ratings = racemodule.elo_race(i, Current_Rating, elo_custom, All_Races)
    Current_Rating['rating'] = updated_ratings['rating']
    update_dict[i] = Current_Rating['rating']
    
    team_ratings = racemodule.elo_race_team(i, Current_Rating_Team, elo_custom, All_Races)
    Current_Rating_Team['rating'] = team_ratings['rating']
    update_dict_team[i] = Current_Rating_Team['rating']
    
    Blended_Rating['rating'] = 0.14*Current_Rating['rating'] + 0.86*Current_Rating_Team['rating']
    update_dict_blended[i] = Blended_Rating['rating']
    
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

Blended_History = pd.concat([Blended_History, pd.DataFrame(update_dict_blended, index=Blended_Rating.index)], axis=1)
numeric_RH_Blend = Blended_History.select_dtypes(include='number')
string_RH_Blend = Blended_History.iloc[:, :2]

Career_High_Blend = string_RH_Blend.copy()
Career_High_Blend['Max'] = numeric_RH_Blend.max(axis=1)


Blended_History.to_csv('blendhistory.csv', index=False)

Rating_History.to_csv('history.csv', index=False)

Rating_History_Team.to_csv('teamhistory.csv', index=False)