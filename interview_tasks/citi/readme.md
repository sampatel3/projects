# Housing data task

# Given the housing data set of properties that are sales (sales.csv), write a function that takes a single property as lat,long and calculates the nearest 10 properties that sold.


main.py contains the function return_k_nearest_sold_properties that returns the property ids of the k nearest sold properties for a set of observed properties m

The following command line has been tested:

	python main.py --path housing_data/ --file sales.csv --lat 47.5112 47.7210 47.7379 --long -122.257 -122.319 -122.233
	
Execution returns the 10 nearest sold property ids for 3 observed properties with latitude and longitude coordinates: (47.5112, -122.257) (47.7210, -122.319) (47.7379, -122.233)

The nearest properties are defined using the Euclidean distance measure (based on Pythagorean theorem, L1 norm and the Scipy.spatial module - with the latter being the fastest) - more accurate distance measures that account for curvature can be included (e.g. Haversine, Vincenty) as distance functions

