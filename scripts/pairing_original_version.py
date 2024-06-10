import math
import numpy as np

from models.meteorite import Meteorite
from geopy.distance import geodesic
from typing import Union


# Weights parameters, adjustable
weights = {
    "distance": 1,
    "petrographic_type": 1,
    "weathering_grade": 1,
    "fayalite_content": 2,
    "ferrosilite_content": 2,
    "magnetic_susceptibility": 2,
}

# Define the parameter for each criterion (sigma i)
sigma = {
    "weathering_grade": 1.0,
    "fayalite_content": 0.6,
    "ferrosilite_content": 0.7,
    "magnetic_susceptibility": 0.1,
}


def calculate_distance(met_1: Meteorite, met_2: Meteorite) -> float:
    """
    Calculates and returns the distance between met_1 and met_2 in kms.

    Args:
    - met_1 : object of the class Meteorite, with obj.position = tuple(latitute, longitude)
    - met_2 : object of the class Meteorite, with obj.position = tuple(latitute, longitude)

    Returns:
    - distance in kilometers
    """

    coord_1 = met_1.position
    coord_2 = met_2.position
    distance = geodesic(coord_1, coord_2).kilometers

    return distance


def dist_factor(distance: float) -> float:
    """
    Calculates and returns the distance factor between two meteorites, takes only the
    distance as argument.

    Args:
    - distance : float, the distance between two meteorites

    Returns:
    - p_dist : the importance factor of the distance
    """
    if distance < 0.2:
        p_dist = 1
    elif distance < 0.5:
        p_dist = 0.9
    elif distance < 1:
        p_dist = 0.8
    elif distance < 2:
        p_dist = 0.7
    elif distance < 3:
        p_dist = 0.6
    elif distance < 5:
        p_dist = 0.3
    else:
        p_dist = 0.1
    return p_dist


def petro_factor(met_1: Meteorite, met_2: Meteorite) -> Union[float, int]:
    """
    Calculates the petrographic factor between met_1 and met_1 : if the petrographic groups are
    farther than one category apart, returns 0, return 1 if perfect match and 0.75 if 1 group apart

    Args:
    - met_1 : meteorite one, object of class Meteorite, to be compared to met_2
    - met_2 : meteorite two, object of class Meteorite, to be compared to met_1

    Returns :
    - petrographic factor, either 1 or 0
    """

    if met_1.petrographic_type is not None and met_2.petrographic_type is not None:
        delta = met_1.petrographic_type - met_2.petrographic_type

    elif met_1.petrographic_type is None or met_2.petrographic_type is None:
        delta = 0

    if delta == 0:
        return 1
    else:
        return 0


def calculate_factor(met_1: Meteorite, met_2: Meteorite, sigma: dict):
    """
    Calculates the relation factors between met_1 and met_2 and returns them as dict

    Args:
    - met_1 : meteorite one, object of the class Meteorite, to compare to met_2
    - met_2 : meteorite two, object of the class Meteorite, to compare to met_1
    - sigma : dict, sigma value for each factor to be calculated

    Returns :

    - factors : a dictionnary containing the relation factors between met_1 and met_2
    """

    factors = {}

    # Calculate the factor for each criterion
    factors["distance"] = dist_factor(calculate_distance(met_1=met_1, met_2=met_2))
    
    factors["petrographic_type"] = petro_factor(met_1=met_1, met_2=met_2)

    """
    If the "fayalite" content of both meteorites exists, it checks if the petrographic type of either meteorite is 3.0. 
    If it is, the "fayalite" factor is set to 1. 
    Otherwise, it calculates the "fayalite" factor using a mathematical expression.
    If the "fayalite" content does not exist for either meteorite, the "fayalite" factor is set to 1.

    Similarly, if the "ferrosilite" content of both meteorites exists, it checks if the petrographic type of either meteorite is 3.0 or 4.0.
    If it is, the "ferrosilite" factor is set to 1. 
    Otherwise, it calculates the "ferrosilite" factor using a mathematical expression. 
    If the "ferrosilite" content does not exist for either meteorite, the "ferrosilite" factor is set to 1.
    """

    if met_1.fa_content is not None and met_2.fa_content is not None:
        if met_1.petrographic_type == 3.0 or met_2.petrographic_type == 3.0:
            factors["fayalite"] = 1
        else:
            factors["fayalite"] = math.exp(-abs(met_1.fa_content - met_2.fa_content) / (2 * sigma["fayalite_content"] ** 2))
    else:
        factors["fayalite"] = 1

    if met_1.fs_content is not None and met_2.fs_content is not None:
        if met_1.petrographic_type == 3.0 or met_2.petrographic_type == 3.0 or met_2.petrographic_type == 4.0 or met_2.petrographic_type == 4.0  :
            factors["ferrosilite"] = 1
        else:
            factors["ferrosilite"] = math.exp(
            -abs(met_1.fs_content - met_2.fs_content) / (2 * sigma["ferrosilite_content"] ** 2)
            )
    else:
        factors["ferrosilite"] = 1
        
    # Calculate "Weathering Grade" factor
    if met_1.weathering_grade is not None and met_2.weathering_grade is not None:
        factors["weathering_grade"] = math.exp(
            -(((met_1.weathering_grade - met_2.weathering_grade)/2) **2 ) / (2 * (sigma["weathering_grade"]) ** 2)
            )
    else:
        factors["weathering_grade"] = 1

    factors["magnetic_susceptibility"] = math.exp(
        -abs(float(met_1.mag_sus) - float(met_2.mag_sus)) / (2 * sigma["magnetic_susceptibility"] ** 2)
        )

    return factors


def calculate_pairing_probability(met_1: Meteorite, met_2: Meteorite) -> float:
    """
    Calculate the product of probabilities weighted by their respective weights using
    factors calculated with calculate_factors() function;

    Args:
    - met_1 : meteorite one, object of the class Meteorite, to compare to met_2
    - met_2 : meteorite two, object of the class Meteorite, to compare to met_1

    Returns :
    - pairing_probability : the probability of two meteorites being paired
    """

    factors = calculate_factor(met_1=met_1, met_2=met_2, sigma=sigma)
    product = np.prod(np.power(list(factors.values()), list(weights.values())))

    # Calculate the pairing probability using the geometric mean
    pairing_probability = np.power(product, 1 / sum(weights.values()))

    return pairing_probability
