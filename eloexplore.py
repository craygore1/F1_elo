# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 14:53:08 2024

@author: woods
"""

import pandas as pd
import racemodule
from multielo import MultiElo, Player, Tracker
import matplotlib.pyplot as plt

Blended_History = pd.read_csv('blendhistory.csv')
Rating_History = pd.read_csv('history.csv')
Team_History = pd.read_csv('teamhistory.csv')

numericblend = Blended_History.select_dtypes(include='number')
alldiffs = numericblend.diff(axis=1)
isactive = alldiffs.rolling(5, axis=1).mean() > 0
onlyactive = numericblend[isactive]
meanhistory = onlyactive.mean(skipna=True)

plt.figure(figsize=(10, 6))

# Plot the Line with Settings
meanhistory.plot(color='#1f77b4', linestyle='-', linewidth=2)

# Add Titles and Labels
plt.title("Average Rating of Active Drivers", fontsize=16, fontweight='bold')
plt.xlabel("Race Number", fontsize=14)
plt.ylabel("Rating", fontsize=14)

plt.ylim([1400, 1800])
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()