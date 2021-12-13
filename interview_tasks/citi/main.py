# packages
import pandas as pd
import numpy as np
import argparse
import os
import time
import scipy.spatial
import math


# functions

def euclidean_distance(cord1, cord2):
    '''
    Function calculates the euclidean distance using Pythagorean theorem
    :param cord1: (latitude, longitude) (m x 2 array)
    :param cord2: (latitude, longitude) (n x 2 array)
    :return: euclidean distance (m x n array)
    '''
    euclidean_function = lambda cord1, cord2: np.sqrt(np.sum((cord1 - cord2) ** 2, axis=1))
    return np.apply_along_axis(func1d=euclidean_function, axis=1, arr=cord1, cord2=cord2)


def norm_euclidean_distance(cord1, cord2):
    '''
    Function calculates the euclidean distance using the L1 norm
    :param cord1: (latitude, longitude) (m x 2 array)
    :param cord2: (latitude, longitude) (n x 2 array)
    :return: euclidean distance (n x n array)
    '''
    euclidean_function = lambda cord1, cord2: np.linalg.norm(cord1 - cord2, axis=1)
    return np.apply_along_axis(func1d=euclidean_function, axis=1, arr=cord1, cord2=cord2)


def scipy_euclidean_distance(cord1, cord2):
    '''
    Function calculates the euclidean distance using scipy,spatial module
    :param cord1: (latitude, longitude) (m x 2 array)
    :param cord2: (latitude, longitude) (n x 2 array)
    :return: euclidean distance (m x n array)
    '''
    return scipy.spatial.distance.cdist(XA=cord1, XB=cord2, metric='euclidean')


def load_sales_df(filepath, filename):
    '''
    Function creates a dataframe of the sale data
    :param filepath: filepath of the sale information (str)
    :param filename: filename of the sale information (str)
    '''
    return pd.read_csv(filepath_or_buffer=os.path.join(filepath, filename), sep=',', header=0)


def return_k_nearest_sold_properties(k_nearest, m_obs_array, n_sold_df, distance_fun):
    '''
    Function that returns the IDs of the k nearest sold properties for a set of observed properties m
    :param k_nearest: number of nearest properties to return (int)
    :param m_obs_array: array of (m observed properties) x (latitude, longitude) (m x 2 array)
    :param n_sold_df: dataframe of (n sold properties) by (id, latitude, longitude) (n x 3 dataframe)
    :param distance_fun: distance function (euclidean, haversine, vincenty etc.)
    :return: array containing id of the k nearest sold properties for each observed property m (m x k list)
    '''

    start = time.perf_counter() * 1000  # start timer
    cord1 = m_obs_array  # observed properties array (m x 2 array)
    cord2 = n_sold_df[['latitude', 'longitude']].to_numpy() # sold properties array (n x 2 array)
    distance = distance_fun(cord1, cord2).T # calculate distance  (m x n array)
    idx = np.argpartition(distance, k_nearest, axis=0)  # indices
    ids = n_sold_df.id.to_numpy() # property ids
    ids_idx = np.take(a=ids, indices=idx[:k_nearest].T) # partition property ids by indices
    end = time.perf_counter() * 1000 # end timer

    print(f"Processing time ({distance_fun.__name__} distance function): {round(end - start, 5)} milliseconds")

    return ids_idx


# main
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=os.getcwd(), type=str, help='filepath for sale information')
    parser.add_argument('--file', default='sales.csv', type=str, help='filename for sale information')
    parser.add_argument('--lat', type=float, nargs='+', help='latitude decimal coordinate(s)')
    parser.add_argument('--long', type=float, nargs='+', help='longitude decimal coordinate(s)')
    args = parser.parse_args()

    sales_df = load_sales_df(filepath=args.path, filename=args.file)
    sales_df['latitude'] = sales_df.loc[:, 'lat'].map(lambda x: math.radians(x))
    sales_df['longitude'] = sales_df.loc[:, 'long'].map(lambda x: math.radians(x))
    n_sold_df = sales_df[['id', 'latitude', 'longitude']]
    m_obs_array = np.array(list(zip(map(lambda x: math.radians(x), args.lat),
                                    map(lambda x: math.radians(x), args.long))))

    ids1 = return_k_nearest_sold_properties(k_nearest=10,
                                            m_obs_array=m_obs_array,
                                            n_sold_df=n_sold_df,
                                            distance_fun=euclidean_distance)
    print(ids1)

    ids2 = return_k_nearest_sold_properties(k_nearest=10,
                                            m_obs_array=m_obs_array,
                                            n_sold_df=n_sold_df,
                                            distance_fun=norm_euclidean_distance)
    print(ids2)

    ids3 = return_k_nearest_sold_properties(k_nearest=10,
                                            m_obs_array=m_obs_array,
                                            n_sold_df=n_sold_df,
                                            distance_fun=scipy_euclidean_distance)
    print(ids3)

    # Check (47.5112, -122.257)
    # cord1 = m_obs_array[0]
    # cord2 = n_sold_df[['latitude', 'longitude']].to_numpy()
    # euclidean_function = lambda cord1, cord2: np.sqrt(np.sum((cord1 - cord2) ** 2, axis=1))
    # sales_df['distance'] = euclidean_function(cord1, cord2).T
    # nearest_k_df = sales_df.nsmallest(10, 'distance')
    # print(np.sort(nearest_k_df['id'].to_numpy()) == np.sort(ids1)) # TRUE

    # python main.py --path housing_data/ --file sales.csv --lat 47.5112 47.7210 47.7379 --long -122.257 -122.319 -122.233