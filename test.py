# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:18:55 2024

@author: woods
"""

import glicko2

p1 = glicko2.Player()
p2 = glicko2.Player()
p3 = glicko2.Player()

p1.update_player([1500,1500],[350,350], [1,1])
p2.update_player([1500,1500],[350,350], [0,0])
p3.did_not_compete()

results = ["john", "bob", "matt", 'cheryl']

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
    