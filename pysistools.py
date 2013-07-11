#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
pysistools
Module for often used functions while scripting using pysis.
To use: import pysistools as pyst
Eventually will become isistools.py
"""

import os, re
import numpy as np
import pandas as pd

from pysis import isis, CubeFile
from pysis.labels import parse_file_label, parse_label
from pysis.util.file_manipulation import ImageName, write_file_list


GROUP_RE = re.compile(r'(Group.*End_Group)', re.DOTALL)
content_re = re.compile(r'(Group.*End_Group)', re.DOTALL)


# Do I need this function? can't I just glob?
def read_in_list(filename):    
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

def create_mosaic(subname):
    os.system('ls '+subname+'*.proj.cub '+ subname+'*.proj.cub > proj.lis')
    isis.automos(fromlist=proj.lis, mosaic=subname+'.mos.cub')
    os.system('rm -f proj.lis') # CLEAN UP: there is a better way to run this
    pass

def get_pixel_scale(img_name):
    '''
    Input image filename
    Rturns the pixel_scale (as a string?)
    '''
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    pixel_scale = parse_label(output)['GroundPoint']['SampleResolution']
    return pixel_scale

def get_img_center(img_name):
    output = isis.campt.check_output(from_=img_name)
    output = content_re.search(output).group(1) 
    clon = parse_label(output)['GroundPoint']['PositiveEast360Longitude']
    clat = parse_label(output)['GroundPoint']['PlanetographicLatitude']
    return clat, clon

# Maybe this should go in photometry module??
def get_center_lat_lon(minlat, maxlat, minlon, maxlon):
    '''
    Input minimum and maximum latitude and longitude
    Returns center latitude and longitude
    '''
    center_lat = minlat + abs(maxlat - minlat)/2
    center_lon = minlon + abs(maxlon - minlon)/2
    return center_lat, center_lon

def makemap(region, feature, scale, proj):
    '''
    Uses a set of latitude and longitude boundaries, a projection, and
    a scale to create a mapfile.
    '''
    clon = region[2]+abs(region[3]-region[2])/2
    clat = region[0]+abs(region[1]-region[0])/2

    isis.maptemplate(map=feature+'.map', 
                     projection=proj,
                     clat=clat,
                     clon=clon,
                     rngopt='user',
                     resopt='mpp'
                     scale=scale,
                     minlat=region[0],
                     maxlat=region[1],
                     minlon=region[2],
                     maxlon=region[3]
                     )
    pass


def makemap_freescale(region, feature, proj, listfile):
    '''
    Uses a set of latitude and longitude boundaries, a projection,
    and a list of images to calculate the image scale
    A mapfile is created
    '''
    clon = region[2]+abs(region[3]-region[2])/2
    clat = region[0]+abs(region[1]-region[0])/2

    isis.maptemplate(map=feature+'.map',
                     fromlist=listfile, 
                     projection=proj,
                     clat=clat,
                     clon=clon,
                     rngopt='user',
                     resopt='calc'
                     scale=scale,
                     minlat=region[0],
                     maxlat=region[1],
                     minlon=region[2],
                     maxlon=region[3]
                     )
    pass


def process_frames(frames, color, name, model, feature): 
    '''
    Processes WAC frames (uv or vis) into regionally constrained images
    LROWACCAL calibrates pixels to DN
    '''
    subname = name+'.'+color
    mapname = feature+'.map'

    for frame in frames:
        isis.spiceinit(from_='+frame+', 
                       spksmithed='true', 
                       shape='user', 
                       model=model
                       )
        isis.lrowaccal(from_='+frame+',
                       to='+frame+'.cal,
                       RADIOMETRIC=FALSE
                       )
        isis.cam2map(from_='+frame+'.cal,
                     to='+frame+'.proj,
                     map=mapname,
                     matchmap=true
                     )

    create_mosaic(subname)


# Version from lroc_wac_proc_cal.py
def get_image_info(image):
    """
    GATHER INFORMATION ABOUT SINGLE OBSERVATION
    BASED ON VIS mosaic only
    """
    # Get label info
    label = parse_file_label(image)
    instrument = label['IsisCube']['Instrument']

    # Get campt info
    output = isis.campt.check_output(from_=image)
    gp = parse_label(GROUP_RE.search(output).group(1))['GroundPoint']

    return pd.Series({
        'start_time':              instrument['StartTime'],
        'exp_time':                instrument['ExposureDuration'],
        'fpa_temp':                instrument['MiddleTemperatureFpa'],
        'subsolar_azimuth':        gp['SubSolarAzimuth'],
        'subsolar_ground_azimuth': gp['SubSolarGroundAzimuth'],
        'solar_distance':          gp['SolarDistance']
    })

def band_means(bands):
    return bands.mean(axis=(1,2))

def band_stds(bands):
    return bands.std(axis=(1,2))

def get_img_stats(name):
    cube = CubeFile.open(name)
    return band_means(cube.data), band_stds(cube.data)

def get_spectra(name):
    uv_avgs, uv_stds = get_img_stats('{}.uv.mos.crop.cub'.format(name))
    vis_avgs, vis_stds = get_img_stats('{}.vis.mos.crop.cub'.format(name))

    bands = [321, 360, 415, 566, 604, 643, 689]

    avgs = pd.Series(
        data = np.concatenate([uv_avgs, vis_avgs]),
        index = ['avg_{}'.format(band) for band in bands]
    )

    stds = pd.Series(
        data = np.concatenate([uv_stds, vis_stds]),
        index = ['std_{}'.format(band) for band in bands]
    )

    return pd.concat([avgs, stds])

