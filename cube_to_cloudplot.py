#!/usr/bin/env python

'''
Take a number of cubes and make them into a cloud plot.
'''
import numpy as np
import pandas as pd
from math import floor 
from pysis import isis
from glob import iglob
from pysis import CubeFile
from os.path import basename
from matplotlib import pyplot as plt


source_dir = '/home/sbraden/lunar_rois/matching_cubes/'

# Colors will be applyed to filters by filter in alphabetical ordear
colours = [
  'red',        # C
  'blue',       # D
  'green',      # E
  'burlywood',  # F
  'cyan',       # G
  'magenta',    # I
  'yellow',     # J
  'black'       # L
]


def circle_list(seq):
  """
  Takes a sequence and creates a generator which
  circles over the sequence.
  """
  i = 0
  while True:
    yield seq[i]
    i = (i + 1)%len(seq)


def clem_or_wac(img_name):
    '''
    Reads in image, reads extension,
    Python arrays are y, x instead of isis x, y => take the transpose of the
    image data array  
    '''
    image = CubeFile.open(source_dir+img_name) # pysis.cubefile.CubeFile
    if img_name[-7:-4] == 'wac':
        wac_320 = image.apply_scaling()[0].T #applies scaling and Transposes
        wac_415 = image.apply_scaling()[2].T
        wac_320_over_415 = wac_320/wac_415
        return img_name[-7:-4], wac_320_over_415

    elif img_name[-7:-4] == 'clm':
        clm_950 = image.apply_scaling()[3].T
        clm_750 = image.apply_scaling()[1].T
        clm_950_over_750 = clm_950/clm_750
        return img_name[-7:-4], clm_950_over_750
    else:
        print 'This is not a input cube that works with this script.'


def get_banddata(image_list):
    '''
    Takes in a list of images
    Performs math on selected bands
    Returns data in a pandas dataframe
    '''
    index = []
    data = []

    for img_name in image_list:
        camera, ratio_array = clem_or_wac(img_name)
        index.append(basename(img_name))
        data.append(ratio_array)

    return pd.DataFrame(data, index=index)


# lookup_dict = dict(zip(lookup.FILTER_ID, lookup.BAND_nm))


def main():

    # read in WAC images
    wac_img_list = iglob('*_wac.cub')
    print wac_img_list
    # read in clementine images
    clm_img_list = iglob('*_clm.cub')

    wac_df = get_banddata(wac_img_list)
    print wac_df
    clem_df = get_banddata(clm_img_list)
    print clem_df
    # area.mean(), area.std()


if __name__ == '__main__':
    main()
