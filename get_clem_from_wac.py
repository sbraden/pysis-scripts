#!/usr/bin/env python

from math import floor 
from pysis import isis
from pysis.labels import parse_file_label, parse_label
# TODO: use tempfile to write and auto clean isis output files

# PROBLEM: Clementine output and original WAC do not have the same
# number of pixels. Example, tsiolkovsky is 20x20 but the clementine version
# has only 18 samples.

# A check of a larger area red-imbrium-flow2 shows that there is a projection
# error. This is due to the fact that the original file was cropped from a
# larger projection centered on 0,0. The pixels will therefore not match. 

# try re-running with clat, clon = 0,0

source_dir = '/home/sbraden/lunar_rois/'
clem_dir = '/home/sbraden/Datasets/clementine/'
projection = 'equirectangular'
scale = 473.8 # units of meters per pixel LROC WAC 7-band mosaic


def read_in_list(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines


def create_maptemplate(region, projection, scale):
    '''
    Uses a set of latitude and longitude boundaries, a projection, and
    a scale to create a mapfile.
    region = (minlat, maxlat, minlon, maxlon)
    ''' 
    # center_longitude = region[2] + abs(region[3]-region[2])
    # center_latitude = region[0] + abs(region[1]-region[0])
    center_latitude = 0.0
    center_longitude = 0.0

    isis.maptemplate(
        projection_=projection,
        map  = 'temp_map.map', 
        clat = center_latitude,
        clon = center_longitude,
        minlat = region[0],
        maxlat = region[1],
        minlon = region[2],
        maxlon = region[3],
        rngopt = 'user',
        resopt = 'mpp',
        resolution = scale
                    )


def get_max_sample_line(img_name): # TODO: add to module
    '''
    Get the max sample line without reading in the image.
    '''
    output = isis.catlab.check_output(from_=img_name)
    data = parse_label(output)['IsisCube']['Core']
    max_sample = data['Dimensions']['Samples']
    max_line = data['Dimensions']['Lines']
    return max_sample, max_line


def get_lat_lon_from_x_y(xy, img_name): # TODO: add to module
    '''
    Takes xy tuple containing sample and line ints
    Returns latitude and longitude 
    '''
    output = isis.mappt.check_output(
        from_  = img_name,
        to     = 'mappt_temp.txt', 
        format = 'flat', 
        type   = 'image', 
        sample = xy[0], 
        line   = xy[1]
        )
    latitude = parse_label(output)['Results']['PlanetographicLatitude']
    longitude = parse_label(output)['Results']['PositiveEast360Longitude']
    return latitude, longitude


def main():

    image_list = read_in_list(source_dir+'temp.txt') # read in image list

    for img_name in image_list:
        # extract corner sample, line
        max_xy = get_max_sample_line(img_name)
        print max_xy #debug
        min_xy = (1,1)
        # get min max lat lon 
        min_latitude, max_longitude = get_lat_lon_from_x_y(max_xy, img_name)
        print min_latitude, max_longitude #debug
        max_latitude, min_longitude = get_lat_lon_from_x_y(min_xy, img_name)
        region = (min_latitude, max_latitude, min_longitude, max_longitude)
        # make new maptemplate
        create_maptemplate(region, projection, scale)
        # make new cub file
        isis.map2map(
            from_    = clem_dir + 'clementine_uvvis_warp_mosaic_400m.cub', 
            to       = source_dir + img_name[:-4]+'_clem.cub', 
            map      = 'temp_map.map', 
            matchmap = 'true'
            )


if __name__ == '__main__':
    main()