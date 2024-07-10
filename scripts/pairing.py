import math
import numpy as np

from models.meteorite import Meteorite
from geopy.distance import geodesic
from typing import Union


# Weights parameters, adjustable
weights = {
    "distance": 1,
    "weathering_grade": 1,
    "petrographic_type": 2,
    "fayalite_content": 2,
    "ferrosilite_content": 2,
    "magnetic_susceptibility": 2,
}

# Define the parameter for each criterion (sigma i)
sigma = {
    "fayalite_content": 0.63,
    "ferrosilite_content": 0.61,
    "magnetic_susceptibility": 0.1
}


def calculate_distance(met_1: Meteorite, met_2: Meteorite) -> float:
    """
    Calculates and returns the distance between met_1 and met_2 in ms.

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
    - distance : float, the distance between two meteorites in km

    Returns:
    - p_dist : the importance factor of the distance
    """
    if distance < 0.2:
        p_dist = 1
    elif 0.2 <= distance < 0.3:
        p_dist = 0.9
    elif 0.3 <= distance < 0.4:
        p_dist = 0.8
    elif 0.4 <= distance < 0.5:
        p_dist = 0.7
    elif 0.5 <= distance < 0.7:
        p_dist = 0.6
    elif 0.7 <= distance < 0.9:
        p_dist = 0.5
    elif 0.9 <= distance < 1:
        p_dist = 0.4
    elif 1 <= distance < 1.5:
        p_dist = 0.3
    elif 1.5 <= distance < 2:
        p_dist = 0.2
    elif 2 <= distance < 3:
        p_dist = 0.1
    else:
        p_dist = 0.05
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

    if any([met_1.petrographic_type, met_2.petrographic_type]) == 3:
        return 1

    if delta == 0 or delta == 0.5:
        return 1
    elif delta == 1:
        return 0.75
    else:
        return 0  # disqualifying factor


def weath_factor(met_1: Meteorite, met_2: Meteorite) -> Union[float, int]:
    """
    Calculates the weathering grade factor between met_1 and met_2 : if the weathering
    grades are more than one grade apart, returns 0, returns 1 if same grade
    and 0.75 if one grade apart

    Args:
    - met_1 : meteorite one, object of class Meteorite, to be compared to met_2

    """
    if met_1.weathering_grade is not None and met_2.weathering_grade is not None:
        delta_w = met_1.weathering_grade - met_2.weathering_grade

    elif met_1.weathering_grade is None or met_2.weathering_grade is None:
        delta_w = 0

    if delta_w == 0:
        return 1
    elif delta_w == 1:
        return 0.75
    elif delta_w == 2:
        return 0.5
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

    factors["weathering_grade"] = weath_factor(met_1=met_1, met_2=met_2)
    """
    If the Fa content of both meteorites exists, it checks if the petrographic type of either meteorite is 3.0
    If it is, the Fa factor is set to 1
    If not, Fa factor is calculated
    If the Fa content does not exist for either meteorite, the Fa 1.

    Similarly, if the "ferrosilite" content of both meteorites exists, it checks if the petrographic
    type of either meteorite is 3.0 or 4.0.
    If it is, the "ferrosilite" factor is set to 1.
    Otherwise, it calculates the "ferrosilite" factor using a mathematical expression.
    If the "ferrosilite" content does not exist for either meteorite, the "ferrosilite" factor is set to 1.
    """

    if met_1.fa_content is not None and met_2.fa_content is not None:
        if met_1.petrographic_type == 3.0 or met_2.petrographic_type == 3.0:
            factors["fayalite"] = 1
        else:
            factors["fayalite"] = math.exp(
                -(((met_1.fa_content - met_2.fa_content)**2) / ((2 * sigma["fayalite_content"]) ** 2))
            )
    else:
        factors["fayalite"] = 1

    if met_1.fs_content is not None and met_2.fs_content is not None:
        if met_1.petrographic_type == 3.0 or met_2.petrographic_type == 3.0 or met_2.petrographic_type == 4.0 or met_2.petrographic_type == 4.0:
            factors["ferrosilite"] = 1
        else:
            factors["ferrosilite"] = math.exp(
                -(((met_1.fs_content - met_2.fs_content)**2) / ((2*sigma["ferrosilite_content"]) ** 2))
            )

    else:
        factors["ferrosilite"] = 1

    if met_1.mag_sus is not None and met_2.mag_sus is not None:
        factors["magnetic_susceptibility"] = math.exp(
            -(((float(met_1.mag_sus) - float(met_2.mag_sus)))**2 / (2 *sigma["magnetic_susceptibility"]) ** 2))
    else:
        factors["magnetic_susceptibility"] = 1

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
