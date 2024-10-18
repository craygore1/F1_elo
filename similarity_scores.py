# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import UnivariateSpline

Active_History = pd.read_csv('activehistory.csv')

def get_ratings_dict(df):
    ratings_dict = {}
    for _, row in df.iterrows():
        id_val = row['id']        
        ratings = row.drop(['id', 'name']).dropna().tolist()
        
        ratings_dict[id_val] = ratings
    return ratings_dict

Career = get_ratings_dict(Active_History)

def career_average(careers, career_length):
    temp = []
    for driver in careers:
        if len(careers[driver]) >= career_length and len(careers[driver]) <= career_length*1.2:
            temp.append(careers[driver][:career_length])
        
    temp = pd.DataFrame(temp)
    average_career = temp.mean()
    return average_career

def find_similar_drivers(target_driver, career_ratings_dict, length_coeff, metric='pearson'):
    """
    Finds the 5 drivers with the most similar career ratings to the target driver based on a specified metric.
    
    Parameters:
    - target_driver (str): The ID of the driver whose career is to be compared.
    - career_ratings_dict (dict): A dictionary where keys are driver IDs and values are lists of career ratings.
    - length_coeff (float): How much longer should the drivers' careers be than the target driver.
    - metric (str): The similarity metric to use ('pearson', 'euclidean', 'rmse', 'cosine').

    Returns:
    - List of 5 tuples: Each tuple contains the driver ID and similarity score.
    """
    
    if target_driver not in career_ratings_dict:
        return "Target driver not found in the dictionary."
    
    target_ratings = career_ratings_dict[target_driver]
    races_completed = len(target_ratings)
    
    min_career_length = int(races_completed + length_coeff)
    
    similarities = []
    
    for driver, ratings in career_ratings_dict.items():
        if driver == target_driver:
            continue
        
        if len(ratings) < min_career_length:
            continue
        
        ratings_to_compare = ratings[:races_completed]
        
        if len(ratings_to_compare) != races_completed:
            continue
        
        # Calculate similarity based on the chosen metric
        if metric == 'pearson':
            similarity = np.corrcoef(target_ratings, ratings_to_compare)[0, 1]
        elif metric == 'euclidean':
            similarity = -np.linalg.norm(np.array(target_ratings) - np.array(ratings_to_compare))
        elif metric == 'rmse':
            similarity = -np.sqrt(np.mean((np.array(target_ratings) - np.array(ratings_to_compare)) ** 2))
        elif metric == 'cosine':
            dot_product = np.dot(target_ratings, ratings_to_compare)
            norm_a = np.linalg.norm(target_ratings)
            norm_b = np.linalg.norm(ratings_to_compare)
            similarity = dot_product / (norm_a * norm_b)
        else:
            raise ValueError("Invalid metric specified. Choose from 'pearson', 'euclidean', 'rmse', 'cosine'.")
        
        similarities.append((driver, similarity))
    
    # Sort based on similarity score (descending for pearson and cosine, ascending for distance-based metrics)
    if metric in ['pearson', 'cosine']:
        most_similar_drivers = sorted(similarities, key=lambda x: x[1], reverse=True)[:5]
    else:
        most_similar_drivers = sorted(similarities, key=lambda x: x[1])[:5]
    
    return most_similar_drivers

def get_driver_list(target_driver, similar_drivers):
    drivers = [x[0] for x in similar_drivers]
    drivers = [target_driver] + drivers
    return drivers      

def project_future_ratings(target_driver, career_ratings_dict, x, similar_drivers):
    """
    Projects the future career of the target driver based on the average rating changes of the most similar drivers
    over the next x races, using cosine similarity as the weighting factor.
    
    Parameters:
    - target_driver (str): The ID of the driver whose future career is to be projected.
    - career_ratings_dict (dict): Dictionary where keys are driver IDs and values are lists of career ratings.
    - x (int): Number of races to project into the future.
    - similar_drivers (list): List of tuples where each tuple contains a driver ID and cosine similarity score.
    
    Returns:
    - List of projected ratings for the target driver over the next x races.
    """
    
    if target_driver not in career_ratings_dict:
        return "Target driver not found in the dictionary."
    
    # Get the current career ratings of the target driver
    target_ratings = career_ratings_dict[target_driver]
    current_race_count = len(target_ratings)
    
    # Initialize a list to store the projected changes from similar drivers
    projected_changes = []
    
    # Filter out drivers with negative similarity
    filtered_drivers = [(driver, coeff) for driver, coeff in similar_drivers if coeff > 0]
    if not filtered_drivers:
        return "Not enough positive similarity data to project future ratings."
    
    for driver, weight in filtered_drivers:
        if driver not in career_ratings_dict:
            continue
        
        similar_driver_ratings = career_ratings_dict[driver]
        
        # Ensure the similar driver has enough races beyond the target driver's current career length
        if len(similar_driver_ratings) > current_race_count + x:
            # Calculate the rating changes over the next x races
            future_ratings = similar_driver_ratings[current_race_count:current_race_count + x]
            current_ratings = similar_driver_ratings[current_race_count - 1:current_race_count - 1 + x]
            changes = [future_ratings[i] - current_ratings[i] for i in range(x)]
            # Apply the normalized weight
            changes = [change * weight for change in changes]
            projected_changes.append(changes)
            
            print(driver)
            print(weight)
            
    
    # Calculate the average change per race for each of the x future races
    if projected_changes:
        avg_changes = np.sum(np.array(projected_changes), axis=0)
    else:
        return "Not enough data to project future ratings."
    
    # Project the future ratings for the target driver
    projected_ratings = target_ratings[:]
    last_rating = projected_ratings[-1]
    
    for change in avg_changes:
        last_rating += change
        projected_ratings.append(last_rating)
    
    return projected_ratings[-x:]

