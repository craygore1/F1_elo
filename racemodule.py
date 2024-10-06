# -*- coding: utf-8 -*-
import pandas as pd

def race_to_h2h(results, teams):
    """
    Converts a race result list into head-to-head vectors (omits teammates).
    
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

def race_to_h2h_team(results):
    """
    Converts a race result list into head-to-head vectors (omits teammates).
    
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
    
    
    # Step 3: Update head-to-head vectors based on person results
    for i, driver in enumerate(participant_idx):
        current_participant = driver
        for j in range(i, len(results)-1):
            head_to_head_vectors[current_participant][j] = 1

    return head_to_head_vectors

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
    ratingss : Current ratingss and RD of all drivers
    glicko : glicko class instances for all drivers
    df : dataframe of all races

    Returns
    -------
    updated_ratingss : updated dataframe of ratingss and rd for all drivers
    race_result : new ratingss for only the drivers in the race

    '''
    Race_Result, Dnfs = extract_race(racenumber ,df)
    h2h, opponents = race_to_h2h(Race_Result['driverId'],Race_Result['constructorId'])
    
    New_Rating = []

    for i, driver in enumerate(Race_Result['driverId']):
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
        
    return updated_ratings, race_result

def run_race_team(racenumber, ratings, glicko, df):
    race, dnf = extract_race(racenumber, df)
    
    teamdict = {k: v for k, v in race.groupby("constructorId")}
    teamdict = {key: df for key, df in teamdict.items() if df.shape[0] > 1}
    
    h2h_dict = {}
    New_Rating = []
    for team in teamdict.keys():
        h2h = race_to_h2h_team(teamdict[team]['driverId'])
        h2h_dict[team] = h2h
    
    for team in teamdict.keys():
        for i, driver in enumerate(h2h_dict[team]):
            Race_Ratings = ratings[ratings['id'].isin(teamdict[team]['driverId'])]
            Race_Ratings = Race_Ratings[Race_Ratings['id'].isin([driver]) == False]
    
            glicko[driver].update_player(Race_Ratings['Rating'], 
                                                Race_Ratings['RD'], h2h_dict[team][driver])
             
            New_Rating.append(glicko[driver].getRating())
             
            ratings.loc[ratings['id'] == driver, 'Rating'] = glicko[driver].getRating()
            ratings.loc[ratings['id'] == driver, 'RD'] = glicko[driver].getRd()

    updated_ratings = ratings
         
    return updated_ratings

def results_without_teammates(df):
    """
    Given a dataframe of race results, returns a dictionary where each key is a driver's name
    and the value is a dataframe of race results with only their teammates removed.
    """
    # Create a dictionary to store the results for each driver
    results_dict = {}

    # Iterate over unique drivers
    for driver in df['driverId'].unique():
        # Get the team of the current driver
        driver_team = df.loc[df['driverId'] == driver, 'constructorId'].iloc[0]

        # Filter out only the teammates (same team but different driver)
        filtered_results = df[~((df['constructorId'] == driver_team) & (df['driverId'] != driver))]

        # Store the filtered results in the dictionary
        results_dict[driver] = filtered_results

    return results_dict

def elo_race(racenumber, ratings, elo, df):
    race, dnf = extract_race(racenumber, df)
    temp = results_without_teammates(race)
    
    resultsdict = {}
    for driver in temp.keys():
        Race_Ratings = ratings.merge(temp[driver], left_on='id', right_on = 'driverId')
        Race_Ratings = Race_Ratings.sort_values(by = ['positionDisplayOrder'])
        Race_Ratings = Race_Ratings.drop_duplicates(subset = 'driverId', keep='first')
        resultsdict[driver] = Race_Ratings
        
    for person in race['driverId']:
        tempdf = resultsdict[person].reset_index(drop=True)
        person_idx = tempdf[tempdf['driverId'] == person].index
        result = resultsdict[person]['rating']
        new_rating = elo.get_new_ratings(result)[person_idx]
        ratings.loc[ratings['id'] == person, 'rating'] = new_rating
    
    updated_ratings = ratings
    
    return updated_ratings

def results_only_teammates(df):
    """
    Given a dataframe of race results, returns a dictionary where each key is a driver's name
    and the value is a dataframe of race results with only their teammates removed.
    """
    # Create a dictionary to store the results for each driver
    results_dict = {}

    # Iterate over unique drivers
    for driver in df['driverId'].unique():
        # Get the team of the current driver
        driver_team = df.loc[df['driverId'] == driver, 'constructorId'].iloc[0]

        # Filter out only the teammates (same team but different driver)
        filtered_results = df[df['constructorId'] == driver_team]

        # Store the filtered results in the dictionary
        results_dict[driver] = filtered_results

    return results_dict

def remove_single_row_dfs(df_dict):
    """Removes DataFrames with only one row from a dictionary of DataFrames."""

    new_df_dict = {}
    for key, df in df_dict.items():
        if df.shape[0] > 1:
            new_df_dict[key] = df

    return new_df_dict

def elo_race_team(racenumber, ratings, elo, df):
    race, dnf = extract_race(racenumber, df)
    temp = results_only_teammates(race)
    temp = remove_single_row_dfs(temp)
    
    resultsdict = {}
    for driver in temp.keys():
        Race_Ratings = ratings.merge(temp[driver], left_on='id', right_on = 'driverId')
        Race_Ratings = Race_Ratings.sort_values(by = ['positionDisplayOrder'])
        Race_Ratings = Race_Ratings.drop_duplicates(subset = 'driverId', keep='first')
        resultsdict[driver] = Race_Ratings
        
    for person in temp.keys():
        tempdf = resultsdict[person].reset_index(drop=True)
        person_idx = tempdf[tempdf['driverId'] == person].index
        result = resultsdict[person]['rating']
        new_rating = elo.get_new_ratings(result)[person_idx]
        ratings.loc[ratings['id'] == person, 'rating'] = new_rating
    
    updated_ratings = ratings
    
    return updated_ratings