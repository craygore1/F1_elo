# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import glicko2
import racemodule

All_Races = pd.read_csv('f1db-races-race-results.csv')
All_Drivers = pd.read_csv('f1db-drivers.csv')

Driver_Glicko = {driver: idx for idx, driver in enumerate(All_Drivers.id)}

for row in All_Drivers.itertuples():
    temp = glicko2.Player()
    driver = row.id
    Driver_Glicko[driver] = temp