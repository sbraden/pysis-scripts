#rolotools.py

import numpy as np
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label


def compute_incidence(subsolarlat, subsolarlon, lat, lon):
    """ 
    Computes incidence angles
    
    Args:
        subsolarlat: subsolar latitude at observation time (in degrees)
        subsolarlon: subsolar longitude at observation time (in degrees)
        lat: latitude of the image or point of interest (in degrees)
        lon: longitude of the image or point of interest (in degrees)

    Returns:
        incidence angle in degrees for point or image of interest
    """
    deltalat = np.radians(np.abs(subsolarlat - lat))
    deltalon = np.radians(np.abs(subsolarlon - lon))
    incidence = np.degrees(np.arccos(np.cos(deltalat) * np.cos(deltalon)))

    return incidence


def compute_emission(subearthlat, subearthlon, lat, lon):
    """
    Computes emission angles

    Args:
        subearthlat: subearth latitude at observation time (in degrees)
        subearthlon: subearth longitude at observation time (in degrees)
        lat: latitude of the image or point of interest (in degrees)
        lon: longitude of the image or point of interest (in degrees)   

    Returns:
        emission angle in degrees for the point or image of interest
    """
    deltalat = np.radians(np.abs(subearthlat - lat))
    deltalon = np.radians(np.abs(subearthlon - lon))
    emission = np.degrees(np.arccos(np.cos(deltalat) * np.cos(deltalon)))

    return emission


