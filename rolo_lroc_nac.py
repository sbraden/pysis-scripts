#!/usr/bin/env python
import re
from glob import iglob
from math import floor
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label
import numpy as np
import scipy
import rolotools

# Sarah Braden
# 4/3/2012
# Must use isis 3.3.1
# pysis script to project ROLO data to LROCNAC footprints 

# "rolo set" = set of multispectral rolo files
# "rolo image" = one rolo file of a single band

# ROLO images to use
rolo_set = 'mm1858'
rolo_subset = '01'
rolo_base = rolo_set + rolo_subset
# LROC NAC directory
NAC_type = 'pri'
# NAC_type = 'com'
# .map files go in nacdir
nacdir = '/home/sbraden/NACCAL/' + rolo_set + NAC_type
# ROLO directory
rolodir = '/home/sbraden/ROLO/calibrated/' + rolo_base


def photomet_rolo(img_name, rolo_angle_dict):
    """ Compute and return photometric properties of a projected rolo image
    Args: LROC NAC frame

    Returns: 
        clat, clon, emission, incidence
    """
    #rolo_band = rolodir + '/footprints/' + no_ext + '.' + rolo_base + '.band0001.cub'
    # get clat and clon for next calculation (just from the NAC map file) 
    # needs to be updated for new pysis
    mapping = parse_file_header(img_name + '.map')['Mapping']
    lat = mapping['CenterLatitude']
    lon = mapping['CenterLongitude']
    subearthlat = rolo_angle_dict[rolo_base]['selat']
    subearthlon = rolo_angle_dict[rolo_base]['selon']
    subsolarlat = rolo_angle_dict[rolo_base]['sslat']
    subsolarlon = rolo_angle_dict[rolo_base]['sslon']
    emission = rolotools.compute_emission(subearthlat, subearthlon, lat, lon)
    incidence = rolotoos.compute_incidence(subsolarlat, subsolarlon, lat, lon)
    return lat, lon, emission, incidence


def project_rolo(img_name):
    # img_name includes the path
    """" Reproject ROLO data onto LROC NAC footprints

    Args:
        img_name: The LROC NAC image that the ROLO data is reprojecting to.
    """
    rolo_images = iglob(rolodir + '/*.cub') # all bands of rolo observation
    # do I need the next two lines?
    ext_len = -len('.IMG')
    no_ext = img_name[:ext_len]
    for rolo_name in rolo_images:
        isis.map2map(from_=rolo_name, to=rolodir + '/footprints/' + no_ext + '.' + rolo_name, 
                    map=img_name+'.map', pixres='mpp', 
                    resolution=7000, interp='nearestneighbor', 
                    defaultrange='map')


# this line needed to get info from isis.campt
content_re = re.compile(r'(Group.*End_Group)', re.DOTALL)

def get_pho_angles(img_name):    
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    phase_angle = parse_label(output)['GroundPoint']['Phase']
    incidence_angle = parse_label(output)['GroundPoint']['Incidence']
    emission_angle = parse_label(output)['GroundPoint']['Emission']
    return phase_angle, incidence_angle, emission_angle


def create_mapfile(img_name):
    """ Create a mapfile in isis from a LROC NAC

    Args: img_name

    """
    (cub_name, trim_name) = file_variations(img_name,
            ['.cub', '.trim.cub'])
    isis.lronac2isis(from_=img_name, to=cub_name)
    isis.spiceinit(from_=cub_name)
    isis.trim(from_=cal_name, to=trim_name, left=45, right=45)

    write_file_list('map.lis', trim_name)
    isis.mosrange(fromlist='map.lis', to=img_name+'.map', precision=2,
        projection='equirectangular')


def multispec_rolo(img_name):
    """ Find the avg and stdev of radiance in ROLO observation projected to NAC
    footprint, for each band.

    Args: 
        rolo_observation: The rolo_observation that the images are from.
        img_name: The LROC NAC image that the ROLO data is reprojecting to.

    Returns:
        dictionary of avg and stdev radiance for each band in rolo indexed 
        by NAC image.
    """
    rolo_images = iglob(rolodir + '/footprints/*.cub') 
    for rolo_image in rolo_images:
        isis.stats(from_=rolo_image, to=rolo_image + '.stat')
        # needs to be updated for new pysis
        results = parse_file_header(rolo_image + '.stat')['Results']
        avg = results['Average']
        stdev = results['StandardDeviation']


def main():
    # remember img_name will include the path!????
    images = iglob(nacdir + '/*.IMG')
    
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

    # Create map files from NAC images 
    for img_name in images:
        # create mapfile from each NAC
        create_mapfile(img_name)
        # Project all rolo images to the mapfile for each NAC
        project_rolo(img_name) 
        # Get photomet of the rolo images projected to the NAC
        photomet_rolo(img_name, rolo_angle_dict)
        # get radiance avg and stdev for all bands in rolo subset
        multispect_rolo()

if __name__ == '__main__':
    main()
