# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


All_Races = pd.read_csv('f1db-races-race-results.csv')

Blended_History = pd.read_csv('blendhistory.csv')
Rating_History = pd.read_csv('history.csv')
Team_History = pd.read_csv('teamhistory.csv')
Quali_History = pd.read_csv('qualihistory.csv')

def get_active_history(history): # Function to get active history
    numeric_blend = history.select_dtypes(include='number')
    all_diffs = numeric_blend.diff(axis=1)

    # Identify active rows where there is a sum of non-zero differences in a rolling window
    is_active = all_diffs.rolling(5, axis=1).sum() != 0

    only_active = numeric_blend[is_active]
    only_active = only_active.iloc[:, 5:]

    active_history = only_active.copy()
    active_history.insert(0, 'id', history['id'])
    active_history.insert(1, 'name', history['name'])

    return active_history

Active_History = get_active_history(Blended_History)
Active_Quali = get_active_history(Quali_History)

def get_recent_rating(history, drivers, n):
    
    filtered_history = history[history['id'].isin(drivers)]
    filtered_ratings = filtered_history.iloc[:, 2:]
    
    recent_ratings = filtered_ratings.apply(lambda row: row.dropna().iloc[-n:].tolist() if not row.dropna().empty else [np.nan]*n, axis=1)
    recent_ratings = pd.DataFrame(recent_ratings.tolist(), columns=[f"rating_{i+1}" for i in range(n)])
    
    results = filtered_history.iloc[:, :2].copy()
    results = results.reset_index(drop=True)
    results = pd.concat([results, recent_ratings], axis=1)
    
    return results
    
    
def get_year_round(race_numbers):
    race_mask = All_Races['raceId'].isin(race_numbers)  # Mask to filter matching race IDs
    filtered_races = All_Races.loc[race_mask, ['raceId', 'year', 'round']].drop_duplicates('raceId')
    
    year = filtered_races['year']
    myround = filtered_races['round']
    return year, myround

def get_seasons(df): #FUnction to get season starts and ends
    starts = All_Races[All_Races['round'] == 1]['raceId']
    starts = list(dict.fromkeys(starts))
    ends = starts[1:]
    ends = [x-1 for x in ends]
    return starts, ends                          

def adjust_fig_width(ax, xtick_labels, label_fontsize=10, padding=2):
    max_label_length = max([len(label) for label in xtick_labels])
    
    # Estimate required figure width (scale factor based on font size)
    width_scale = max_label_length / 5  # Adjust scaling factor if necessary
    
    # Get the current figure size
    fig_width, fig_height = ax.figure.get_size_inches()
    
    # Set new width proportional to the label length
    ax.figure.set_size_inches(fig_width + width_scale + padding, fig_height)

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

def set_myxticks(xtick_positions, min_val, max_val, start_year=1950):
    # Filter the xtick positions to include only those within the min and max range
    filtered_xticks = [pos for pos in xtick_positions if min_val <= pos <= max_val]
    
    # Generate corresponding labels starting from the base year and matching filtered ticks
    labels = list(range(start_year, start_year + len(xtick_positions)))
    filtered_labels = [labels[xtick_positions.index(pos)] for pos in filtered_xticks]
    
    filtered_xticks = [pos-5 for pos in filtered_xticks]
    plt.xticks(filtered_xticks, filtered_labels)
    return str(filtered_labels)

def plot_career(df, history, drivers, title):
    fig, ax1 = plt.subplots()
    globmin = 5000
    globmax = 0
    racemin = 5000
    racemax = 0
    
    starts, ends = get_seasons(df)
    for i, Driver in enumerate(drivers):
        ser = history[history['id'] == Driver].select_dtypes(include='number')
        ser = ser.iloc[0,:]
        
        if int(ser.first_valid_index()) < globmin:
            globmin = int(ser.first_valid_index()) - 10
        
        if int(ser.last_valid_index()) > globmax:
            globmax = int(ser.last_valid_index()) + 10
        
        if int(ser.first_valid_index()) < racemin:
            racemin = int(ser.first_valid_index())
        
        if int(ser.last_valid_index()) > racemax:
            racemax = int(ser.last_valid_index())
        
        ax1.plot(ser.index, ser)
        
        #line = plt.gca().get_lines()[0]  # Get the first line object
        #x_values = line.get_xdata()
        #y_values = line.get_ydata()
    
    racenumbers = range(racemin, racemax+1)
    
    years, rounds = get_year_round(racenumbers)
    years = list(dict.fromkeys(years))
    
    myticklabels = set_myxticks(starts, racemin, racemax)
    
    ax1.set_xlabel('Year')
    ax1.set_ylabel("Rating")
    ax1.set_xlim([globmin, globmax])

    
    adjust_fig_width(ax1, myticklabels, padding=8)
    
    plt.title(title, fontsize=16, fontweight='bold')
    
    ax1.set_ylim([1200, 1800])
    ax1.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()    
    apply_plot_style(ax1, 2)
    
    ax1.legend(drivers)
    plt.show()

def find_largest_changes(df):

    rating_data = df.iloc[:, 2:].copy()
    
    # Calculate absolute differences between successive columns
    diff_data = np.abs(rating_data.diff(axis=1))
    
    flat_data = []
    for row_idx, row in diff_data.iterrows():
        for col_idx, value in enumerate(row):
            if not np.isnan(value):  # Ignore NaN differences
                flat_data.append((value, df.iloc[row_idx, 0], df.iloc[row_idx, 1], col_idx + 5))  # Include id, name, and column index
    
    flat_data = sorted(flat_data, key=lambda x: x[0], reverse=True)
    
    # Create a dataframe from the results
    result_df = pd.DataFrame(flat_data, columns=["max_change", "id", "name", "race_number"])
    
    cols = result_df.columns.to_list()
    cols = cols[1:] + [cols[0]]
    
    result_df = result_df[cols]
    
    return result_df


Drivers = ["max-verstappen", "lando-norris", 'george-russell', 'charles-leclerc']
plot_career(All_Races, Active_History, Drivers, 'Driver History')

big_diff = find_largest_changes(Active_History)

current_grid = ["max-verstappen", "lando-norris", 'george-russell', 'charles-leclerc',
                'fernando-alonso', 'lewis-hamilton', 'sergio-perez', 'lance-stroll', 
                'alexander-albon', 'oscar-piastri', 'esteban-ocon', 'pierre-gasly',
                'liam-lawson', 'yuki-tsunoda', 'guanyu-zhou', 'valtteri-bottas',
                'nico-hulkenberg', 'kevin-magnussen', 'carlos-sainz-jr', 'franco-colapinto']
grid_rating = get_recent_rating(Active_History, current_grid, 5)

Active_History.to_csv('activehistory.csv', index=False)