def smooth_spline(ratings, smoothing_factor=0.5):
    x = np.arange(len(ratings))
    spline = UnivariateSpline(x, ratings)
    spline.set_smoothing_factor(smoothing_factor)
    return spline(x)

def smooth_moving_average(ratings, window_size=3):
    return np.convolve(ratings, np.ones(window_size) / window_size, mode='valid')

def apply_plot_style(ax, marker_size=6):
    """
    Parameters: ax : Axes object
    """
    colorblind_palette = ['#0072B2', '#D55E00', '#E69F00', '#009E73', '#F0E442', 
                          '#56B4E9', '#CC79A7', '#999999', '#F781BF', '#A65628']
    
    # Different line styles and markers for visual distinction
    linestyles = ['-', '--', '-.', ':', '-', '--', '-.', ':', '-', '--']
    markers = ['o', 's', 'D', '^', 'v', '>', '<', 'p', 'h', '*']
    
    # Get all line objects from the plot (ax)
    lines = ax.get_lines()
    
    # Apply colors, linestyles, and markers to each line
    for i, line in enumerate(lines):
        color = colorblind_palette[i % len(colorblind_palette)]   
        linestyle = linestyles[i % len(linestyles)]               
        marker = markers[i % len(markers)]                        
        line.set_color(color)
        line.set_linestyle(linestyle)
        line.set_marker(marker)
        line.set_markersize(marker_size)
        
def plot_career_races(careers, drivers):
    fig, ax1 = plt.subplots()
   
    for Driver in drivers:
        ser = careers[Driver]       
        ax1.plot(ser)
    
    
    ax1.set_xlabel('Career Race Number')
    ax1.set_ylabel("Rating")
    
    plt.title('Career Ratings', fontsize=16, fontweight='bold')
    
    ax1.set_ylim([1300, 1800])
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()    
    apply_plot_style(ax1, 2)
    
    ax1.legend(drivers)
    plt.show()
    
def plot_career_projection(target_driver, career_ratings_dict, projected_ratings):
    """
    Plots the target driver's career ratings so far and the future projection.
    
    Parameters:
    - target_driver (str): The ID of the driver whose career will be plotted.
    - career_ratings_dict (dict): Dictionary where keys are driver IDs and values are lists of career ratings.
    - projected_ratings (list): List of projected ratings for the next x races.
    - x (int): Number of races to project into the future.

    """
    
    if target_driver not in career_ratings_dict:
        print("Target driver not found in the dictionary.")
        return
    
    projected_ratings = list(projected_ratings)
    
    current_ratings = career_ratings_dict[target_driver]
    current_race_count = len(current_ratings)
    proj_race_count = len(projected_ratings)
    
    # Create race indices for the current and projected ratings
    current_race_indices = list(range(1, current_race_count + 1))
    projected_race_indices = list(range(current_race_count, current_race_count + proj_race_count + 1))
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    
    # Plot the current career ratings
    plt.plot(current_race_indices, current_ratings, label='Career So Far', color='blue', linestyle='-')

    # Plot the projected ratings as a red dashed line
    plt.plot(projected_race_indices, [current_ratings[-1]] + projected_ratings, 
             label='Future Projection', color='red', linestyle='--')
    plt.ylim([1300, 1800])
    plt.xlabel('Race Number')
    plt.ylabel('Rating')
    plt.title(f"Career Projection for Driver {target_driver}")
    plt.legend()
    
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.show()


target_driver = 'ayrton-senna'
proj_num = 50
               
similarity_score = find_similar_drivers(target_driver, Career, proj_num, metric='pearson')

projection = project_future_ratings(target_driver, Career, proj_num, similarity_score)
smooth_projection = smooth_moving_average(projection, window_size=5)

Drivers = get_driver_list(target_driver, similarity_score)
plot_career_races(Career, Drivers)

plot_career_projection(target_driver, Career, smooth_projection)

# =============================================================================
# average_career = career_average(Career, 50)
# 
# fig, ax1 = plt.subplots()
# 
# ax1.plot(average_career)
# plt.title('Average Career', fontsize=16, fontweight='bold')
# 
# ax1.set_ylim([1400, 1700])
# ax1.grid(True, linestyle='--', alpha=0.6)
# 
# plt.tight_layout()    
# apply_plot_style(ax1, 2)
# 
# plt.show()
# =============================================================================
        
    