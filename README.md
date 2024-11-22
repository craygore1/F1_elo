# F1 Elo Rating System

This project calculates Elo ratings for Formula 1 drivers, considering their performance against teammates and non-teammates. The ratings provide an estimate of driver skill by combining intra-team and inter-team comparisons into a single weighted average.

## Methodology
- Ratings are updated after each race with each driver having two seperate ratings, one against teammates and one against the rest of the grid. 
- The two ratings are blended with more weight given to the teammate ratings.
- The ratings are normalized to an average of 1500 in order to mitigate rating inflation/deflation across eras.
- Rookies are initialized at a rating of 1400 and all DNFs are discounted.
- Utilizes the [MultiElo](https://pypi.org/project/multielo/) Python package to calculate Elo ratings for matchups involving more than two drivers.

## Top 10 Career Peaks
| Rank | Name                 | Elo Rating          |
|------|----------------------|---------------------|
| 1    | Max Verstappen       | 1779.2414135742288 |
| 2    | Fernando Alonso      | 1767.0872739478875 |
| 3    | Michael Schumacher   | 1766.13133040331   |
| 4    | Juan Manuel Fangio   | 1751.8409132365075 |
| 5    | Sebastian Vettel     | 1735.952900707724  |
| 6    | Lewis Hamilton       | 1719.8160269248594 |
| 7    | Jim Clark            | 1705.156415348319  |
| 8    | Stirling Moss        | 1702.4422176585715 |
| 9    | Jackie Stewart       | 1700.5004768037325 |
| 10   | Ayrton Senna         | 1687.7800028151896 |

## Features
- Career projections based on a weighted comparison of the 5 drivers with most similar careers calculated using pearson correlation.
- Career projections based on a Long short-term memory neural network (LSTM). 


