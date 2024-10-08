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
isactive = alldiffs.rolling(5, axis=1).sum() != 0
onlyactive = numericblend[isactive]
onlyactive = onlyactive.iloc[:,5:]
meanhistory = onlyactive.mean(skipna=True)

Active_History = onlyactive.copy()
Active_History.insert(0,'id',Blended_History['id'])
Active_History.insert(1,'name',Blended_History['name'])

rollnum = 100
Rolling_Blend = onlyactive.rolling(rollnum, axis=1).mean(skipna=True).iloc[:, rollnum:]

Career_High_Average = Blended_History[['id','name']].copy()
Career_High_Average = pd.concat([Career_High_Average, Rolling_Blend.max(axis=1)], axis=1)

plt.figure(figsize=(10, 6))
Drivers = ["lewis-hamilton", "fernando-alonso", "sebastian-vettel", "max-verstappen", "lance-stroll"]
for Driver in Drivers:
    ser = Active_History[Active_History['id'] == Driver].select_dtypes(include='number')
    ser = ser.iloc[0,:]
    
    ser.plot(linestyle='-', linewidth=2)
    
    plt.title("Elo", fontsize=16, fontweight='bold')
    plt.xlabel("Race Number", fontsize=14)
    plt.ylabel("Rating", fontsize=14)
    
    plt.ylim([1300, 1900])
    plt.grid(True, linestyle='--', alpha=0.6)
    
    plt.tight_layout()
    
plt.legend(Drivers)
plt.show()