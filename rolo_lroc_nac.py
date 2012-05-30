#!/usr/bin/env python
import re
from glob import iglob
from math import floor
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label
import numpy as np
import scipy

# Sarah Braden
# 4/3/2012
# Must use isis 3.3.1
# pysis script to project ROLO data to LROCNAC footprints 
# and get data

# "rolo observation" = set of multispectral rolo files
# "rolo image" = one rolo file of a single band

# processes data: raw input and returns processed data
# plots: give processed data

# ROLO images to use
# get this input from the command line
rolo_observation = 'mm185801'
# perhaps change rolo_observation to rolo_set: it makes more sense

# LROC NAC directory
nacdir = '/home/sbraden/NACCAL/mm1858/'
# ROLO directory
rolodir = '/home/sbraden/ROLO/' + rolo_observation


def compute_emission_angles(rolo_observation, angle_dict):
    """ compute emission angles
    
    Args:
        image_name: which set of images do we want angles for?
        angle_dict: dictionary of angles for images

    Returns:
        emission angle the center of the image
    """
    deltalat = np.radians(np.abs(angle_dict[rolo_observation]['selat'] - pix['lat']))
    deltalon = np.radians(np.abs(angle_dict[rolo_observation]['selon'] - pix['lon']))
    emission = np.degrees(np.arccos(np.cos(deltalat) * np.cos(deltalon)))
    return emission

def compute_incidence_angles(rolo_observation, angle_dict):
    """ compute incidence angles
    
    Args:
        image_name: which set of images do we want angles for?
        angle_dict: dictionary of angles for images

    Returns:
        incidence angle for the center of the image
    """
    deltalat = np.radians(np.abs(angle_dict[rolo_observation]['sslat'] - pix['lat']))
    deltalon = np.radians(np.abs(angle_dict[rolo_observation]['sslon'] - pix['lon']))
    incidence = np.degrees(np.arccos(np.cos(deltalat) * np.cos(deltalon)))
    return incidence

# this line needed to get info from isis.campt
content_re = re.compile(r'(Group.*End_Group)', re.DOTALL)

def get_pho_angles(img_name):    
        output = isis.campt.check_output(from_=img_name)
        output = content_re.search(output).group(1) 
        phase_angle = parse_label(output)['GroundPoint']['Phase']
        incidence_angle = parse_label(output)['GroundPoint']['Incidence']
        emission_angle = parse_label(output)['GroundPoint']['Emission']
        return phase_angle, incidence_angle, emission_angle


def multispec_rolo(rolo_observation, img_name):
    """ Find the avg and stdev of radiance in ROLO observation projected to NAC
    footprint, for each band.

    Args: 
        rolo_observation: The rolo_observation that the images are from.
        img_name: The LROC NAC image that the ROLO data is reprojecting to.

    Returns:
        dictionary of avg and stdev radiance for each band in rolo indexed 
        by NAC image.
    """


def photomet_rolo(img_name, rolo_angle_dict):
    """ Compute and return photometric properties of a projected rolo image
    Args: LROC NAC frame

    Returns: 
        clat, clon, emission, incidence, LS ratio
    """
    ext_len = -len('.IMG')
    no_ext = img_name[:ext_len]
    rolo_band = rolodir + '/footprints/' + no_ext + rolo_observation + 'band0001.cub'
    # get clat and clon for next calculation (just from one image) 
    #mapping = parse_file_header('nac_eqr.map')['Mapping']
    #clon = mapping['CenterLongitude']
    #clat = mapping['CenterLatitude']
    #isis.cam2map(from_=trim_name, to=proj_name, pixres='map', map='nac_eqr.map')

    # add clat and clon as arguments that need to be passed
    emission = compute_emission_angles(rolo_observation, rolo_angle_dict)
    incidence = compute_incidence_angles(rolo_observation, rolo_angle_dict)

    # calculate Lommel-Seeliger factor for each point
    # L-S = cos(i) / ( cos(e) + cos(i) )
    LommelSeeliger = np.cos( np.radians(incidence) ) / ( np.cos( np.radians(emission) ) + np.cos( np.radians(incidence)))
    # LS value at Sub Earth point
    LSsubearth = 0.4590 # I think I need to compute this for each image.
    # compute LS ratio for each point in image
    LSratio = LSsubearth / LommelSeeliger
    return clat, clon, emission, incidence, LSratio

def project_rolo(rolo_observation, img_name):
    """" Reproject ROLO data onto LROC NAC footprints

    Args:
        rolo_observation: The rolo_observation that the images are from.
        img_name: The LROC NAC image that the ROLO data is reprojecting to.
    """
    rolo_images = iglob(rolodir + '/*.cub') # all bands of rolo observation
    ext_len = -len('.IMG')
    no_ext = img_name[:ext_len]
    for rolo_name in rolo_images:
        isis.map2map(from_=rolo_name, to=rolodir + '/footprints/' + no_ext+rolo_name, 
                    map='nac_eqr.map', pixres='mpp', 
                    resolution=7000, interp='nearestneighbor', 
                    defaultrange='map')


def main():
    images = iglob('*.IMG')
    
    pho_angles = [(img_name, get_pho_angles(img_name)) for img_name in images]
    # import pickle
    # pickle.dump(obj, open('myfile.dat','w'))
    # pickle.load(open('myfile.dat'))

    dtype = {
        'names': ['imagename', 'phase', 'selat', 'selon', 'sslat', 'sslon', 'lsratioatSE'],
        'formats': ['S64', 'f8', 'f8', 'f8', 'f8', 'f8', 'f8']
    }
    angle = np.loadtxt('rolo_angle_info.csv', dtype=dtype, delimiter=',')
    
    # zip two lists together
    rolo_angle_dict = dict(zip(angle['imagename'], angle))

    for img_name in images:
        (cub_name, trim_name, proj_name) = file_variations(img_name,
            ['.cub', '.trim.cub', '.proj.cub'])

        isis.lronac2isis(from_=img_name, to=cub_name)
        isis.spiceinit(from_=cub_name)
        isis.trim(from_=cal_name, to=trim_name, left=45, right=45)

        write_file_list('map.lis', glob='*.trim.cub')
        isis.mosrange(fromlist='map.lis', to='nac_eqr.map', precision=2,
            projection='equirectangular')

        # ROLO observation is "mm185801" for example; set at the command line
        project_rolo(rolo_observation, img_name) 
        # pass one rolo image for each LROC NAC
        photomet_rolo(img_name, rolo_angle_dict)

if __name__ == '__main__':
    main()