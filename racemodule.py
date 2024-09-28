# -*- coding: utf-8 -*-

def race_to_head_to_head(results):
    """
    Converts a race result list into head-to-head vectors.
    
    Parameters:
        results: A list that represents a single race's finish order. 
                                 E.g., ["john", "matt", "bob"]
    
    Returns:
        dict: A dictionary where the key is the participant and the value is the head-to-head vector.
    """
    # Step 1: Gather all unique participants
    participant_idx = {participant: idx for idx, participant in enumerate(results)}

    # Step 2: Create a dictionary to store head-to-head vectors
    head_to_head_vectors = {participant: [0] * (len(results) - 1) for participant in results}

    # Step 3: Update head-to-head vectors based on person results
    for i in range(len(results)):
        current_participant = results[i]
        for j in range(i + 1, len(results)):
            opponent = results[j]
            # Current participant beat opponent
            head_to_head_vectors[current_participant][participant_idx[opponent] - 1] = 1

    return head_to_head_vectors

def extract_race(year, racenumber, df):
    '''
    Parameters
    ----------
    year : Year of race
    racenumber : Race number in desired year
    df: DataFrame containing all results

    Returns
    -------
    race_results : Cleaned race results
    driver_dnfs: list of dnfs
    '''
    driver_dnfs = list()
    
    year_results = df[df['year'] == year]
    race_results = year_results[year_results['round'] == racenumber]
    
    race_results = race_results[['raceId','round','positionDisplayOrder',
                                 'positionNumber', 'driverId', 'constructorId']]
    
    if race_results.empty:
        return race_results, driver_dnfs
    else:
        driver_dnfs = race_results[race_results['positionNumber'].isna()]
        race_results = race_results.drop(driver_dnfs.index)
    return race_results, driver_dnfs
    

