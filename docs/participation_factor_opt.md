# Dashboard for visualising the impact of the optimisation algorithm

## Visualisation of a single algorithm
### Starting situation
![alt text](image-1.png)
![alt text](image-2.png)
+ source of the functions in src/notebooks/gate3/Gate3.ipynb

### After optimisation
#### Energy amounts
![alt text](image.png)
+ Filtering of timestamps to display different optimisation targets per time horizon
+ source of the function: src/modules/pf_calculations.py -> plot_stacked_gain_loss_sortable

#### Fairness metrics
![alt text](image-3.png)
+ Implementation: independent of the metric used / the metric is interchangeable
+ source of the functions in src/notebooks/gate3/Gate3.ipynb

## Comparison of different algorithms

+ Inspiration
![alt text](image-4.png)
