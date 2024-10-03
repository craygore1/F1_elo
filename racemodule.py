# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import glicko2

def race_to_h2h(results, teams):
    """
    Converts a race result list into head-to-head vectors.
    
    Parameters:
        results: A list that represents a single race's finish order. 
                                 E.g., ["john", "matt", "bob"]
        teams: A corresponding list of teams for each of the drivers also in finishing order.
    
    Returns:
        dict: A dictionary where the key is the participant and the value is the head-to-head vector.
    """
    # Step 1: Gather all unique participants
    participant_idx = {participant: idx for idx, participant in enumerate(results)}

    # Step 2: Create a dictionary to store head-to-head vectors
    head_to_head_vectors = {participant: [0] * (len(results) - 1) for participant in results}
    
    fulldf = pd.concat([results, teams], axis=1)
    fulldf.columns = ['Results', 'Teams']
    
    all_opponents = {participant: [] for participant in results}
    # Step 3: Update head-to-head vectors based on person results
    for i, driver in enumerate(participant_idx):
        current_participant = driver
        for j in range(i, len(results)-1):
            head_to_head_vectors[current_participant][j] = 1
        for k in range(len(results)-1):
            opponent = results.iloc[k]
            if fulldf.loc[fulldf['Results'] == opponent, 'Teams'].values[0] == fulldf.loc[fulldf['Results'] == current_participant, 'Teams'].values[0]:
                head_to_head_vectors[current_participant][k] = 999
            else:
                all_opponents[current_participant].append(opponent)
                
                
        head_to_head_vectors[current_participant] = [x for x in head_to_head_vectors[current_participant] if x != 999]

    return head_to_head_vectors, all_opponents

def extract_race(racenumber, df):
    '''
    Parameters
    ----------
    racenumber : Race number in f1 history (from raceID column)
    df: DataFrame containing all results

    Returns
    -------
    race_results : Cleaned race results
    driver_dnfs: list of dnfs
    '''
    driver_dnfs = list()
    
    race_results = df[df['raceId'] == racenumber]
    
    race_results = race_results[['raceId','round','positionDisplayOrder',
                                 'positionNumber', 'driverId', 'constructorId']]
    
    if race_results.empty:
        return race_results, driver_dnfs
    else:
        driver_dnfs = race_results[race_results['positionNumber'].isna()]
        race_results = race_results.drop(driver_dnfs.index)
    return race_results, driver_dnfs

def run_race(racenumber, ratings, glicko, df):
    '''
    Does a glicko update for all competitors (excludes teammates).
    
    Parameters
    ----------
    racenumber : Race number in f1 history (from raceID column)
    ratings : Current ratings and RD of all drivers
    glicko : glicko class instances for all drivers
    df : dataframe of all races

    Returns
    -------
    updated_ratings : updated dataframe of ratings and rd for all drivers
    race_result : new ratings for only the drivers in the race

    '''
    Race_Result, Dnfs = extract_race(racenumber ,df)
    h2h, opponents = race_to_h2h(Race_Result['driverId'],Race_Result['constructorId'])
    
    New_Rating = []

    for i, driver in enumerate(Race_Result['driverId']):
        #sequence = [x for x in range(len(Race_Ratings['id'])) if x != i]
        
        Race_Ratings = ratings[ratings['id'].isin(opponents[driver])]
        temp = Race_Result[Race_Result['driverId'].isin(opponents[driver])]
        Race_Ratings = Race_Ratings.merge(temp, left_on='id', right_on = 'driverId')
        Race_Ratings = Race_Ratings.sort_values(by = ['positionDisplayOrder'])
        
        Race_Ratings = Race_Ratings.drop_duplicates(subset = 'driverId', keep='first')

        glicko[driver].update_player(Race_Ratings['Rating'], 
                                         Race_Ratings['RD'], h2h[driver])
        
        New_Rating.append(glicko[driver].getRating())
        
        ratings.loc[ratings['id'] == driver, 'Rating'] = glicko[driver].getRating()
        ratings.loc[ratings['id'] == driver, 'RD'] = glicko[driver].getRd()
        
    for driver in Dnfs['driverId']:
        glicko[driver].did_not_compete()
        ratings.loc[ratings['id'] == driver, 'RD'] = glicko[driver].getRd()
    
    New_Rating = pd.DataFrame(New_Rating)
    extracted_col = Race_Result['driverId']
    updated_ratings = ratings
    race_result = New_Rating.assign(LocationSpecificColumn=pd.Series(extracted_col).values)
        
    return updated_ratings, race_result, Race_Ratings, h2h
    
    

