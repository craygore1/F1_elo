# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import racemodule
from multielo import MultiElo, Player, Tracker
import time

start_time = time.time()

All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Quali = pd.read_csv('f1db-races-qualifying-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')

# Function to create initial dataframes and set ratings
def create_driver_data(all_drivers, default_rating=1425, old_driver_rating=1500):
    df = pd.DataFrame(data=all_drivers, columns=['id', 'name', 'dateOfBirth'])
    df['dateOfBirth'] = pd.to_datetime(df['dateOfBirth'])
    df['rating'] = np.where(df['dateOfBirth'].dt.year < 1920, old_driver_rating, default_rating)
    return df

# Function to create rating history dataframes
def create_rating_history(all_drivers, rating_column):
    history = pd.DataFrame(data=all_drivers, columns=['id', 'name'])
    history[0] = rating_column
    return history

Current_Rating = create_driver_data(All_Drivers)
Current_Quali = create_driver_data(All_Drivers)

Rating_History = create_rating_history(All_Drivers, Current_Rating['rating'])
Quali_History = create_rating_history(All_Drivers, Current_Quali['rating'])

Current_Rating_Team = Current_Rating[['id', 'name']].copy()
Current_Rating_Team['rating'] = Current_Rating['rating']

Current_Quali_Team = Current_Quali[['id', 'name']].copy()
Current_Quali_Team['rating'] = Current_Quali['rating']

Rating_History_Team = create_rating_history(All_Drivers, Current_Rating_Team['rating'])
Quali_History_Team = create_rating_history(All_Drivers, Current_Quali_Team['rating'])

# Function to create Blended Rating and History
def create_blended_data(all_drivers, rating1, rating2, weight1=0.25, weight2=0.75):
    blended = pd.DataFrame(data=all_drivers, columns=['id', 'name'])
    blended['rating'] = weight1 * rating1 + weight2 * rating2
    blended_history = create_rating_history(all_drivers, blended['rating'])
    return blended, blended_history

Blended_Rating, Blended_History = create_blended_data(All_Drivers, Current_Rating['rating'], Current_Rating_Team['rating'])
Blended_Quali, Blended_History_Quali = create_blended_data(All_Drivers, Current_Quali['rating'], Current_Quali_Team['rating'])
Full_Blend, Full_Blend_History = create_blended_data(All_Drivers, Blended_Quali['rating'], Blended_Rating['rating'], weight1=0.2, weight2=0.8)

k = 32
k_team = 26
base = 1

elo_custom = MultiElo(k_value=k, score_function_base=base)
elo_team = MultiElo(k_value=k_team, score_function_base=base)

indy = [3, 9, 17, 25, 34, 44, 51, 59, 68, 77, 87] #indy500 racenumbers
    
# Function to update ratings for a given race
def update_ratings(race_id, is_indy, current_df, current_team_df, quali_df, 
                   quali_team_df, blended_df, quali_blended_df, full_blend_df, 
                   base_value):
    # Adjust k values based on the race type (Indy 500 or others)
    k = 8 if is_indy else 32
    k_team = 8 if is_indy else 24
    
    elo_custom = MultiElo(k_value=k, score_function_base=base_value)
    elo_team = MultiElo(k_value=k_team, score_function_base=base_value)
    
    # Update driver ratings
    updated_ratings = racemodule.elo_race(race_id, current_df, elo_custom, All_Races)
    current_df['rating'] = updated_ratings['rating']
    
    # Update team ratings
    team_ratings = racemodule.elo_race_team(race_id, current_team_df, elo_team, All_Races)
    current_team_df['rating'] = team_ratings['rating']
    
    # Update qualifying ratings
    updated_quali = racemodule.elo_race(race_id, quali_df, elo_custom, All_Quali)
    quali_df['rating'] = updated_quali['rating']
    
    # Update qualifying team ratings
    team_quali = racemodule.elo_race_team(race_id, quali_team_df, elo_team, All_Quali)
    quali_team_df['rating'] = team_quali['rating']
    
    # Calculate blended ratings
    blended_df['rating'] = 0.25 * current_df['rating'] + 0.75 * current_team_df['rating']
    quali_blended_df['rating'] = 0.25 * quali_df['rating'] + 0.75 * quali_team_df['rating'] 
    full_blend_df['rating'] = 0.2 * quali_blended_df['rating'] + 0.8 * blended_df['rating']
    
    # Return the updated ratings in dictionary format
    return (current_df['rating'].copy(), team_ratings['rating'].copy(), 
            quali_df['rating'].copy(), team_quali['rating'].copy(), 
            blended_df['rating'].copy(), quali_blended_df['rating'].copy(), 
            full_blend_df['rating'].copy())

update_dict, update_dict_team = {}, {}
update_dict_quali, update_dict_quali_team = {}, {}
update_dict_blended, update_dict_quali_blended = {}, {}
update_dict_full_blend = {}

# Iterate through all races and update ratings
for i in range(1, max(All_Races['raceId']) + 1):
    # Check if the race is an Indy 500 race
    is_indy_race = i in indy

    # Update ratings and get the updated dictionaries
    (update_dict[i], update_dict_team[i], 
     update_dict_quali[i], update_dict_quali_team[i], 
     update_dict_blended[i], update_dict_quali_blended[i], 
     update_dict_full_blend[i]) = update_ratings(
        race_id=i,
        is_indy=is_indy_race,
        current_df=Current_Rating,
        current_team_df=Current_Rating_Team,
        quali_df=Current_Quali,
        quali_team_df=Current_Quali_Team,
        blended_df=Blended_Rating,
        quali_blended_df=Blended_Quali,
        full_blend_df=Full_Blend,
        base_value=base
    )
    
# Function to create Career High and Career History
def history_and_high(df, update_dict, index):
    df = pd.concat([df, pd.DataFrame(update_dict, index=index)], axis=1)
    
    # Separate numeric and string columns
    numeric_df = df.select_dtypes(include='number')
    string_df = df.iloc[:, :2]  # Assuming the first two columns are string-type
    
    # Create a copy and calculate career high
    Career_High = string_df.copy()
    Career_High['Max'] = numeric_df.max(axis=1)
    
    History = df.copy()
    return History, Career_High

Rating_History, Career_High = history_and_high(Rating_History, update_dict, Current_Rating.index)
Rating_History_Team, Career_High_Team = history_and_high(Rating_History_Team, update_dict_team, Current_Rating_Team.index)
Blended_History, Career_High_Blend = history_and_high(Blended_History, update_dict_blended, Blended_Rating.index)
Blended_History_Quali, Career_High_Quali_Blend = history_and_high(Blended_History_Quali, update_dict_quali_blended, Blended_Quali.index)
Full_Blend_History, Career_High_Full_Blend = history_and_high(Full_Blend_History, update_dict_full_blend, Full_Blend.index)

Full_Blend_History.to_csv('blendhistory.csv', index=False)
Blended_History_Quali.to_csv('qualihistory.csv', index=False)
Rating_History.to_csv('history.csv', index=False)
Rating_History_Team.to_csv('teamhistory.csv', index=False)

end_time = time.time()
elapsed_time = end_time - start_time
print(elapsed_time)
