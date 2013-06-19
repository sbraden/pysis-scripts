#!/usr/bin/env python

import re
from glob import iglob
from math import floor
from pysis.commands import isis
from pysis.util import write_file_list, file_variations
from pysis.labels import parse_file_label, parse_label
import numpy as np


source_dir = '/home/sbraden/'
clem_dir = '/home/sbraden/Datasets/clementine/'
projection = 'equirectangular'
scale = 473.8 # units of meters per pixel

# ext_len = -len('.IMG')

def read_in_list(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines


    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    phase_angle = parse_label(output)['GroundPoint']['Phase']
    

def get_pixel_scale(img_name):
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    pixel_scale = parse_label(output)['GroundPoint']['SampleResolution']
    return minlat, maxlat, minlon, maxlon


def isis.map2map(from_=rolo_name, to=rolodir + '/footprints/' + no_ext + '.' + rolo_name, 
                    map=img_name+'.map', pixres='mpp', 
                    resolution=7000, interp='nearestneighbor', 
                    defaultrange='map')

def create_maptemplate(region, feature):
    '''
    Uses a set of latitude and longitude boundaries, a projection, and
    a scale to create a mapfile.
    region = (minlat, maxlat, minlon, maxlon)
    ''' 

    minlat = str(region[0])
    maxlat = str(region[1])
    minlon = str(region[2])
    maxlon = str(region[3])
    clon = str( region[2] + abs(region[3]-region[2]) )
    clat = str( region[0] + abs(region[1]-region[0]) )

    isis.maptemplate(
        projection_=projection,
        map  = 'temp_map.map', 
        clat = center_latitude,
        clon = center_longitude,
        minlat = minimum_latitude,
        maxlat = maximum_latitude,
        minlon = minimum_longitude,
        maxlon = maximum_longitude,
        rngopt = user,
        resopt = mpp,
        resolution = scale
                    )


def 

    isis.maptemplate(map='D_mdis_wac_eqr.map', projection='equirectangular',
        clon=0.0, clat=0.0, resopt='mpp', resolution=1000, rngopt='user', 
        minlat=-40.0, maxlat=40.0, minlon=0.0, maxlon=360.0)


def main():

    images = iglob(source_dir + '*.cub')

    # read in images
    # extract corner sample, line 
    # get min max lat lon 
    # make new maptemplate
    # make new cub file



if __name__ == '__main__':
    main()