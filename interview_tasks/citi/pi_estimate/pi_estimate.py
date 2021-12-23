# packages
import pandas as pd
import numpy as np
import argparse
import random
import math

n = 10000
radius = 1

x = np.array([(random.randrange(0, 10000, 1)/10000 - 0.5) * 2 for i in range(n)])
y = np.array([(random.randrange(0, 10000, 1)/10000 - 0.5) * 2 for i in range(n)])
euclidean_function = lambda x, y: np.sqrt(x**2 + y**2)
distance_from_origin = euclidean_function(x, y)

circle_counter = np.where(distance_from_origin <= radius, 1, 0)

pi_estimate = (np.sum(circle_counter) / n) * 4

#print(x)
#print(distance_from_origin)
#print(np.sum(circle_counter))
#print(circle_counter)
print(pi_estimate)
